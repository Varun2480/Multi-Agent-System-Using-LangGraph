# app/main.py
from fastapi import FastAPI
from api.v1.router import api_router
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

app.include_router(api_router, prefix="/api/v1")
