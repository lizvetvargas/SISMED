from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Paciente, Medico, Cita

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard")
def dashboard(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    pacientes = db.query(Paciente).count()
    medicos = db.query(Medico).count()
    citas = db.query(Cita).count()

    citas_recientes = db.query(Cita).order_by(
        Cita.id.desc()
    ).limit(5).all()

    db.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "nombre": request.session.get("nombre"),
            "rol": request.session.get("rol"),
            "pacientes": pacientes,
            "medicos": medicos,
            "citas": citas,
            "citas_recientes": citas_recientes
        }
    )