
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Cita, Paciente, Medico

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get("/enfermeria")
def enfermeria(request: Request):
    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        citas = (
            db.query(Cita)
            .order_by(Cita.fecha.desc(), Cita.hora.asc())
            .all()
        )

        pacientes = {
            paciente.id: paciente
            for paciente in db.query(Paciente).all()
        }

        medicos = {
            medico.id: medico
            for medico in db.query(Medico).all()
        }

        return templates.TemplateResponse(
            request=request,
            name="enfermeria/lista.html",
            context={
                "citas": citas,
                "pacientes": pacientes,
                "medicos": medicos,
            },
        )

    finally:
        db.close()