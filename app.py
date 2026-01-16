import uvicorn
from fastapi import FastAPI

from shopify.webhook import shopify
from config import APP_HOST, APP_PORT

app = FastAPI(title="Shopify Webhook Handler")

app.include_router(shopify.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "Shopify Webhook Handler Running"}

if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
