from datetime import datetime
from typing import Union, List


class FileData:
    def __init__(self):
        self._id: Union[int, None] = None
        self._modpack_id: Union[int, None] = None
        self._name: Union[str, None] = None
        self._filename: Union[str, None] = None
        self._author_id: Union[int, None] = None
        self._changelog: Union[str, None] = None
        self._filesize: Union[int, None] = None
        self._download_count: Union[int, None] = None
        self._uploaded_at: Union[datetime, None] = None
        self._version_id: Union[int, None] = None
        self._modloader_id: Union[int, None] = None
        self._java_version_id: Union[int, None] = None

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, value):
        self._id = value

    @property
    def modpackId(self):
        return self._modpack_id

    @modpackId.setter
    def modpackId(self, value):
        self._modpack_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def authorId(self):
        return self._author_id

    @authorId.setter
    def authorId(self, value):
        self._author_id = value

    @property
    def changelog(self):
        return self._changelog

    @changelog.setter
    def changelog(self, value):
        self._changelog = value

    @property
    def fileSize(self):
        return self._filesize

    @fileSize.setter
    def fileSize(self, value):
        self._filesize = value

    @property
    def downloadCount(self):
        return self._download_count

    @downloadCount.setter
    def downloadCount(self, value):
        self._download_count = value

    @property
    def uploadedAt(self):
        return self._uploaded_at

    @uploadedAt.setter
    def uploadedAt(self, value):
        self._uploaded_at = value

    @property
    def versionId(self):
        return self._version_id

    @versionId.setter
    def versionId(self, value):
        self._version_id = value

    @property
    def modloaderId(self):
        return self._modloader_id

    @modloaderId.setter
    def modloaderId(self, value):
        self._modloader_id = value

    @property
    def javaVersionId(self):
        return self._java_version_id

    @javaVersionId.setter
    def javaVersionId(self, value):
        self._java_version_id = value


class ModpackData:
    def __init__(self):
        self._id: Union[int, None] = None
        self._name: Union[str, None] = None
        self._main_image: Union[str, None] = None
        self._create_date: Union[datetime, None] = None
        self._description: Union[str, None] = None
        self._wiki_page: Union[str, None] = None
        self._issues_page: Union[str, None] = None
        self._license_name: Union[str, None] = None
        self._license_description: Union[str, None] = None
        self._donate_link: Union[str, None] = None
        self._source_url: Union[str, None] = None
        self._author_ids: Union[List[int], None] = None
        self._file_ids: Union[List[int], None] = None

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def mainImage(self):
        return self._main_image

    @mainImage.setter
    def mainImage(self, value):
        self._main_image = value

    @property
    def createDate(self):
        return self._create_date

    @createDate.setter
    def createDate(self, value):
        self._create_date = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def wikiPage(self):
        return self._wiki_page

    @wikiPage.setter
    def wikiPage(self, value):
        self._wiki_page = value

    @property
    def issuesPage(self):
        return self._issues_page

    @issuesPage.setter
    def issuesPage(self, value):
        self._issues_page = value

    @property
    def licenseName(self):
        return self._license_name

    @licenseName.setter
    def licenseName(self, value):
        self._license_name = value

    @property
    def licenseDescription(self):
        return self._license_description

    @licenseDescription.setter
    def licenseDescription(self, value):
        self._license_description = value

    @property
    def donateLink(self):
        return self._donate_link

    @donateLink.setter
    def donateLink(self, value):
        self._donate_link = value

    @property
    def sourceUrl(self):
        return self._source_url

    @sourceUrl.setter
    def sourceUrl(self, value):
        self._source_url = value

    @property
    def authorIds(self):
        return self._author_ids

    @authorIds.setter
    def authorIds(self, value):
        self._author_ids = value

    @property
    def fileIds(self):
        return self._file_ids

    @fileIds.setter
    def fileIds(self, value):
        self._file_ids = value


class UserData:
    def __init__(self):
        self._id: Union[int, None] = None
        self._name: Union[str, None] = None
        self._email: Union[str, None] = None
        self._password: Union[str, None] = None
        self._create_date: Union[datetime, None] = None
        self._language_id: Union[int, None] = None
        self._promo_active: Union[bool, None] = None
        self._modpack_list: Union[List[int], None] = None
        self._roles_ordered: Union[List[int], None] = None

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def createDate(self):
        return self._create_date

    @createDate.setter
    def createDate(self, value):
        self._create_date = value

    @property
    def languageId(self):
        return self._language_id

    @languageId.setter
    def languageId(self, value):
        self._language_id = value

    @property
    def promoActive(self):
        return self._promo_active

    @promoActive.setter
    def promoActive(self, value):
        self._promo_active = value

    @property
    def modpackList(self):
        return self._modpack_list

    @modpackList.setter
    def modpackList(self, value):
        self._modpack_list = value

    @property
    def rolesOrdered(self):
        return self._roles_ordered

    @rolesOrdered.setter
    def rolesOrdered(self, value):
        self._roles_ordered = value