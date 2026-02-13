"""

This module sets up the FastAPI application with MongoDB integration.

It includes configuration for logging, database connections, and API routes.

"""

# Standard Library
import logging
import logging.config
import os
from contextlib import asynccontextmanager
from os.path import expanduser

# Third Party
import pymongo
from dotenv import dotenv_values
from fastapi import FastAPI
from pymongo import MongoClient

# Local imports
from .repositories.mongo_paper_repository import MongoPaperRepository
from .routes import router as paper_router  # Adjusted to absolute import
from .services.paper_service import PaperService

os.chdir(os.path.dirname(__file__))


# setup loggers
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

# get root logger
# the __name__ resolve to "main" since we are at the root of the project.
logger = logging.getLogger(__name__)
# This will get the root logger since no logger in the configuration has
# this name.

home = expanduser("~")
# Load environment variables
# (.env is not on git nor project folder, so copilot will not be able to
# find it)
mongo_config = dotenv_values(os.path.join(home, "creds", "mongodb.env"))


@asynccontextmanager
async def lifespan(api_app: FastAPI):
    """
    Asynchronous context manager for managing the lifecycle of the MongoDB
    connection. Intended for use with FastAPI's startup and shutdown events.

    Initializes and attaches the MongoDB client and database to the FastAPI
    app instance. Pings the MongoDB server to ensure a successful connection.
    Closes the MongoDB connection upon exiting the context.

    Parameters:
    app (FastAPI): The FastAPI app instance to attach the MongoDB client and
    database.

    Yields:
    None: Maintains the MongoDB connection until the context is exited.

    Raises:
    pymongo.errors.ConnectionFailure: If connection to the MongoDB database
    fails.
    """
    try:
        api_app.mongodb_client = MongoClient(mongo_config["ATLAS_URI"])
        api_app.database = api_app.mongodb_client[mongo_config["DB_NAME"]]
        api_app.paper_repository = MongoPaperRepository(
            api_app.database["papers"]
        )
        api_app.paper_service = PaperService(api_app.paper_repository)
        api_app.mongodb_client.admin.command("ping")
        logger.info(
            "Successfully connected to MongoDB! See API documentation at"
            " http://localhost:8000/docs#/papers"
        )
    except pymongo.errors.ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB database: {e}")
        raise
    else:
        yield
    finally:
        logger.info("Closing MongoDB connection!")
        api_app.mongodb_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(paper_router, tags=["papers"], prefix="/paper")
