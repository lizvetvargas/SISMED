
from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Paciente, HistoriaClinica

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


def usuario_autenticado(request: Request) -> bool:
    return bool(request.session.get("usuario"))


@router.get("/historias")
def lista_historias(request: Request):
    if not usuario_autenticado(request):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        pacientes = (
            db.query(Paciente)
            .order_by(Paciente.apellidos, Paciente.nombres)
            .all()
        )

        historias = db.query(HistoriaClinica).all()

        historias_por_paciente = {
            historia.paciente_id: historia
            for historia in historias
        }

        return templates.TemplateResponse(
            request=request,
            name="historias/lista.html",
            context={
                "pacientes": pacientes,
                "historias": historias,
                "historias_por_paciente": historias_por_paciente,
            },
        )
    finally:
        db.close()


@router.get("/historias/{paciente_id}")
def detalle_historia(request: Request, paciente_id: int):
    if not usuario_autenticado(request):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        paciente = (
            db.query(Paciente)
            .filter(Paciente.id == paciente_id)
            .first()
        )

        if not paciente:
            return RedirectResponse("/historias", status_code=303)

        historia = (
            db.query(HistoriaClinica)
            .filter(HistoriaClinica.paciente_id == paciente_id)
            .first()
        )

        return templates.TemplateResponse(
            request=request,
            name="historias/detalle.html",
            context={
                "paciente": paciente,
                "historia": historia,
            },
        )
    finally:
        db.close()


@router.post("/historias/guardar")
def guardar_historia(
    request: Request,
    paciente_id: int = Form(...),
    antecedentes: str = Form(""),
    diagnostico: str = Form(""),
    tratamiento: str = Form(""),
    observaciones: str = Form(""),
):
    if not usuario_autenticado(request):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        paciente = (
            db.query(Paciente)
            .filter(Paciente.id == paciente_id)
            .first()
        )

        if not paciente:
            return RedirectResponse("/historias", status_code=303)

        historia = (
            db.query(HistoriaClinica)
            .filter(HistoriaClinica.paciente_id == paciente_id)
            .first()
        )

        if historia:
            historia.antecedentes = antecedentes.strip() or None
            historia.diagnostico = diagnostico.strip() or None
            historia.tratamiento = tratamiento.strip() or None
            historia.observaciones = observaciones.strip() or None
        else:
            historia = HistoriaClinica(
                paciente_id=paciente_id,
                antecedentes=antecedentes.strip() or None,
                diagnostico=diagnostico.strip() or None,
                tratamiento=tratamiento.strip() or None,
                observaciones=observaciones.strip() or None,
            )
            db.add(historia)

        db.commit()

        return RedirectResponse(
            f"/historias/{paciente_id}",
            status_code=303,
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()