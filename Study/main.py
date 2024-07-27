from fastapi import FastAPI

app = FastAPI()

@app.get("/item/{item_id}")
def read_item(item_id):
    retrun {"item_id": item_id}