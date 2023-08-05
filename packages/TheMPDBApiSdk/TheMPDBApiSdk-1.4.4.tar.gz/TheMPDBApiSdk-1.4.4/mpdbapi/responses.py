from typing import Union, List

from .data_classes import UserData, ModpackData, FileData


class FileResponse:
    def __init__(self):
        self._status_code: Union[int, None] = None
        self._file: Union[FileData, None] = None

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, value):
        self._file = value


class FilesResponse:
    def __init__(self):
        self._status_code: Union[int, None] = None
        self._files: Union[List[FileData], None] = None

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value):
        self._files = value


class ModpackResponse:
    def __init__(self):
        self._status_code: Union[int, None] = None
        self._modpack: Union[ModpackData, None] = None

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def modpack(self):
        return self._modpack

    @modpack.setter
    def modpack(self, value):
        self._modpack = value


class ModpacksResponse:
    def __init__(self):
        self._status_code: Union[int, None] = None
        self._modpacks: Union[List[ModpackData], None] = None

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def modpacks(self):
        return self._modpacks

    @modpacks.setter
    def modpacks(self, value):
        self._modpacks = value


class UserResponse:
    def __init__(self):
        self._status_code: Union[int, None] = None
        self._user: Union[UserData, None] = None

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value


class UsersResponse:
    def __init__(self):
        self._status_code: Union[int, None] = None
        self._users: Union[List[UserData], None] = None

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def users(self):
        return self._users

    @users.setter
    def users(self, value):
        self._users = value