"""PHINDU API entry point."""

from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine, Base
from app.api.routes import products
from app.api.routes import sales
from app.api.routes import analytics
from app.api.routes import dashboard
from app.api.routes import expenses
from app.api.routes import alerts
from app.api.routes import sessions
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",# Local development
        "https://phindu-app.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(products)          # products is the router object directly
app.include_router(sales)             # sales is the router object directly
app.include_router(expenses.router)
app.include_router(alerts.router)
app.include_router(sessions.router)

# Create tables
Base.metadata.create_all(bind=engine)

# Ensure existing SQLite DB schema has any new columns
if engine.url.drivername == "sqlite":
    with engine.begin() as conn:
        # sale_items columns
        existing_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(sale_items)"))]
        if "cost_price" not in existing_columns:
            conn.execute(text("ALTER TABLE sale_items ADD COLUMN cost_price FLOAT DEFAULT 0"))

        # products columns
        existing_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(products)"))]
        if "is_deleted" not in existing_columns:
            conn.execute(text("ALTER TABLE products ADD COLUMN is_deleted BOOLEAN DEFAULT 0"))
        if "archived" not in existing_columns:
            conn.execute(text("ALTER TABLE products ADD COLUMN archived BOOLEAN DEFAULT 0"))

        # sales columns – add session_id
        existing_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(sales)"))]
        if "session_id" not in existing_columns:
            conn.execute(text("ALTER TABLE sales ADD COLUMN session_id VARCHAR REFERENCES sessions(id)"))

        # expenses columns – add session_id
        existing_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(expenses)"))]
        if "session_id" not in existing_columns:
            conn.execute(text("ALTER TABLE expenses ADD COLUMN session_id VARCHAR REFERENCES sessions(id)"))

@app.get("/")
def root():
    return {"message": "PHINDU BACKEND RUNNING small businesses sales & insights  🔥"}

@app.get("/ping")
def ping():
    return {"ping": "pong"}