import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from config import SHOPIFY_WEBHOOK_SECRET


processed_event_ids = {}

def is_duplicate_event(event_id: str) -> bool:
    current_time = datetime.now()
    
    if event_id in processed_event_ids:
        return True
    
    processed_event_ids[event_id] = current_time
    
    for eid in list(processed_event_ids.keys()):
        if (current_time - processed_event_ids[eid]) > timedelta(hours=24):
            del processed_event_ids[eid]
    
    return False

def verify_shopify_webhook(data: bytes, hmac_header: str):
    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode("utf-8"),
        data,
        hashlib.sha256
    ).digest()

    computed_hmac = base64.b64encode(digest).decode("utf-8")
    print(f"🔐 Computed HMAC: {computed_hmac}")
    print(f"🔐 Received HMAC: {hmac_header}")
    print(f"🔐 Match: {hmac.compare_digest(computed_hmac, hmac_header)}")
    return hmac.compare_digest(computed_hmac, hmac_header)