import uuid

from ._base import Check, CheckResult

try:
    from aiorgwadmin import RGWAdmin
    from aiorgwadmin.exceptions import NoSuchBucket
except ImportError as exc:
    raise ImportError("Using this module requires the aiorgwadmin library.") from exc


class CephCheck(Check):
    _host: str
    _access_key: str
    _secret_key: str
    _secure: bool
    _verify_ssl: bool
    _timeout: int
    _name: str

    def __init__(
        self,
        host: str,
        access_key: str,
        secret_key: str,
        secure: bool = True,
        verify_ssl: bool = True,
        timeout: int = 60,
        name: str = "Ceph",
    ):
        self._host = host
        self._access_key = access_key
        self._secret_key = secret_key
        self._secure = secure
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._name = name

    async def __call__(self) -> CheckResult:
        rgw = RGWAdmin(  # type: ignore[no-untyped-call]
            server=self._host,
            access_key=self._access_key,
            secret_key=self._secret_key,
            verify=self._verify_ssl,
            secure=self._secure,
            timeout=self._timeout,
        )
        try:
            await rgw.get_bucket(bucket=str(uuid.uuid4()))  # type: ignore[no-untyped-call]
        except NoSuchBucket:
            pass
        except Exception as exception:
            return CheckResult(name=self._name, passed=False, details=str(exception))

        return CheckResult(name=self._name, passed=True)
