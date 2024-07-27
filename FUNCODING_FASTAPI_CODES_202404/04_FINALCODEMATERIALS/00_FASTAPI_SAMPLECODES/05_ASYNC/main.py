from fastapi import FastAPI
import asyncio

app = FastAPI()

async def fetch_data():
    await asyncio.sleep(2)
    return {"data": "some_data"}

@app.get("/")
async def read_root():
    data = await fetch_data()
    return {"message": "Hello, World!", "fetched_data": data}