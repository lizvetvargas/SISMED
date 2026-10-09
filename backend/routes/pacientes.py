
from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Paciente, HistoriaClinica


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# =========================================================
# 1. LISTA DE PACIENTES
# =========================================================

@router.get("/pacientes")
def lista_pacientes(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        pacientes = (
            db.query(Paciente)
            .order_by(Paciente.apellidos)
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="pacientes/lista.html",
            context={
                "pacientes": pacientes
            }
        )

    finally:
        db.close()


# =========================================================
# 2. FORMULARIO DE REGISTRO
# =========================================================

@router.get("/pacientes/registrar")
def registrar_paciente_form(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="pacientes/registrar.html",
        context={}
    )


# =========================================================
# 3. GUARDAR PACIENTE
# =========================================================

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

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    # Comprobamos que el DNI tenga ocho dígitos.
    dni = dni.strip()

    if len(dni) != 8 or not dni.isdigit():
        return RedirectResponse(
            "/pacientes/registrar",
            status_code=303
        )

    db = SessionLocal()

    try:
        # El modelo actual no contiene fecha_nacimiento.
        # Por eso no enviamos ese campo al constructor.
        # La fecha se integrará cuando se añada formalmente
        # al modelo y a la estructura de la base de datos.

        paciente = Paciente(
            dni=dni,
            nombres=nombres.strip(),
            apellidos=apellidos.strip(),
            telefono=telefono.strip() or None,
            direccion=direccion.strip() or None
        )

        db.add(paciente)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    return RedirectResponse(
        "/pacientes",
        status_code=303
    )


# =========================================================
# 4. DETALLE DEL PACIENTE
# =========================================================

@router.get("/pacientes/{paciente_id}")
def detalle_paciente(
    request: Request,
    paciente_id: int
):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        paciente = (
            db.query(Paciente)
            .filter(Paciente.id == paciente_id)
            .first()
        )

        if paciente is None:
            return RedirectResponse(
                "/pacientes",
                status_code=303
            )

        historia = (
            db.query(HistoriaClinica)
            .filter(
                HistoriaClinica.paciente_id == paciente_id
            )
            .first()
        )

        return templates.TemplateResponse(
            request=request,
            name="pacientes/detalle.html",
            context={
                "paciente": paciente,
                "historia": historia
            }
        )

    finally:
        db.close()