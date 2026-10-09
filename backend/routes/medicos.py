
from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Medico

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/medicos")
def lista_medicos(request: Request):
    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        medicos = db.query(Medico).order_by(Medico.apellidos).all()

        return templates.TemplateResponse(
            request=request,
            name="medicos/lista.html",
            context={"medicos": medicos},
        )
    finally:
        db.close()


@router.get("/medicos/registrar")
def registrar_medico_form(request: Request):
    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="medicos/registrar.html",
        context={},
    )


@router.post("/medicos/registrar")
def registrar_medico(
    request: Request,
    nombres: str = Form(...),
    apellidos: str = Form(...),
    especialidad: str = Form(...),
    telefono: str = Form(""),
    correo: str = Form(""),
):
    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    try:
        medico = Medico(
            nombres=nombres.strip(),
            apellidos=apellidos.strip(),
            especialidad=especialidad.strip(),
            telefono=telefono.strip() or None,
            correo=correo.strip() or None,
        )

        db.add(medico)
        db.commit()

        return RedirectResponse("/medicos", status_code=303)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()