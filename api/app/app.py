from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.routers import todos


app = FastAPI()


# Setting up the metrics
Instrumentator().instrument(app).expose(app, '/metrics')


# Setting up the routers
app.include_router(todos.router)
