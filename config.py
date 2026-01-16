SHOPIFY_CLIENT_ID="ad94264990687b8f087569fb03612974"
SHOPIFY_CLIENT_SECRET="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"
SHOPIFY_WEBHOOK_SECRET="688c024dbcf5f42f5424fc1b565488649a92ca433d5c9fccb61446b219f88a18"

API_VERSION = "2026-01"

def get_access_token_url(store_url: str):
    return f"https://{store_url}/admin/oauth/access_token"

def list_products_url(store_url: str):
    return f"https://{store_url}/admin/api/{API_VERSION}/products.json"

def get_product_url(store_url: str, product_id: int):
    return f"https://{store_url}/admin/api/{API_VERSION}/products/{product_id}.json"