import httpx

from apiclient.client import APIClient


def test_get_parcels():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": 1,
                        "name": "Birch 0001",
                        "status": "active",
                        "category": "charlie",
                        "created": "2025-09-08",
                    }
                ],
                "offset": 0,
                "limit": 1,
                "total": 1,
            },
        )

    transport = httpx.MockTransport(handler)
    client = APIClient("http://test-server")
    client.client.close()
    client.client = httpx.Client(
        base_url="http://test-server",
        transport=transport,
        timeout=5.0,
    )

    try:
        parcels = client.get_parcels(limit=1)

        assert len(parcels) == 1
        assert parcels[0].id == 1
        assert parcels[0].name == "Birch 0001"
    finally:
        client.close()


def test_retries_server_error():
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(500)

        return httpx.Response(
            200,
            json={
                "variant": 3,
                "domain": "Parcels",
                "entity": "parcels",
                "pagination": "offset",
                "total": 237,
            },
        )

    transport = httpx.MockTransport(handler)
    client = APIClient("http://test-server")
    client.client.close()
    client.client = httpx.Client(
        base_url="http://test-server",
        transport=transport,
        timeout=5.0,
    )

    # Avoid waiting during this test.
    import unittest.mock

    try:
        with unittest.mock.patch("apiclient.client.time.sleep"):
            metadata = client.get_metadata()

        assert metadata["total"] == 237
        assert attempts == 2
    finally:
        client.close()


def test_timeout_is_enforced():
    def handler(request):
        raise httpx.ReadTimeout(
            "Request timed out",
            request=request,
        )

    transport = httpx.MockTransport(handler)
    client = APIClient("http://test-server")
    client.client.close()
    client.client = httpx.Client(
        base_url="http://test-server",
        transport=transport,
        timeout=5.0,
    )

    try:
        import pytest

        with pytest.raises(httpx.ReadTimeout):
            client.get_metadata()
    finally:
        client.close()


def test_bad_record_is_rejected():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": "not-an-integer",
                        "name": "Birch 0001",
                        "status": "active",
                        "category": "charlie",
                        "created": "2025-09-08",
                    }
                ],
                "offset": 0,
                "limit": 1,
                "total": 1,
            },
        )

    transport = httpx.MockTransport(handler)
    client = APIClient("http://test-server")
    client.client.close()
    client.client = httpx.Client(
        base_url="http://test-server",
        transport=transport,
        timeout=5.0,
    )

    try:
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            client.get_parcels(limit=1)
    finally:
        client.close()
