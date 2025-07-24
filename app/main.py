from fastapi import FastAPI
from app.database import engine, Base
from app.api.v1 import users ,utils , product
from prometheus_fastapi_instrumentator import Instrumentator

# database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CRUD API with Soft Delete",
    description="API complète avec CRUD ",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)


# Include  routes
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(utils.router, tags=["Health Check"])
app.include_router(product.router, prefix="/api/v1", tags=["produits"])

@app.get("/")
def root():
    return {
        "message": "API Ready"
        
    }