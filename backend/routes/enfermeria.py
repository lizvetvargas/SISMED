from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Cita, Paciente, Medico

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/enfermeria")
def enfermeria(request: Request):

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
        "enfermeria/lista.html",
        {
            "request": request,
            "citas": citas,
            "pacientes": pacientes,
            "medicos": medicos
        }
    )