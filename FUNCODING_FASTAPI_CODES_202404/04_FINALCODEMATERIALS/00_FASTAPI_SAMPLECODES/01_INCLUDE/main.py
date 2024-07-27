from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/include_example")
def include_example(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})