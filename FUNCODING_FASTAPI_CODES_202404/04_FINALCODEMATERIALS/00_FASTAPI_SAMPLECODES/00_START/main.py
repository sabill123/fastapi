from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/inherit")
def template_inherit(request: Request):
    my_text = "FastAPI와 Jinja2를 이용한 예시입니다."
    return templates.TemplateResponse("index.html", {"request": request, "text": my_text})