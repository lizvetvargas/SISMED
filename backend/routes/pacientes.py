from datetime import date

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Paciente, HistoriaClinica

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/pacientes")
def lista_pacientes(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    pacientes = db.query(Paciente).order_by(
        Paciente.apellidos
    ).all()

    db.close()

    return templates.TemplateResponse(
        "pacientes/lista.html",
        {
            "request": request,
            "pacientes": pacientes
        }
    )


@router.get("/pacientes/registrar")
def registrar_paciente_form(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        "pacientes/registrar.html",
        {
            "request": request
        }
    )


@router.post("/pacientes/registrar")
def registrar_paciente(
    request: Request,
    dni: str = Form(...),
    nombres: str = Form(...),
    apellidos: str = Form(...),
    fecha_nacimiento: str = Form(""),
    telefono: str = Form(""),
    direccion: str = Form("")
):

    db = SessionLocal()

    fecha = None

    if fecha_nacimiento:
        fecha = date.fromisoformat(fecha_nacimiento)

    paciente = Paciente(
        dni=dni,
        nombres=nombres,
        apellidos=apellidos,
        fecha_nacimiento=fecha,
        telefono=telefono,
        direccion=direccion
    )

    db.add(paciente)
    db.commit()

    db.close()

    return RedirectResponse(
        "/pacientes",
        status_code=303
    )


@router.get("/pacientes/{paciente_id}")
def detalle_paciente(
    request: Request,
    paciente_id: int
):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()

    historia = db.query(HistoriaClinica).filter(
        HistoriaClinica.paciente_id == paciente_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        "pacientes/detalle.html",
        {
            "request": request,
            "paciente": paciente,
            "historia": historia
        }
    )