import unittest
import httpx
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.core.dependencies.integration import get_user_info


class AuthDependencyTests(unittest.IsolatedAsyncioTestCase):
    async def validate(self, response=None, failure=None):
        def handle(request):
            self.assertEqual(request.url.path, "/api/v1/auth/me")
            self.assertEqual(request.headers["Authorization"], "Bearer test-access")
            self.assertNotIn("x-auth-role", request.headers)
            if failure:
                raise failure
            return response

        async with httpx.AsyncClient(
            base_url="http://auth", transport=httpx.MockTransport(handle)
        ) as client:
            return await get_user_info(
                HTTPAuthorizationCredentials(
                    scheme="Bearer", credentials="test-access"
                ),
                client,
            )

    async def test_current_admin_identity_comes_from_auth(self):
        user = await self.validate(
            httpx.Response(200, json={"id": 12, "role": "admin", "is_active": True})
        )
        self.assertEqual(user, {"user_id": 12, "role": "admin"})

    async def test_client_cannot_access_global_device_registry(self):
        with self.assertRaises(HTTPException) as error:
            await self.validate(
                httpx.Response(
                    200, json={"id": 12, "role": "client", "is_active": True}
                )
            )
        self.assertEqual(error.exception.status_code, 403)

    async def test_revoked_session_is_rejected(self):
        with self.assertRaises(HTTPException) as error:
            await self.validate(httpx.Response(401))
        self.assertEqual(error.exception.status_code, 401)

    async def test_auth_outage_fails_closed(self):
        with self.assertRaises(HTTPException) as error:
            await self.validate(failure=httpx.ReadTimeout("timeout"))
        self.assertEqual(error.exception.status_code, 503)

    async def test_invalid_auth_response_fails_closed(self):
        for body in (
            {"id": True, "role": "admin", "is_active": True},
            {"id": 1, "role": "admin", "is_active": False},
            [],
        ):
            with self.subTest(body=body), self.assertRaises(HTTPException) as error:
                await self.validate(httpx.Response(200, json=body))
            self.assertEqual(error.exception.status_code, 503)

    async def test_no_bearer_is_rejected(self):
        with self.assertRaises(HTTPException) as error:
            await get_user_info(None, None)
        self.assertEqual(error.exception.status_code, 401)
