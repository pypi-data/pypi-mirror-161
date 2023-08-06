import base64
import uuid

from severino.sdk.helpers.http_requests import Http
from severino.settings import SEVERINO_API_URL


class MailCarrier:
    def __init__(self):
        self.http = Http()
        self.severino_api_url = SEVERINO_API_URL
        self.path = "/mail-carrier"

    def last_email_sent_to(self, email: str):
        return self.http.get(
            url=f"{self.severino_api_url}{self.path}/last-email-sent-to/{email}/"
        )

    def send(
        self,
        to_email: str,
        from_connection: uuid,
        template_name: str,
        subject: str = "",
        context_vars: dict = {},
        files: list = [],
    ):

        data = {
            "subject": subject,
            "to_email": to_email,
            "from_connection": from_connection,
            "template_name": template_name,
            "context_vars": context_vars,
        }

        if files:
            data["base64_files"] = []

            for file in files:
                data["base64_files"].append(
                    {
                        "name": file["name"],
                        "content": self.__get_file(file=file["file"]),
                    }
                )

        return self.http.post(
            url=f"{self.severino_api_url}{self.path}/send/", data=data
        )

    def __get_file(self, file):
        if isinstance(file, str):
            file = open(file, "rb")
            file = file.read()

        return base64.b64encode(file).decode("utf8")
