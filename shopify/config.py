import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False

load_dotenv()

SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-01")
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET", "")

_DEFAULT_STORE_URL = os.getenv("SHOPIFY_STORE_URL", "showcasevault.myshopify.com")

_CLIENTS = {
    "12345" : {
        "store_url": _DEFAULT_STORE_URL,
        "client_id": os.getenv("SHOPIFY_CLIENT_ID", ""),
        "client_secret": os.getenv("SHOPIFY_CLIENT_SECRET", ""),
    }
}


def get_store_url(client_id: str):
    client = _CLIENTS.get(client_id)
    if not client:
        return None
    return client.get("store_url")


def get_client_credentials(client_id: str):
    client = _CLIENTS.get(client_id)
    if not client:
        return None
    return {
        "client_id": client.get("client_id"),
        "client_secret": client.get("client_secret"),
    }


def get_access_token_url(store_url: str):
    return f"https://{store_url}/admin/oauth/access_token"


def list_products_url(store_url: str):
    return f"https://{store_url}/admin/api/{SHOPIFY_API_VERSION}/products.json"


def get_product_url(store_url: str, product_id: int):
    return f"https://{store_url}/admin/api/{SHOPIFY_API_VERSION}/products/{product_id}.json"
