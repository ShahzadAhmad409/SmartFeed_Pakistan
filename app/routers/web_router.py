from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app import auth, models, database
from sqlalchemy.orm import Session

router = APIRouter(tags=["Web Pages"])
templates = Jinja2Templates(directory="app/templates")

def get_optional_user(request: Request, db: Session = Depends(database.get_db)):
    return auth.get_current_user(request, db)

@router.get("/", response_class=HTMLResponse)
def index(request: Request, current_user: models.User = Depends(get_optional_user)):
    return templates.TemplateResponse(request=request, name="index.html", context={"current_user": current_user})

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@router.get("/ngo-request", response_class=HTMLResponse)
def ngo_request_page(request: Request):
    return templates.TemplateResponse(request=request, name="ngo_request.html")

@router.get("/dashboard/donor", response_class=HTMLResponse)
def donor_dashboard(request: Request, current_user: models.User = Depends(auth.require_role(["donor"]))):
    return templates.TemplateResponse(request=request, name="donor_dashboard.html", context={"current_user": current_user})

@router.get("/dashboard/receiver", response_class=HTMLResponse)
def receiver_dashboard(request: Request, current_user: models.User = Depends(auth.require_role(["receiver"]))):
    return templates.TemplateResponse(request=request, name="receiver_dashboard.html", context={"current_user": current_user})

@router.get("/dashboard/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, current_user: models.User = Depends(auth.require_role(["admin", "superadmin"]))):
    return templates.TemplateResponse(request=request, name="admin_dashboard.html", context={"current_user": current_user})
