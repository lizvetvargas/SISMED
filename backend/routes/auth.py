from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Usuario

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def login(request: Request):
    if request.session.get("usuario"):
        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    )


@router.post("/login")
def iniciar_sesion(
    request: Request,
    usuario: str = Form(...),
    password: str = Form(...)
):
    db: Session = SessionLocal()

    user = db.query(Usuario).filter(
        Usuario.usuario == usuario,
        Usuario.password == password
    ).first()

    db.close()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Usuario o contraseña incorrectos."
            }
        )

    request.session["usuario"] = user.usuario
    request.session["nombre"] = user.nombre
    request.session["rol"] = user.rol

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


@router.get("/logout")
def cerrar_sesion(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/",
        status_code=303
    )