from severino.sdk.helpers.http_requests import Http
from severino.settings import SEVERINO_API_URL


class HubDistance:
    def __init__(self):
        self.http = Http()
        self.severino_api_url = SEVERINO_API_URL
        self.path = "/hub-distance"

    def distance(self, cep: str):
        """Get the distance between CEP and Hub

        Args:
            cep (str): E.g: 06401-000

        Returns:
            object: Http requests object
        """
        return self.http.get(url=f"{self.severino_api_url}{self.path}/{cep}/")
