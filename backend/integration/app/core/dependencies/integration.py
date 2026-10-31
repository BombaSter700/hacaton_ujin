from typing import Any, Dict, List, Optional
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from app.core.config import settings
from app.core.exceptions.integration_exceptions import IntegrationAuthException

security = HTTPBearer(auto_error=False)


async def get_user_from_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:

    if not credentials:
        raise IntegrationAuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (no token provided)",
        )

    try:
        # Делаем запрос к сервису авторизации
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                f"{settings.auth_service_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            if response.status_code == 401:
                raise IntegrationAuthException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid or expired token"
                )
            
            if response.status_code != 200:
                raise IntegrationAuthException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Auth service is unavailable or returned an error"
                )
            
            data = response.json()
            
            return {
                "user_id": data.get("id"), 
                "role": data.get("role", "client"),
                "is_active": data.get("is_active", False)
            }
            
    except httpx.RequestError:
        raise IntegrationAuthException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service connection error"
        )



get_user_info = get_user_from_auth


def require_role(required_role: str):
    def checker(user_info: Dict[str, Any] = Depends(get_user_info)) -> Dict[str, Any]:
        if user_info.get("role") != required_role:
            raise IntegrationAuthException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
            )
        return user_info
    return checker


def require_any_role(required_roles: List[str]):
    def checker(user_info: Dict[str, Any] = Depends(get_user_info)) -> Dict[str, Any]:
        if user_info.get("role") not in required_roles:
            raise IntegrationAuthException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}",
            )
        return user_info
    return checker


def require_admin(user_info: Dict[str, Any] = Depends(get_user_info)) -> Dict[str, Any]:
    return require_role("admin")(user_info)


def require_client_or_admin(
    user_info: Dict[str, Any] = Depends(get_user_info),
) -> Dict[str, Any]:
    return require_any_role(["client", "admin"])(user_info)