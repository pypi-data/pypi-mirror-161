class ApiLimitReachedError(Exception):
    def __init__(self) -> None:
        super().__init__("Monthly Api Limit Reached!")


class FileNoFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("This File Is Not Found In Database!")


class ModpackNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("This Modpack Is Not Found In Database!")


class NoApiKeyError(Exception):
    def __init__(self) -> None:
        super().__init__("This Api Key Is Not Valid!")


class UserNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("This User Is Not Found In Database!")
