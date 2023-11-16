from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
import logging
import os
from os.path import expanduser

from routes import router as paper_router


home = expanduser("~")
# Load environment variables (.env is not on git nor project folder, so copilot will not be able to find it)
mongo_config = dotenv_values(os.path.join(home, "creds", "mongodb.env"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = MongoClient(mongo_config["ATLAS_URI"])
    app.database = app.mongodb_client[mongo_config["DB_NAME"]]
    try:
        app.mongodb_client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        print("Connected to the MongoDB database!")
    except Exception as e:
        raise e
    yield
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(paper_router, tags=["papers"], prefix="/paper")