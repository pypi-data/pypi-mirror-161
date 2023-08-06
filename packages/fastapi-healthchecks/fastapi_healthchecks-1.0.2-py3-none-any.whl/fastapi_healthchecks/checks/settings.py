from pydantic import BaseSettings, ValidationError

from ._base import Check, CheckResult


class SettingsCheck(Check):
    _name: str
    _settings_class: type[BaseSettings]

    def __init__(self, name: str, settings_class: type[BaseSettings]):
        self._name = name
        self._settings_class = settings_class

    async def __call__(self) -> CheckResult:
        try:
            self._settings_class()
            return CheckResult(name=self._name, passed=True)
        except ValidationError as exception:
            error_messages: list[str] = []
            for error in exception.errors():
                field, *path_parts = error["loc"]
                variable_name = f"{self._settings_class.Config.env_prefix}{field}".upper()
                location: str = " -> ".join(map(str, [variable_name, *path_parts]))
                error_message: str = f"{location}: {error['msg']}"
                error_messages.append(error_message)
            return CheckResult(name=self._name, passed=False, details=", ".join(error_messages))
        except Exception as exception:
            return CheckResult(name=self._name, passed=False, details=str(exception))
