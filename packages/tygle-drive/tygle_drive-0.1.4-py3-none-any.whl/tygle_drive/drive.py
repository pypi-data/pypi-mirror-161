from aiogoogle import GoogleAPI
from tygle.base import API
from tygle.client import Client

from .rest import Files


class Drive(API):
    api_name = "drive"
    api_version = "v3"

    def __init__(self, client: Client, api: GoogleAPI) -> None:
        super().__init__(client, api)
        self.files = Files(client, self.api)
