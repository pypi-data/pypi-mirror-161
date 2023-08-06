import asyncio
from collections.abc import Iterable
from operator import attrgetter
from typing import NamedTuple

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from fastapi_healthchecks.api.models import HealthcheckReport
from fastapi_healthchecks.checks import Check, CheckResult


class Probe(NamedTuple):
    name: str
    checks: Iterable[Check]


class HealthcheckRouter(APIRouter):
    def __init__(self, *probes: Probe):
        super().__init__()
        for probe in probes:
            self._add_probe_route(probe)

    def _add_probe_route(self, probe: Probe) -> None:
        async def handle_request():
            return await self._handle_request(probe)

        self.add_api_route(
            path=f"/{probe.name}",
            endpoint=handle_request,
            response_model=HealthcheckReport,
        )

    async def _handle_request(self, probe: Probe) -> JSONResponse:
        tasks = [check() for check in probe.checks]
        results: list[CheckResult] = await asyncio.gather(*tasks)
        is_healthy = all(map(attrgetter("passed"), results))
        report = HealthcheckReport(healthy=is_healthy, checks=results)
        return JSONResponse(
            content=jsonable_encoder(report),
            status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
