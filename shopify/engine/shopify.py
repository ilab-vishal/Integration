from base.base import CatalogBase
from shopify.utils.shopify_utils import get_access_token, list_client_products, get_product

class ShopifyEngine(CatalogBase):
    def __init__(self,client_id:str):
        self._access_token = None
        self._access_token_expires_in = None
        super().__init__(client_id)
    
    def _get_access_token(self):
        if self._access_token is None or self._access_token_expires_in is None:
            access_credentials = get_access_token(self._client_id)
            self._access_token = access_credentials.get("access_token")
            self._access_token_expires_in = access_credentials.get("expires_in")


    def list_products(self, limit:int = None):
        self._get_access_token()
        products = list_client_products(self._client_id, self._access_token, limit)
        return products

    def get_product(self, product_id: int):
        self._get_access_token()
        return get_product(self._client_id, self._access_token, product_id)