from fastapi import APIRouter, Request, Header, HTTPException
import json
from utils.shopify_router_utils import verify_shopify_webhook, is_duplicate_event, handle_product_change

router = APIRouter()

@router.post("/products/create")
async def product_created(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
    x_shopify_event_id: str = Header(None)
):
    print("🔔 Webhook received: products/create")
    
    if x_shopify_event_id and is_duplicate_event(x_shopify_event_id):
        print("⚠️  Duplicate event - skipping")
        return 200
    
    body = await request.body()

    if not x_shopify_hmac_sha256:
        print("❌ HMAC header missing")
        raise HTTPException(status_code=401)

    if not verify_shopify_webhook(body, x_shopify_hmac_sha256):
        print("❌ HMAC verification failed")
        raise HTTPException(status_code=401, detail="Invalid webhook")

    product = json.loads(body.decode("utf-8"))

    print("\n" + "="*60)
    print(" PRODUCT DATA (CREATE):")
    print("="*60)
    print(product)
    print("="*60 + "\n")
    # handle_product_change("created", product)

    return 200
