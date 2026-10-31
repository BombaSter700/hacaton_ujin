from fastapi import Depends
from app.core.dependencies.integration import get_user_info

def require_object_access(object_id: str, user: dict = Depends(get_user_info)):
    # TODO: Реализовать проверку через БД или внешний сервис
    # Пока заглушка: админ имеет доступ ко всему
    if user.get("role") == "admin":
        return user
    # В реальности здесь запрос к БД: есть ли у user_id доступ к object_id
    raise HTTPException(status_code=403, detail="No access to this object")