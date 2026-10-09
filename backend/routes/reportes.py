
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Paciente, Medico, Cita


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


@router.get("/reportes")
def reportes(request: Request):

    # Verificar que el usuario haya iniciado sesión.
    if not request.session.get("usuario"):
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    db = SessionLocal()

    try:
        # Totales generales.
        total_pacientes = db.query(Paciente).count()
        total_medicos = db.query(Medico).count()
        total_citas = db.query(Cita).count()

        # Citas por estado.
        atendidas = (
            db.query(Cita)
            .filter(Cita.estado == "Atendida")
            .count()
        )

        pendientes = (
            db.query(Cita)
            .filter(Cita.estado == "Pendiente")
            .count()
        )

        confirmadas = (
            db.query(Cita)
            .filter(Cita.estado == "Confirmada")
            .count()
        )

        canceladas = (
            db.query(Cita)
            .filter(Cita.estado == "Cancelada")
            .count()
        )

        # Mostrar el reporte.
        return templates.TemplateResponse(
            request=request,
            name="reportes/dashboard.html",
            context={
                "pacientes": total_pacientes,
                "medicos": total_medicos,
                "citas": total_citas,
                "atendidas": atendidas,
                "pendientes": pendientes,
                "confirmadas": confirmadas,
                "canceladas": canceladas,
            },
        )

    finally:
        db.close()