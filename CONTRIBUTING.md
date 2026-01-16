# Contributing to E-Commerce Integration Platform

Thank you for your interest in contributing! This document provides comprehensive guidelines for adding new e-commerce platform integrations like WooCommerce, Magento, BigCommerce, and others.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Step-by-Step Integration Guide](#step-by-step-integration-guide)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Submission Process](#submission-process)
- [Platform-Specific Notes](#platform-specific-notes)

## Getting Started

Before you begin, please:

1. **Check existing integrations** - Review the Shopify integration as a reference implementation
2. **Read the architecture** - Understand the base classes and patterns used
3. **Set up your environment** - Follow the development setup instructions below

## Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd Integration

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest black flake8
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# App-level configuration
APP_HOST=127.0.0.1
APP_PORT=8050

# Shopify configuration (example)
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_CLIENT_ID=your_client_id
SHOPIFY_CLIENT_SECRET=your_client_secret
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret
SHOPIFY_API_VERSION=2026-01
```

## Project Architecture

### Directory Structure

```
Integration/
├── base/                          # Core abstract classes
│   ├── base.py                   # CatalogBase - Abstract base class
│   └── integrations.py           # Enum of supported integrations
├── <platform_name>/              # Integration module (e.g., shopify, woocommerce)
│   ├── config.py                 # Platform-specific configuration
│   ├── connection_adapter/       # API client implementation
│   │   └── adapter.py           # Engine class extending CatalogBase
│   ├── services/                 # Business logic and API calls
│   │   └── <platform>_services.py
│   ├── routers/                  # Webhook route handlers
│   │   ├── product_create.py
│   │   ├── product_update.py
│   │   └── product_delete.py
│   ├── utils/                    # Platform-specific utilities
│   │   └── <platform>_router_utils.py
│   └── webhook/                  # Webhook router configuration
│       └── <platform>.py
├── utils/                         # Shared utilities
│   └── response_formatter.py
├── config.py                      # App-level configuration
├── app.py                         # FastAPI webhook server
├── main.py                        # Example usage
└── __init__.py                    # Factory pattern for engine creation
```

### Core Components

Every integration consists of **five main components**:

1. **Configuration Module** (`config.py`) - Platform-specific settings and credentials
2. **Connection Adapter** (`connection_adapter/adapter.py`) - Engine class that extends `CatalogBase`
3. **Services Layer** (`services/<platform>_services.py`) - API authentication and data fetching logic
4. **Webhook Handlers** (`routers/`) - Processes incoming webhooks with HMAC verification
5. **Router Configuration** (`webhook/<platform>.py`) - Aggregates webhook endpoints

## Step-by-Step Integration Guide

Follow these steps to add a new e-commerce platform integration (WooCommerce, Magento, BigCommerce, etc.).

### Phase 1: Setup and Planning

#### 1.1 Research the Platform

Before coding, research:
- **API authentication method** (OAuth 2.0, API keys, tokens, Basic Auth)
- **API endpoints** for product operations (list, get, create, update, delete)
- **Webhook signature verification** method (HMAC-SHA256, digital signatures, etc.)
- **Rate limits** and pagination strategies
- **API version** to use (stable/recommended version)
- **Required headers** and authentication patterns

#### 1.2 Update Integration Enum

Add your platform to the integrations registry:

```python
# base/integrations.py
from enum import Enum

class Integrations(Enum):
    SHOPIFY: str = "shopify"
    WOOCOMMERCE: str = "woocommerce"  # Add your platform
    MAGENTO: str = "magento"          # Add your platform
```

#### 1.3 Create Directory Structure

```bash
# Create the integration package structure
mkdir -p <platform_name>/connection_adapter
mkdir -p <platform_name>/services
mkdir -p <platform_name>/routers
mkdir -p <platform_name>/utils
mkdir -p <platform_name>/webhook
touch <platform_name>/__init__.py
```

Example for WooCommerce:
```bash
mkdir -p woocommerce/connection_adapter
mkdir -p woocommerce/services
mkdir -p woocommerce/routers
mkdir -p woocommerce/utils
mkdir -p woocommerce/webhook
touch woocommerce/__init__.py
```

---

### Phase 2: Create Platform Configuration

#### 2.1 Create Configuration Module

File: `<platform_name>/config.py`

```python
import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False

load_dotenv()

# Platform-specific constants
WOOCOMMERCE_API_VERSION = os.getenv("WOOCOMMERCE_API_VERSION", "wc/v3")
WOOCOMMERCE_WEBHOOK_SECRET = os.getenv("WOOCOMMERCE_WEBHOOK_SECRET", "")

# Default store configuration
_DEFAULT_STORE_URL = os.getenv("WOOCOMMERCE_STORE_URL", "yourstore.com")

# Client credentials mapping (client_id -> credentials)
_CLIENTS = {
    "12345": {
        "store_url": _DEFAULT_STORE_URL,
        "consumer_key": os.getenv("WOOCOMMERCE_CONSUMER_KEY", ""),
        "consumer_secret": os.getenv("WOOCOMMERCE_CONSUMER_SECRET", ""),
    }
}


def get_store_url(client_id: str):
    """Get store URL for a given client ID."""
    client = _CLIENTS.get(client_id)
    if not client:
        return None
    return client.get("store_url")


def get_client_credentials(client_id: str):
    """Get authentication credentials for a given client ID."""
    client = _CLIENTS.get(client_id)
    if not client:
        return None
    return {
        "consumer_key": client.get("consumer_key"),
        "consumer_secret": client.get("consumer_secret"),
    }


def get_products_url(store_url: str) -> str:
    """Generate products list URL."""
    return f"https://{store_url}/wp-json/{WOOCOMMERCE_API_VERSION}/products"


def get_product_url(store_url: str, product_id: int) -> str:
    """Generate single product URL."""
    return f"https://{store_url}/wp-json/{WOOCOMMERCE_API_VERSION}/products/{product_id}"
```

**Key Points:**
- Use environment variables for sensitive data
- Make `python-dotenv` optional (graceful fallback)
- Store client configurations in `_CLIENTS` dictionary
- Provide helper functions for URL generation

---

### Phase 3: Implement Services Layer

#### 3.1 Create Services Module

File: `<platform_name>/services/<platform_name>_services.py`

This module handles all API interactions and business logic.

```python
import requests
from <platform_name>.config import (
    get_store_url,
    get_client_credentials,
    get_products_url,
    get_product_url,
)


def _get_store_url(client_id: str):
    """Internal helper to get store URL."""
    return get_store_url(client_id)


def get_access_token(client_id: str) -> dict:
    """
    Obtain access token for API authentication.
    
    Args:
        client_id: Client identifier
        
    Returns:
        dict: {"access_token": "...", "expires_in": 3600}
        
    Raises:
        ValueError: If client_id is unknown or credentials are missing
    """
    store_url = _get_store_url(client_id)
    if not store_url:
        raise ValueError(f"Unknown client_id: {client_id}")
    
    credentials = get_client_credentials(client_id) or {}
    
    if not credentials.get("consumer_key") or not credentials.get("consumer_secret"):
        raise ValueError(f"Missing credentials for client_id: {client_id}")
    
    # Implement platform-specific authentication
    # For WooCommerce, you might use Basic Auth or OAuth
    # For Shopify, you use client credentials grant
    # Example for OAuth 2.0:
    
    auth_url = f"https://{store_url}/oauth/token"
    json_body = {
        "grant_type": "client_credentials",
        "client_id": credentials.get("consumer_key"),
        "client_secret": credentials.get("consumer_secret"),
    }
    
    response = requests.post(auth_url, json=json_body)
    
    if response.status_code == 200:
        access_information = response.json()
        return {
            "access_token": access_information.get("access_token"),
            "expires_in": access_information.get("expires_in"),
        }
    else:
        return {
            "access_token": None,
            "expires_in": None,
        }


def list_client_products(
    client_id: str,
    access_token: str,
    limit: int = None
) -> dict:
    """
    Fetch products from the platform API.
    
    Args:
        client_id: Client identifier
        access_token: Authentication token
        limit: Maximum number of products to return
        
    Returns:
        dict: API response with products
        
    Raises:
        ValueError: If client_id is unknown
    """
    store_url = _get_store_url(client_id)
    if not store_url:
        raise ValueError(f"Unknown client_id: {client_id}")
    
    products_url = get_products_url(store_url)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    params = {}
    if limit:
        params["per_page"] = limit  # Adjust based on platform
    
    response = requests.get(products_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_client_product(
    client_id: str,
    access_token: str,
    product_id: int
) -> dict:
    """
    Fetch a single product by ID.
    
    Args:
        client_id: Client identifier
        access_token: Authentication token
        product_id: Product ID
        
    Returns:
        dict: API response with product data
        
    Raises:
        ValueError: If client_id is unknown
    """
    store_url = _get_store_url(client_id)
    if not store_url:
        raise ValueError(f"Unknown client_id: {client_id}")
    
    product_url = get_product_url(store_url, product_id)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(product_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
```

**Key Points:**
- Separate API logic from the adapter layer
- Add validation for client_id and credentials
- Use proper error handling
- Return consistent data structures
- Add comprehensive docstrings

---

### Phase 4: Implement Connection Adapter

#### 4.1 Create the Engine Class

File: `<platform_name>/connection_adapter/adapter.py`

```python
from base.base import CatalogBase
from <platform_name>.services.<platform_name>_services import (
    get_access_token,
    list_client_products,
    get_client_product
)


class WooCommerceEngine(CatalogBase):
    """
    Main engine for WooCommerce integration.
    
    Extends CatalogBase and implements required methods for
    product catalog operations.
    """
    
    def __init__(self, client_id: str):
        """
        Initialize the WooCommerce engine.
        
        Args:
            client_id: Unique identifier for the client/store
        """
        self._access_token = None
        self._access_token_expires_in = None
        super().__init__(client_id)
    
    def _get_access_token(self):
        """
        Retrieve and cache access token.
        
        Checks if token exists and is valid. If not, requests
        a new token and caches it along with expiration time.
        """
        if self._access_token is None or self._access_token_expires_in is None:
            access_credentials = get_access_token(self._client_id)
            self._access_token = access_credentials.get("access_token")
            self._access_token_expires_in = access_credentials.get("expires_in")
    
    def list_products(self, limit: int = None):
        """
        Fetch a list of products from WooCommerce.
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            dict: JSON response containing products
        """
        self._get_access_token()
        products = list_client_products(self._client_id, self._access_token, limit)
        return products
    
    def get_product(self, product_id: int):
        """
        Fetch a single product by ID from WooCommerce.
        
        Args:
            product_id: Unique identifier of the product
            
        Returns:
            dict: JSON response containing product data
        """
        self._get_access_token()
        return get_client_product(self._client_id, self._access_token, product_id)
```

**Required Methods:**
- `list_products(limit: int = None)` - Fetch multiple products
- `get_product(product_id: int)` - Fetch a single product by ID

**Key Points:**
- Must extend `CatalogBase`
- Implement both abstract methods
- Handle authentication internally
- Cache tokens to avoid unnecessary API calls
- Import from services layer, not utils

---

### Phase 5: Implement Webhook Utilities

#### 5.1 Create Router Utilities

File: `<platform_name>/utils/<platform_name>_router_utils.py`

```python
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from <platform_name>.config import WOOCOMMERCE_WEBHOOK_SECRET


# In-memory cache for processed event IDs
processed_event_ids = {}


def is_duplicate_event(event_id: str) -> bool:
    """
    Check if an event has already been processed.
    
    Prevents duplicate webhook processing when platforms
    send multiple delivery attempts.
    
    Args:
        event_id: Unique event identifier from webhook header
        
    Returns:
        bool: True if event was already processed
    """
    current_time = datetime.now()
    
    # Check if event exists in cache
    if event_id in processed_event_ids:
        return True
    
    # Add event to cache
    processed_event_ids[event_id] = current_time
    
    # Cleanup old events (older than 24 hours)
    for eid in list(processed_event_ids.keys()):
        if (current_time - processed_event_ids[eid]) > timedelta(hours=24):
            del processed_event_ids[eid]
    
    return False


def verify_webhook(data: bytes, signature: str) -> bool:
    """
    Verify webhook signature to ensure authenticity.
    
    Implementation varies by platform:
    - HMAC-SHA256 (Shopify, WooCommerce)
    - Digital signatures (BigCommerce)
    - Custom verification (Magento)
    
    Args:
        data: Raw webhook payload (bytes)
        signature: Signature from webhook header
        
    Returns:
        bool: True if signature is valid
    """
    if not WOOCOMMERCE_WEBHOOK_SECRET:
        return False
    
    # Example: HMAC-SHA256 verification (WooCommerce style)
    digest = hmac.new(
        WOOCOMMERCE_WEBHOOK_SECRET.encode("utf-8"),
        data,
        hashlib.sha256
    ).digest()
    
    computed_signature = base64.b64encode(digest).decode("utf-8")
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(computed_signature, signature)
```

**Key Points:**
- Implement duplicate event detection
- Use HMAC for signature verification
- Make webhook secret validation graceful
- Clean up old event IDs periodically

---

### Phase 6: Implement Webhook Handlers

Create three webhook handlers for product lifecycle events.

#### 6.1 Product Create Handler

File: `<platform_name>/routers/product_create.py`

```python
from fastapi import APIRouter, Request, Header, HTTPException
import json
from <platform_name>.utils.<platform_name>_router_utils import (
    verify_webhook,
    is_duplicate_event
)

router = APIRouter()


@router.post("/products/create")
async def product_created(
    request: Request,
    x_wc_webhook_signature: str = Header(None),
    x_wc_webhook_id: str = Header(None)
):
    """
    Handle product creation webhook.
    
    Headers:
        x-wc-webhook-signature: Webhook signature for verification
        x-wc-webhook-id: Unique event identifier
        
    Returns:
        int: HTTP status code
    """
    print("🔔 Webhook received: products/create")
    
    # Step 1: Check for duplicate events
    if x_wc_webhook_id and is_duplicate_event(x_wc_webhook_id):
        print("⚠️  Duplicate event - skipping")
        return 200
    
    # Step 2: Read request body
    body = await request.body()
    
    # Step 3: Verify webhook signature
    if not x_wc_webhook_signature:
        print("❌ Webhook signature missing")
        raise HTTPException(status_code=401)
    
    if not verify_webhook(body, x_wc_webhook_signature):
        print("❌ Webhook verification failed")
        raise HTTPException(status_code=401, detail="Invalid webhook")
    
    # Step 4: Parse and process webhook data
    product = json.loads(body.decode("utf-8"))
    
    print("\n" + "="*60)
    print("📦 PRODUCT DATA (CREATE):")
    print("="*60)
    print(f"Product ID: {product.get('id')}")
    print(f"Title: {product.get('name')}")
    print("="*60 + "\n")
    
    # TODO: Add your business logic here
    # - Save to database
    # - Trigger sync operations
    # - Send notifications
    
    return 200
```

#### 6.2 Product Update Handler

File: `<platform_name>/routers/product_update.py`

```python
from fastapi import APIRouter, Request, Header, HTTPException
import json
from <platform_name>.utils.<platform_name>_router_utils import (
    verify_webhook,
    is_duplicate_event
)

router = APIRouter()


@router.post("/products/update")
async def product_updated(
    request: Request,
    x_wc_webhook_signature: str = Header(None),
    x_wc_webhook_id: str = Header(None)
):
    """Handle product update webhook."""
    print("🔔 Webhook received: products/update")
    
    if x_wc_webhook_id and is_duplicate_event(x_wc_webhook_id):
        print("⚠️  Duplicate event - skipping")
        return 200
    
    body = await request.body()
    
    if not x_wc_webhook_signature:
        print("❌ Webhook signature missing")
        raise HTTPException(status_code=401)
    
    if not verify_webhook(body, x_wc_webhook_signature):
        print("❌ Webhook verification failed")
        raise HTTPException(status_code=401, detail="Invalid webhook")
    
    product = json.loads(body.decode("utf-8"))
    
    print("\n" + "="*60)
    print("📦 PRODUCT DATA (UPDATE):")
    print("="*60)
    print(f"Product ID: {product.get('id')}")
    print(f"Title: {product.get('name')}")
    print("="*60 + "\n")
    
    return 200
```

#### 6.3 Product Delete Handler

File: `<platform_name>/routers/product_delete.py`

```python
from fastapi import APIRouter, Request, Header, HTTPException
import json
from <platform_name>.utils.<platform_name>_router_utils import (
    verify_webhook,
    is_duplicate_event
)

router = APIRouter()


@router.post("/products/delete")
async def product_deleted(
    request: Request,
    x_wc_webhook_signature: str = Header(None),
    x_wc_webhook_id: str = Header(None)
):
    """Handle product deletion webhook."""
    print("🔔 Webhook received: products/delete")
    
    if x_wc_webhook_id and is_duplicate_event(x_wc_webhook_id):
        print("⚠️  Duplicate event - skipping")
        return 200
    
    body = await request.body()
    
    if not x_wc_webhook_signature:
        print("❌ Webhook signature missing")
        raise HTTPException(status_code=401)
    
    if not verify_webhook(body, x_wc_webhook_signature):
        print("❌ Webhook verification failed")
        raise HTTPException(status_code=401, detail="Invalid webhook")
    
    product = json.loads(body.decode("utf-8"))
    
    print("\n" + "="*60)
    print("📦 PRODUCT DATA (DELETE):")
    print("="*60)
    print(f"Product ID: {product.get('id')}")
    print("="*60 + "\n")
    
    return 200
```

**Key Points:**
- Always check for duplicates first
- Verify webhook signature before processing
- Use platform-specific header names
- Return 200 even for duplicates (prevents retries)
- Add business logic after verification

---

### Phase 7: Configure Webhook Router

#### 7.1 Create Router Aggregator

File: `<platform_name>/webhook/<platform_name>.py`

```python
from fastapi import APIRouter

from <platform_name>.routers.product_create import router as create_router
from <platform_name>.routers.product_update import router as update_router
from <platform_name>.routers.product_delete import router as delete_router

# Create main router with prefix and tags
router = APIRouter(
    prefix="/webhooks/<platform_name>",
    tags=["YourPlatform"]
)

# Include all product webhook routers
router.include_router(create_router)
router.include_router(update_router)
router.include_router(delete_router)
```

This creates endpoints:
- `POST /webhooks/woocommerce/products/create`
- `POST /webhooks/woocommerce/products/update`
- `POST /webhooks/woocommerce/products/delete`

---

### Phase 8: Register Integration

#### 8.1 Update Main App

File: `app.py`

```python
import uvicorn
from fastapi import FastAPI

from shopify.webhook import shopify
from woocommerce.webhook import woocommerce  # Add import
from config import APP_HOST, APP_PORT

app = FastAPI(title="E-Commerce Webhook Handler")

# Include webhook routers
app.include_router(shopify.router)
app.include_router(woocommerce.router)  # Add router

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "Webhook Handler Running"}

if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
```

#### 8.2 Update Factory Pattern

File: `__init__.py`

```python
from base.integrations import Integrations
from shopify.connection_adapter.adapter import ShopifyEngine
from woocommerce.connection_adapter.adapter import WooCommerceEngine  # Add import

__all__ = ["ShopifyEngine", "WooCommerceEngine", "Integrations"]

_ENGINE_REGISTRY = {
    Integrations.SHOPIFY.value: ShopifyEngine,
    Integrations.WOOCOMMERCE.value: WooCommerceEngine,  # Add to registry
}


def get_engine(integration_name: str, client_id: str):
    """
    Factory function to get the appropriate engine.
    
    Args:
        integration_name: Name of the integration platform
        client_id: Client identifier
        
    Returns:
        CatalogBase: Engine instance for the platform
        
    Raises:
        ValueError: If integration is not supported
    """
    engine_cls = _ENGINE_REGISTRY.get(integration_name)
    if not engine_cls:
        raise ValueError(f"Unknown integration: {integration_name}")
    return engine_cls(client_id)
```

**Key Points:**
- Use `_ENGINE_REGISTRY` for easy extension
- Import the engine class
- Add to `__all__` for proper exports
- No need for long if/else chains

---

## Code Style Guidelines

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for all classes and functions (Google style)
- Maximum line length: **100 characters**
- Use **absolute imports** (not relative)

### Formatting

```bash
# Format code with black
black <platform_name>/

# Check style with flake8
flake8 <platform_name>/
```

### Naming Conventions

- **Modules**: `lowercase_with_underscores` (e.g., `shopify_services.py`)
- **Classes**: `PascalCase` (e.g., `ShopifyEngine`, `WooCommerceEngine`)
- **Functions**: `lowercase_with_underscores` (e.g., `get_client_product`, `list_client_products`)
- **Constants**: `UPPERCASE_WITH_UNDERSCORES` (e.g., `SHOPIFY_API_VERSION`)
- **Private methods/vars**: `_leading_underscore` (e.g., `_get_store_url`)

### Documentation

Every function should have a docstring:

```python
def get_client_product(client_id: str, access_token: str, product_id: int) -> dict:
    """
    Fetch a single product by ID from the platform API.
    
    This function retrieves detailed product information including
    variants, images, pricing, and inventory data.
    
    Args:
        client_id: Unique identifier for the client/store
        access_token: Authentication token for API access
        product_id: Unique identifier of the product to fetch
        
    Returns:
        dict: Product data in platform-specific format, or None if not found
        
    Raises:
        ValueError: If client_id is unknown or invalid
        requests.RequestException: If API request fails
        
    Example:
        >>> product = get_client_product("12345", "token_abc", 7890)
        >>> print(product['title'])
        'Cotton T-Shirt'
    """
    pass
```

---

## Testing Requirements

### Unit Tests

Create tests for your integration:

```python
# tests/test_woocommerce.py
import pytest
from woocommerce.connection_adapter.adapter import WooCommerceEngine
from woocommerce.services.woocommerce_services import get_client_product


def test_engine_initialization():
    """Test engine can be initialized."""
    engine = WooCommerceEngine("test_client_id")
    assert engine._client_id == "test_client_id"
    assert engine._access_token is None


def test_list_products():
    """Test listing products."""
    engine = WooCommerceEngine("12345")
    # Mock API response or use test credentials
    products = engine.list_products(limit=5)
    assert products is not None


def test_get_product():
    """Test getting single product."""
    engine = WooCommerceEngine("12345")
    product = engine.get_product(123)
    assert product is not None
```

### Webhook Tests

```python
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_webhook_create():
    """Test product create webhook."""
    response = client.post(
        "/webhooks/woocommerce/products/create",
        json={"id": 123, "name": "Test Product"},
        headers={
            "X-WC-Webhook-Signature": "valid_signature",
            "X-WC-Webhook-ID": "unique_event_id"
        }
    )
    assert response.status_code == 200


def test_webhook_duplicate():
    """Test duplicate event detection."""
    headers = {
        "X-WC-Webhook-Signature": "valid_signature",
        "X-WC-Webhook-ID": "duplicate_id"
    }
    
    # First request
    response1 = client.post(
        "/webhooks/woocommerce/products/create",
        json={"id": 123},
        headers=headers
    )
    
    # Duplicate request
    response2 = client.post(
        "/webhooks/woocommerce/products/create",
        json={"id": 123},
        headers=headers
    )
    
    assert response1.status_code == 200
    assert response2.status_code == 200  # Should still return 200
```

---

## Submission Process

### Before Submitting

1. ✅ **Test your integration** - Ensure all functionality works
2. ✅ **Format your code** - Run `black` and `flake8`
3. ✅ **Update documentation** - Add platform-specific notes to README
4. ✅ **Write tests** - Add unit and integration tests
5. ✅ **Check dependencies** - Update `requirements.txt` if needed
6. ✅ **Test webhooks** - Verify HMAC verification works
7. ✅ **Check imports** - Ensure all imports are absolute, not relative

### Pull Request Checklist

```markdown
## Description
Brief description of the integration (e.g., "Add WooCommerce integration")

## Platform Details
- **Platform**: WooCommerce
- **API Version**: v3
- **Authentication**: OAuth 2.0 / Consumer Key & Secret
- **Webhook Verification**: HMAC-SHA256

## Implementation Checklist
- [ ] Extends `CatalogBase` correctly
- [ ] Implements `list_products()` and `get_product()`
- [ ] Services layer created with proper functions
- [ ] Webhook handlers with signature verification
- [ ] Duplicate event detection implemented
- [ ] Configuration added under integration package (`woocommerce/config.py`)
- [ ] Integration registered in `__init__.py` `_ENGINE_REGISTRY`
- [ ] Integration added to `base/integrations.py` enum
- [ ] Webhook router registered in `app.py`
- [ ] Tests added and passing
- [ ] Documentation updated (README.md)
- [ ] Code formatted (`black`, `flake8` passing)
- [ ] All imports are absolute (not relative)

## Testing
Describe how you tested the integration:
- [ ] Tested product listing
- [ ] Tested single product fetch
- [ ] Tested webhook create/update/delete
- [ ] Tested HMAC verification
- [ ] Tested duplicate event detection

## Environment Variables
List required environment variables:
```bash
WOOCOMMERCE_STORE_URL=yourstore.com
WOOCOMMERCE_CONSUMER_KEY=ck_xxx
WOOCOMMERCE_CONSUMER_SECRET=cs_xxx
WOOCOMMERCE_WEBHOOK_SECRET=whs_xxx
```

## Screenshots (optional)
Add screenshots of API responses or webhook handling
```

---

## Platform-Specific Notes

### WooCommerce
- **Authentication**: Consumer Key/Secret (Basic Auth or OAuth 1.0a)
- **API Endpoint**: `/wp-json/wc/v3/`
- **Webhook Signature**: HMAC-SHA256 in `X-WC-Webhook-Signature` header
- **Event ID**: Use `X-WC-Webhook-ID` header
- **Docs**: https://woocommerce.github.io/woocommerce-rest-api-docs/

### Magento
- **Authentication**: Token-based authentication
- **API Endpoint**: `/rest/V1/`
- **Webhook**: Custom implementation or use Magento webhooks module
- **Event Tracking**: Implement custom event ID tracking
- **Docs**: https://devdocs.magento.com/guides/v2.4/rest/bk-rest.html

### BigCommerce
- **Authentication**: OAuth 2.0
- **API Endpoint**: `/stores/{store_hash}/v3/`
- **Webhook Signature**: Digital signature verification
- **Event ID**: Use webhook event ID from payload
- **Docs**: https://developer.bigcommerce.com/api-docs

### Shopify (Reference Implementation)
- **Authentication**: OAuth 2.0 (client credentials)
- **API Endpoint**: `/admin/api/{version}/`
- **Webhook Signature**: HMAC-SHA256 in `X-Shopify-Hmac-SHA256` header
- **Event ID**: Use `X-Shopify-Event-ID` header
- **Docs**: https://shopify.dev/docs/api

---

## Questions?

If you have questions or need help:
1. **Check existing integrations** - Review `shopify/` directory for reference
2. **Review the README.md** - General project documentation
3. **Open an issue** - Ask questions on GitHub
4. **Contact maintainers** - Reach out for guidance

Thank you for contributing! 🎉
