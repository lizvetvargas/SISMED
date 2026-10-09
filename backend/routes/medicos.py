from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Medico

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/medicos")
def lista_medicos(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    medicos = db.query(Medico).order_by(
        Medico.apellidos
    ).all()

    db.close()

    return templates.TemplateResponse(
        "medicos/lista.html",
        {
            "request": request,
            "medicos": medicos
        }
    )


@router.get("/medicos/registrar")
def registrar_medico_form(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        "medicos/registrar.html",
        {
            "request": request
        }
    )


@router.post("/medicos/registrar")
def registrar_medico(
    request: Request,
    nombres: str = Form(...),
    apellidos: str = Form(...),
    especialidad: str = Form(...),
    cmp: str = Form(""),
    telefono: str = Form("")
):

    db = SessionLocal()

    medico = Medico(
        nombres=nombres,
        apellidos=apellidos,
        especialidad=especialidad,
        cmp=cmp,
        telefono=telefono
    )

    db.add(medico)
    db.commit()

    db.close()

    return RedirectResponse(
        "/medicos",
        status_code=303
    )