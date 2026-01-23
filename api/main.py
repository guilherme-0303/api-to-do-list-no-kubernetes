import uvicorn

from app.app import app
from app.core.database import engine
from app.models.base import table_registry


if __name__ == '__main__':
    table_registry.metadata.create_all(engine)
    uvicorn.run(app, host='0.0.0.0', port=8080)
