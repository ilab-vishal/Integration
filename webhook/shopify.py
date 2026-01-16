from fastapi import APIRouter

from routers.shopify_router.product_create import router as create_router
from routers.shopify_router.product_update import router as update_router
from routers.shopify_router.product_delete import router as delete_router

router = APIRouter(prefix="/webhooks/shopify", tags=["Shopify"])

router.include_router(create_router)
router.include_router(update_router)
router.include_router(delete_router)
