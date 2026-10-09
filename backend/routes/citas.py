from datetime import date

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Cita, Paciente, Medico

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/citas")
def lista_citas(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    citas = db.query(Cita).order_by(
        Cita.fecha.desc()
    ).all()

    pacientes = {
        p.id: p
        for p in db.query(Paciente).all()
    }

    medicos = {
        m.id: m
        for m in db.query(Medico).all()
    }

    db.close()

    return templates.TemplateResponse(
        "citas/lista.html",
        {
            "request": request,
            "citas": citas,
            "pacientes": pacientes,
            "medicos": medicos
        }
    )


@router.get("/citas/registrar")
def registrar_cita_form(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    pacientes = db.query(Paciente).all()
    medicos = db.query(Medico).all()

    db.close()

    return templates.TemplateResponse(
        "citas/registrar.html",
        {
            "request": request,
            "pacientes": pacientes,
            "medicos": medicos
        }
    )


@router.post("/citas/registrar")
def registrar_cita(
    request: Request,
    paciente_id: int = Form(...),
    medico_id: int = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    motivo: str = Form("")
):

    db = SessionLocal()

    cita = Cita(
        paciente_id=paciente_id,
        medico_id=medico_id,
        fecha=date.fromisoformat(fecha),
        hora=hora,
        motivo=motivo,
        estado="Pendiente"
    )

    db.add(cita)
    db.commit()

    db.close()

    return RedirectResponse(
        "/citas",
        status_code=303
    )


@router.post("/citas/{cita_id}/estado")
def cambiar_estado(
    request: Request,
    cita_id: int,
    estado: str = Form(...)
):

    db = SessionLocal()

    cita = db.query(Cita).filter(
        Cita.id == cita_id
    ).first()

    if cita:
        cita.estado = estado
        db.commit()

    db.close()

    return RedirectResponse(
        "/citas",
        status_code=303
    )