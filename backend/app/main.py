from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth as auth_router
from .routers import complaints as complaints_router
from .routers import notices as notices_router
from .routers import dashboard as dashboard_router

app = FastAPI(title="Society Maintenance Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(complaints_router.router)
app.include_router(notices_router.router)
app.include_router(dashboard_router.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "society-maintenance-tracker-api"}