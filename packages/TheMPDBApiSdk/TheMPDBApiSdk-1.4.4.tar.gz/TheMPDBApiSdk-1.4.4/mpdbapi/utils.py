import requests
from requests import Response


class Utils:
    @staticmethod
    def getData(url: str, data: dict) -> Response:
        r = requests.get(url, params=data)
        return r

    @staticmethod
    def removeNullsFromDict(data: dict) -> dict:
        removed = {k: v for k, v in data.items() if v is not None}
        return removed

    @staticmethod
    def dictToClass(data: dict, obj):
        cls = obj()
        for k, v in data.items():
            cls.__setattr__(k, v)
        return cls
