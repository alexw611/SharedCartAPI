from API.routers.auth import router as auth_router
from API.routers.users import router as users_router
from API.routers.groups import router as groups_router
from API.routers.shopping_lists import router as shopping_lists_router

__all__ = ["auth_router", "users_router", "groups_router", "shopping_lists_router"]
