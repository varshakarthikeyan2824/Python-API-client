import random
import time
from collections.abc import Iterator

import httpx

from apiclient.models import Parcel


class APIClient:
    def __init__(self, base_url: str):
        self.client = httpx.Client(
            base_url=base_url,
            timeout=5.0,
        )

    def get_metadata(self) -> dict:
        response = self._get_with_retry("/v1/meta")
        response.raise_for_status()
        return response.json()

    def get_parcels(self, offset: int = 0, limit: int = 5) -> list[Parcel]:
        response = self._get_with_retry(
            "/v1/parcels",
            params={"offset": offset, "limit": limit},
        )
        response.raise_for_status()

        data = response.json()
        return [Parcel.model_validate(item) for item in data["items"]]

    def _get_with_retry(self, path: str, params: dict | None = None) -> httpx.Response:
        max_attempts = 3

        for attempt in range(max_attempts):
            response = self.client.get(path, params=params)

            if (
                response.status_code == 429 or response.status_code >= 500
            ) and attempt < max_attempts - 1:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    delay = float(retry_after)
                else:
                    delay = (2**attempt) + random.uniform(0, 0.5)

                time.sleep(delay)
                continue

            response.raise_for_status()
            return response

        raise RuntimeError("Request failed after retries")

    def iter_parcels(self, page_size: int = 50) -> Iterator[Parcel]:
        offset = 0
        seen_ids = set()

        while True:
            parcels = self.get_parcels(offset=offset, limit=page_size)

            if not parcels:
                break

            for parcel in parcels:
                if parcel.id not in seen_ids:
                    seen_ids.add(parcel.id)
                    yield parcel

            if len(parcels) < page_size:
                break

            offset += len(parcels)

    def close(self):
        self.client.close()
