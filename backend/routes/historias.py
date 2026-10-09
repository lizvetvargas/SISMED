from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..database import SessionLocal
from ..models import Paciente, HistoriaClinica

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/historias")
def lista_historias(request: Request):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    pacientes = db.query(Paciente).all()
    historias = db.query(HistoriaClinica).all()

    db.close()

    return templates.TemplateResponse(
        "historias/lista.html",
        {
            "request": request,
            "pacientes": pacientes,
            "historias": historias
        }
    )


@router.get("/historias/{paciente_id}")
def detalle_historia(
    request: Request,
    paciente_id: int
):

    if not request.session.get("usuario"):
        return RedirectResponse("/", status_code=303)

    db = SessionLocal()

    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()

    historia = db.query(HistoriaClinica).filter(
        HistoriaClinica.paciente_id == paciente_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        "historias/detalle.html",
        {
            "request": request,
            "paciente": paciente,
            "historia": historia
        }
    )


@router.post("/historias/guardar")
def guardar_historia(
    request: Request,
    paciente_id: int = Form(...),
    antecedentes: str = Form(""),
    diagnosticos: str = Form(""),
    tratamientos: str = Form(""),
    observaciones: str = Form("")
):

    db = SessionLocal()

    historia = db.query(HistoriaClinica).filter(
        HistoriaClinica.paciente_id == paciente_id
    ).first()

    if historia:
        historia.antecedentes = antecedentes
        historia.diagnosticos = diagnosticos
        historia.tratamientos = tratamientos
        historia.observaciones = observaciones

    else:
        historia = HistoriaClinica(
            paciente_id=paciente_id,
            antecedentes=antecedentes,
            diagnosticos=diagnosticos,
            tratamientos=tratamientos,
            observaciones=observaciones
        )

        db.add(historia)

    db.commit()
    db.close()

    return RedirectResponse(
        f"/historias/{paciente_id}",
        status_code=303
    )