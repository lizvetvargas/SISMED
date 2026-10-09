from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Paciente, Medico, Cita

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/reportes")
def reportes(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    pacientes = db.query(Paciente).count()
    medicos = db.query(Medico).count()
    citas = db.query(Cita).count()

    atendidas = db.query(Cita).filter(
        Cita.estado == "Atendida"
    ).count()

    pendientes = db.query(Cita).filter(
        Cita.estado == "Pendiente"
    ).count()

    confirmadas = db.query(Cita).filter(
        Cita.estado == "Confirmada"
    ).count()

    canceladas = db.query(Cita).filter(
        Cita.estado == "Cancelada"
    ).count()

    db.close()

    return templates.TemplateResponse(
        "reportes/dashboard.html",
        {
            "request": request,
            "pacientes": pacientes,
            "medicos": medicos,
            "citas": citas,
            "atendidas": atendidas,
            "pendientes": pendientes,
            "confirmadas": confirmadas,
            "canceladas": canceladas
        }
    )