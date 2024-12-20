from fastapi import FastAPI
from loguru import logger

from config.appconfig import MONGO_URL, DATABASE, SERVER_PORT
from db.db import DB


app = FastAPI()

def get_db():
    return app.state.db


@app.on_event("startup")
async def startup():
    db_name = DATABASE
    app.state.db = DB(MONGO_URL, db_name)
    await app.state.db.setup_indexes()
    logger.info("MongoDB client and repositories initialized")

@app.on_event("shutdown")
async def shutdown():
    app.state.db.close()

from router.orders import orders_router
from router.products import product_router

app.include_router(product_router)
app.include_router(orders_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
