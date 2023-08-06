from severino.sdk.helpers.http_requests import Http


class PaginationControls:
    LAST_REQUEST = None

    def __init__(self, request) -> None:
        self.LAST_REQUEST = request

    def __control(self, action):
        data = None
        response = None

        if self.LAST_REQUEST:
            data = self.LAST_REQUEST.json()

        if data:
            if data["links"][action]:
                response = Http()._http_request(
                    method="GET",
                    url=data["links"][action],
                    headers=dict(self.LAST_REQUEST.request.headers),
                )
                self.LAST_REQUEST = response
        return self

    @property
    def page_size(self):
        data = self.LAST_REQUEST.json()
        return data["page_size"]

    @property
    def total_pages(self):
        data = self.LAST_REQUEST.json()
        return data["total_pages"]

    @property
    def current_page(self):
        data = self.LAST_REQUEST.json()
        return data["page"]

    @property
    def count(self):
        data = self.LAST_REQUEST.json()
        return data["count"]

    @property
    def is_first_page(self):
        data = self.LAST_REQUEST.json()
        return data["page"] == 1

    @property
    def is_last_page(self):
        data = self.LAST_REQUEST.json()
        return data["page"] == data["total_pages"]

    @property
    def raw_data(self):
        return self.LAST_REQUEST.json()

    @property
    def data(self):
        return self.LAST_REQUEST.json()["results"]

    def request(self):
        return self.LAST_REQUEST

    def next(self):
        return self.__control("next")

    def previous(self):
        return self.__control("previous")
