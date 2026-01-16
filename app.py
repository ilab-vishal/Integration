import uvicorn
from fastapi import FastAPI

from shopify.webhook import shopify

app = FastAPI(title="Shopify Webhook Handler")

app.include_router(shopify.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "Shopify Webhook Handler Running"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8050)
