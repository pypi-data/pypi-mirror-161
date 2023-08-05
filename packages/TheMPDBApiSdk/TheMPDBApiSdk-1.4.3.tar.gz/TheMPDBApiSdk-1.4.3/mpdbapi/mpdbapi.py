from data_classes import FileData
from data_classes import ModpackData
from data_classes import UserData
from exceptions import ApiLimitReachedError
from exceptions import FileNoFoundError
from exceptions import ModpackNotFoundError
from exceptions import NoApiKeyError
from exceptions import UserNotFoundError
from responses import FileResponse
from responses import FilesResponse
from responses import ModpackResponse
from responses import ModpacksResponse
from responses import UserResponse
from responses import UsersResponse
from utils import Utils


class MpdbApi:
    baseUrl = "https://api.thempdb.org"

    def __init__(self, apiKey):
        self.apiKey = apiKey

    def getModpack(self, id_: int) -> ModpackResponse:
        result = Utils.getData(self.baseUrl + "/modpack", {
            "apiKey": self.apiKey,
            "id": id_
        })
        if result.json()["errorMessage"] is not None:
            if result.json()["errorMessage"] == "api_limit_reached":
                raise ApiLimitReachedError()
            if result.json()["errorMessage"] == "no_api_key":
                raise NoApiKeyError()
            if result.json()["errorMessage"] == "modpack_not_found":
                raise ModpackNotFoundError()
        response = ModpackResponse()
        response.status_code = result.status_code
        response.modpack = Utils.dictToClass(result.json()["responseData"], ModpackData)
        return response

    def getModpacks(self, id_=None, name=None, description=None, authorId=None, donateLink=None,
                    fileId=None, issuesPage=None, licenseDescription=None, licenseName=None, mainImage=None,
                    sourceUrl=None, wikiPage=None) -> ModpacksResponse:
        data = {
            "apiKey": self.apiKey,
            "id": id_,
            "name": name,
            "description": description,
            "authorId": authorId,
            "donateLink": donateLink,
            "fileId": fileId,
            "issuesPage": issuesPage,
            "licenseDescription": licenseDescription,
            "licenseName": licenseName,
            "mainImage": mainImage,
            "sourceUrl": sourceUrl,
            "wikiPage": wikiPage
        }
        data = Utils.removeNullsFromDict(data)
        result = Utils.getData(self.baseUrl + "/modpacks", data)
        if result.json()["errorMessage"] is not None:
            if result.json()["errorMessage"] == "api_limit_reached":
                raise ApiLimitReachedError()
            if result.json()["errorMessage"] == "no_api_key":
                raise NoApiKeyError()
        response = ModpacksResponse()
        response.status_code = result.status_code
        modpacks = []
        for i in result.json()["responseData"]:
            modpacks.append(Utils.dictToClass(i, ModpackData))
        response.modpacks = modpacks
        return response

    def getFile(self, id_: int) -> FileResponse:
        result = Utils.getData(self.baseUrl + "/file", {
            "apiKey": self.apiKey,
            "id": id_
        })
        if result.json()["errorMessage"] is not None:
            if result.json()["errorMessage"] == "api_limit_reached":
                raise ApiLimitReachedError()
            if result.json()["errorMessage"] == "no_api_key":
                raise NoApiKeyError()
            if result.json()["errorMessage"] == "file_not_found":
                raise FileNoFoundError()
        response = FileResponse()
        response.status_code = result.status_code
        response.file = Utils.dictToClass(result.json()["responseData"], FileData)
        return response

    def getFiles(self, id_=None, modpackId=None, name=None, fileName=None, author=None,
                 changelog=None, version=None, modloader=None, javaVersion=None) -> FilesResponse:
        data = {
            "apiKey": self.apiKey,
            "id": id_,
            "modpackId": modpackId,
            "name": name,
            "fileName": fileName,
            "author": author,
            "changelog": changelog,
            "version": version,
            "modloader": modloader,
            "javaVersion": javaVersion
        }
        result = Utils.getData(self.baseUrl + "/files", data)
        if result.json()["errorMessage"] is not None:
            if result.json()["errorMessage"] == "api_limit_reached":
                raise ApiLimitReachedError()
            if result.json()["errorMessage"] == "no_api_key":
                raise NoApiKeyError()
        response = FilesResponse()
        response.status_code = result.status_code
        files = []
        for i in result.json()["responseData"]:
            files.append(Utils.dictToClass(i, FileData))
        response.files = files
        return response

    def getUser(self, id_: int) -> UserResponse:
        result = Utils.getData(self.baseUrl + "/user", {
            "apiKey": self.apiKey,
            "id": id_
        })
        if result.json()["errorMessage"] is not None:
            if result.json()["errorMessage"] == "api_limit_reached":
                raise ApiLimitReachedError()
            if result.json()["errorMessage"] == "no_api_key":
                raise NoApiKeyError()
            if result.json()["errorMessage"] == "user_not_found":
                raise UserNotFoundError()
        response = UserResponse()
        response.status_code = result.status_code
        response.user = Utils.dictToClass(result.json()["responseData"], UserData)
        return response

    def getUsers(self, id_=None, name=None) -> UsersResponse:
        data = {
            "apiKey": self.apiKey,
            "id": id_,
            "name": name
        }
        result = Utils.getData(self.baseUrl + "/users", data)
        if result.json()["errorMessage"] is not None:
            if result.json()["errorMessage"] == "api_limit_reached":
                raise ApiLimitReachedError()
            if result.json()["errorMessage"] == "no_api_key":
                raise NoApiKeyError()
        response = UsersResponse()
        response.status_code = result.status_code
        users = []
        for i in result.json()["responseData"]:
            users.append(Utils.dictToClass(i, UserData))
        response.users = users
        return response
