
from pathlib import Path
from datetime import date

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Cita, Paciente, Medico

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

ESTADOS_VALIDOS = {
    "Pendiente",
    "Confirmada",
    "Atendida",
    "Cancelada",
}


def usuario_autenticado(request: Request) -> bool:
    return bool(request.session.get("usuario"))


@router.get("/citas")
def lista_citas(request: Request):
    if not usuario_autenticado(request):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        citas = (
            db.query(Cita)
            .order_by(Cita.fecha.desc(), Cita.hora.asc())
            .all()
        )

        pacientes = {
            p.id: p for p in db.query(Paciente).all()
        }

        medicos = {
            m.id: m for m in db.query(Medico).all()
        }

        return templates.TemplateResponse(
            request=request,
            name="citas/lista.html",
            context={
                "citas": citas,
                "pacientes": pacientes,
                "medicos": medicos,
            },
        )
    finally:
        db.close()


@router.get("/citas/registrar")
def registrar_cita_form(request: Request):
    if not usuario_autenticado(request):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        pacientes = (
            db.query(Paciente)
            .order_by(Paciente.apellidos, Paciente.nombres)
            .all()
        )

        medicos = (
            db.query(Medico)
            .order_by(Medico.apellidos, Medico.nombres)
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="citas/registrar.html",
            context={
                "pacientes": pacientes,
                "medicos": medicos,
            },
        )
    finally:
        db.close()


@router.post("/citas/registrar")
def registrar_cita(
    request: Request,
    paciente_id: int = Form(...),
    medico_id: int = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    motivo: str = Form(""),
):
    if not usuario_autenticado(request):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        # Validar fecha y hora.
        try:
            fecha_validada = date.fromisoformat(fecha)
            hora_validada = hora.strip()

            from datetime import time
            time.fromisoformat(hora_validada)
        except ValueError:
            return RedirectResponse(
                "/citas/registrar?error=fecha_hora",
                status_code=303,
            )

        # Confirmar que el paciente y el médico existen.
        paciente = db.query(Paciente).filter(
            Paciente.id == paciente_id
        ).first()

        medico = db.query(Medico).filter(
            Medico.id == medico_id
        ).first()

        if not paciente or not medico:
            return RedirectResponse(
                "/citas/registrar?error=seleccion",
                status_code=303,
            )

        # Evitar duplicar una cita activa del mismo médico.
        cita_existente = db.query(Cita).filter(
            Cita.medico_id == medico_id,
            Cita.fecha == fecha_validada.isoformat(),
            Cita.hora == hora_validada,
            Cita.estado != "Cancelada",
        ).first()

        if cita_existente:
            return RedirectResponse(
                "/citas/registrar?error=horario",
                status_code=303,
            )

        cita = Cita(
            paciente_id=paciente_id,
            medico_id=medico_id,
            fecha=fecha_validada.isoformat(),
            hora=hora_validada,
            motivo=motivo.strip() or None,
            estado="Pendiente",
        )

        db.add(cita)
        db.commit()

        return RedirectResponse("/citas", status_code=303)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.post("/citas/{cita_id}/estado")
def cambiar_estado(
    request: Request,
    cita_id: int,
    estado: str = Form(...),
):
    if not usuario_autenticado(request):
        return RedirectResponse("/", status_code=303)

    if estado not in ESTADOS_VALIDOS:
        return RedirectResponse("/citas", status_code=303)

    db = SessionLocal()

    try:
        cita = db.query(Cita).filter(
            Cita.id == cita_id
        ).first()

        if not cita:
            return RedirectResponse("/citas", status_code=303)

        cita.estado = estado
        db.commit()

        return RedirectResponse("/citas", status_code=303)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()