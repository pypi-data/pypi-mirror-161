import json
import os
from datetime import datetime
from time import sleep
from typing import Dict, List, Optional
from urllib.parse import unquote, urlencode

import dateutil.parser
import requests
import sqlalchemy as sa
import websockets
from alert_msgs import FontColors, FontSize, Text, send_alert
from ready_logger import get_logger
from sqlalchemy.engine import Engine

td_app_table = sa.Table(
    "app",
    sa.MetaData(schema="td_ameritrade"),
    sa.Column("redirect_url", sa.String),
    sa.Column("consumer_key", sa.String),
    sa.Column("code", sa.String),
    sa.Column("access_token", sa.String),
    sa.Column("refresh_token", sa.String),
)


def create_engine() -> Engine:
    return sa.create_engine(os.environ["POSTGRES_URL"])


def save_app_code(url: str, engine: Engine) -> str:
    code = unquote(url.split("?code=")[-1])
    with engine.begin() as conn:
        conn.execute(sa.update(td_app_table).values({"code": code}))
    return code


class TDAuth:
    """
    Authentication manager for TD Ameritrade APIs.
    Automatically get new access and refresh tokens upon expiring.
    Call standard APIs: https://developer.tdameritrade.com/apis
    Call streaming APIs: https://developer.tdameritrade.com/content/streaming-data
    """

    logger = get_logger("TDAuth")

    def __init__(self, no_stdin: Optional[bool] = None):
        self.no_stdin = os.getenv("NO_STDIN") if no_stdin is None else no_stdin
        self.engine = create_engine()

        with self.engine.begin() as conn:
            self._cfg = dict(conn.execute(sa.select(td_app_table)).fetchone())
        self.logger.info(f"Loaded app config: {', '.join(self._cfg.keys())}")

        self.client_id = f"{self._cfg['consumer_key']}@AMER.OAUTHAP"
        self.auth_code_url = f"https://auth.tdameritrade.com/auth?response_type=code&redirect_uri={self._cfg['redirect_url']}&client_id={self.client_id}"

        # Check for expired credentials and renew if necessary.
        self._user_principles = self._get_user_principles()
        # should only be one account.
        self._account = self._user_principles["accounts"][0]
        self._stream_info = self._user_principles["streamerInfo"]
        self._request_id = 0

    @property
    def request_id(self):
        current_id = self._request_id
        self._request_id += 1
        return current_id

    @property
    def auth_header(self):
        "Authorization header must be passed in header to all API requests."
        return {"Authorization": f"Bearer {self._cfg.get('access_token')}"}

    async def get_stream_websocket(self):
        # TODO -- not async.
        endpoint = f"wss://{self._stream_info['streamerSocketUrl']}/ws"
        connection = await websockets.connect(endpoint, max_size=None)
        if connection.closed:
            raise ConnectionError(
                f"Could not connect to websocket endpoint: {endpoint}."
            )
        # login.
        date = dateutil.parser.parse(self._stream_info["tokenTimestamp"], ignoretz=True)
        # timestamp in ms.
        timestamp = int((date - datetime.utcfromtimestamp(0)).total_seconds()) * 1000
        credential = {
            "userid": self._account["accountId"],
            "token": self._stream_info["token"],
            "company": self._account["company"],
            "segment": self._account["segment"],
            "cddomain": self._account["accountCdDomainId"],
            "usergroup": self._stream_info["userGroup"],
            "accesslevel": self._stream_info["accessLevel"],
            "appid": self._stream_info["appId"],
            "acl": self._stream_info["acl"],
            "timestamp": timestamp,
            "authorized": "Y",
        }
        request = self.authenticate_stream_requests(
            {
                "service": "ADMIN",
                "command": "LOGIN",
                "parameters": {
                    "credential": urlencode(credential),
                    "token": self._stream_info["token"],
                    "version": "1.0",
                },
            }
        )
        await connection.send(request)
        while True:
            message = await connection.recv()
            response = json.loads(message)["response"][0]
            if response["content"]["code"] == 3:
                raise ValueError(f"STREAM LOGIN ERROR: {response[0]['content']['msg']}")
            if (
                response.get("service") == "ADMIN"
                and response.get("command") == "LOGIN"
            ):
                return connection

    def authenticate_stream_requests(self, reqs: List[Dict[str, str]]):
        if not isinstance(reqs, List):
            reqs = [reqs]
        required_fields = ("service", "command", "parameters")
        for req in reqs:
            if not all(field in req for field in required_fields):
                raise ValueError(
                    f"Stream request ({req}) must contain all required fields: {','.join(required_fields)}"
                )
            req["requestid"] = str(self.request_id)
            req["account"] = self._account["accountId"]
            req["source"] = self._stream_info["appId"]
        return json.dumps({"requests": reqs})

    def _get_user_principles(self):
        resp = requests.get(
            url="https://api.tdameritrade.com/v1/userprincipals",
            params={"fields": "streamerSubscriptionKeys,streamerConnectionInfo"},
            headers=self.auth_header,
        )
        if resp.status_code == 200:
            self.logger.info(f"Successfully got userprincipals")
            return resp.json()
        self.logger.info(
            f"Could not get User Principles. Getting access token from refresh token."
        )
        self._set_access_token_from_refresh_token()
        # try again using new token(s)
        return self._get_user_principles()

    def _set_access_token_from_refresh_token(self):
        if "refresh_token" not in self._cfg:
            self.logger.info(
                "`refresh_token` not found in configuration. Getting tokens from `code`."
            )
            self._set_access_and_refresh_tokens()
        resp = requests.post(
            "https://api.tdameritrade.com/v1/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._cfg["refresh_token"],
                "client_id": self.client_id,
            },
        )
        if resp.status_code == 200:
            self.logger.info(f"Successfully got new access token from refresh token.")
            data = resp.json()
            self._update_cfg(access_token=data["access_token"])
        else:
            self.logger.info(
                "Could not get access token from refresh token. Getting access and refresh tokens form CODE."
            )
            self._set_access_and_refresh_tokens()

    def _set_access_and_refresh_tokens(self):
        resp = requests.post(
            r"https://api.tdameritrade.com/v1/oauth2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "access_type": "offline",
                "code": self._cfg.get("code", ""),
                "redirect_uri": f'{self._cfg["redirect_url"]}',
                "client_id": self.client_id,
            },
        )
        if resp.status_code == 200:
            self.logger.info(f"Successfully got new access token from Code.")
            data = resp.json()
            self._update_cfg(
                access_token=data["access_token"], refresh_token=data["refresh_token"]
            )
        else:
            msg = f"""
            Could not get new access token from existing code.
            You must manually get a new code from {self.auth_code_url}
            Sign in, wait to be redirected to a new page"""
            if self.no_stdin:
                # send alert to add new code to the database.
                send_alert(
                    components=[
                        Text(
                            f"{msg}, then run `save_td_app_code {{redirect URL}}`",
                            size=FontSize.LARGE,
                            color=FontColors.IMPORTANT,
                        )
                    ],
                    subject="Set New TD App Code",
                )
                with self.engine.begin() as conn:
                    while (
                        code := conn.execute(sa.select(td_app_table.c.code)).scalar()
                    ) == self._cfg["code"]:
                        self.logger.info("Waiting for code to be save to database.")
                        sleep(2)
                    self._cfg["code"] = code
            else:
                url = input(
                    f"{msg}, then paste the URL of the redirect page here: "
                ).strip()
                self._cfg["code"] = save_app_code(url, self.engine)

            self._set_access_and_refresh_tokens()

    def _update_cfg(self, **kwargs) -> None:
        self.logger.info(f"Saving updated app config {', '.join(kwargs.keys())}")
        self._cfg.update(kwargs)
        with self.engine.begin() as conn:
            conn.execute(sa.update(td_app_table).values(kwargs))
