import requests
from config import SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET
from config import get_access_token_url, list_products_url, get_product_url

_store_url = {
    "12345": "showcasevault.myshopify.com"
}

_client_screts = {
    "12345": {
        "client_key": SHOPIFY_CLIENT_ID,
        "client_secret": SHOPIFY_CLIENT_SECRET
    }
}

def _get_store_url(client_id: str):
    return _store_url.get(client_id)

def get_access_token(client_id: str):
    store_url = _get_store_url(client_id)
    access_token_url = get_access_token_url(store_url)

    json_body = {
        "client_id": _client_screts.get(client_id).get("client_key"),
        "client_secret": _client_screts.get(client_id).get("client_secret"),
        "grant_type": "client_credentials" 
    }

    response = requests.post(access_token_url, json=json_body)
    if response.status_code == 200:
        access_information = response.json()
        access_credentials = {
            "access_token": access_information.get("access_token"),
            "expires_in": access_information.get("expires_in")
        }
    else:
        access_credentials = {
            "access_token": None,
            "expires_in": None
        }
    
    return access_credentials

def list_client_products(
    client_id: str,
    access_token: str,
    limit:int = None):

    store_url = _get_store_url(client_id)
    products_url = list_products_url(store_url)
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    params = {
        "limit": limit
    }
    
    response = requests.get(products_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_product(client_id: str,access_token: str, product_id: int):
    store_url = _get_store_url(client_id)
    products_url = get_product_url(store_url, product_id)
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    
    response = requests.get(products_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None