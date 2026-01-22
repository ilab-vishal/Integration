import os
from dotenv import load_dotenv
from functools import lru_cache
from api.connections.database_connection import get_sync_db_session

from api.models import Integration
from api.utils.encryption import decrypt_value

load_dotenv()

SHOPIFY_API_VERSION = "2026-01"

@lru_cache(maxsize=128)
def get_client_integration(client_id: str):
    with get_sync_db_session() as db:
        integration = db.query(Integration).filter(
            Integration.client_id == client_id,
            Integration.provider == "shopify"
        ).first()

        if not integration:
            return None

        return {
            "store_url": integration.store_url,
            "integration_key": decrypt_value(integration.integration_key),
            "integration_secret": decrypt_value(integration.integration_secret),
            "webhook_secret": decrypt_value(integration.webhook_secret),
        }



def get_store_url(client_id: str):
    client = get_client_integration(client_id)
    if not client:
        return {
            "store_url": None,
        }
    return client.get("store_url")


def get_client_credentials(client_id: str):
    client = get_client_integration(client_id)
    if not client:
        return {
            "client_id": None,
            "client_secret": None,
        }
    return {
        "client_id": client.get("integration_key"),
        "client_secret": client.get("integration_secret"),
    }

def get_webhook_secret(client_id: str):
    client = get_client_integration(client_id)
    if not client:
        return {
            "webhook_secret": None,
        }
    return client.get("webhook_secret")

def get_access_token_url(store_url: str):
    return f"https://{store_url}/admin/oauth/access_token"


def list_products_url(store_url: str):
    return f"https://{store_url}/admin/api/{SHOPIFY_API_VERSION}/products.json"


def get_product_url(store_url: str, product_id: int):
    return f"https://{store_url}/admin/api/{SHOPIFY_API_VERSION}/products/{product_id}.json"

def get_connection_test_url(store_url: str):
    return f"https://{store_url}/admin/api/{SHOPIFY_API_VERSION}/products/count.json"
