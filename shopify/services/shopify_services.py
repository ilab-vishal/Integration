import requests
from shopify.config import (
    get_access_token_url,
    get_client_credentials,
    get_product_url,
    get_store_url,
    list_products_url,
    get_connection_test_url
)

def _get_store_url(client_id: str):
    return get_store_url(client_id)

def get_access_token(client_id: str):
    store_url = _get_store_url(client_id)
    if not store_url:
        raise ValueError(f"Unknown Shopify client_id: {client_id}")
    access_token_url = get_access_token_url(store_url)
    credentials = get_client_credentials(client_id) or {}
    
    if not credentials.get("client_id") or not credentials.get("client_secret"):
        raise ValueError(f"Missing Shopify credentials for client_id: {client_id}")

    json_body = {
        "client_id": credentials.get("client_id"),
        "client_secret": credentials.get("client_secret"),
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
    limit:int = None
    ):

    store_url = _get_store_url(client_id)
    if not store_url:
        raise ValueError(f"Unknown Shopify client_id: {client_id}")
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

def get_client_product(client_id: str,access_token: str, product_id: int):
    store_url = _get_store_url(client_id)
    if not store_url:
        raise ValueError(f"Unknown Shopify client_id: {client_id}")
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

def get_connection_test_results(client_id: str, access_token: str):
    store_url = _get_store_url(client_id)
    if not store_url:
        raise ValueError(f"Unknown Shopify client_id: {client_id}")
    connection_test_url = get_connection_test_url(store_url)
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    response = requests.get(connection_test_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
