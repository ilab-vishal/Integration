from base.integrations import Integrations
from shopify.connection_adapter.adapter import ShopifyEngine


__all__ = ["ShopifyEngine", "Integrations"]


_ENGINE_REGISTRY = {
    Integrations.SHOPIFY.value: ShopifyEngine,
}


def get_engine(integration_name: str, client_id: str):
    engine_cls = _ENGINE_REGISTRY.get(integration_name)
    if not engine_cls:
        raise ValueError(f"Unknown integration: {integration_name}")
    return engine_cls(client_id)
