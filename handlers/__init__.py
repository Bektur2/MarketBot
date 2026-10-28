from aiogram import Router

from handlers.admin import router as admin_router
from handlers.fallback import router as fallback_router
from handlers.info import router as info_router
from handlers.profile import router as profile_router
from handlers.showcase import router as showcase_router
from handlers.start import router as start_router


def get_main_router() -> Router:
    # объединяем обработчики в один главный роутер
    router = Router()
    router.include_routers(
        admin_router,
        start_router,
        showcase_router,
        profile_router,
        info_router,
        fallback_router,
    )
    return router

