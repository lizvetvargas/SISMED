
import os
import hashlib
import hmac
import secrets
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .database import Base, engine, SessionLocal
from .models import (
    Usuario,
    Paciente,
    Medico,
    Cita,
    HistoriaClinica,
)
from .routes import pacientes


# =========================================================
# 1. CONFIGURACIÓN DE RUTAS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# 2. CONFIGURACIÓN DE SEGURIDAD
# =========================================================

SECRET_KEY = os.environ.get("SISMED_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "Falta SISMED_SECRET_KEY. Configúrala en la terminal "
        "antes de iniciar SISMED."
    )


def crear_hash(password: str) -> str:
    """Genera un hash seguro de la contraseña con PBKDF2."""
    salt = secrets.token_hex(16)

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600_000,
    )

    return f"pbkdf2_sha256${salt}${resultado.hex()}"


def verificar_password(password: str, almacenada: str) -> bool:
    """Verifica contraseñas protegidas y antiguas."""
    if not almacenada:
        return False

    if almacenada.startswith("pbkdf2_sha256$"):
        try:
            algoritmo, salt, hash_guardado = almacenada.split("$")

            if algoritmo != "pbkdf2_sha256":
                return False

            resultado = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                600_000,
            ).hex()

            return hmac.compare_digest(resultado, hash_guardado)

        except (ValueError, TypeError):
            return False

    # Compatibilidad temporal con contraseñas anteriores.
    return hmac.compare_digest(password, almacenada)


# =========================================================
# 3. CREACIÓN DE LA APLICACIÓN
# =========================================================

app = FastAPI(
    title="SISMED",
    description="Sistema de Gestión Médica - Consultorio Los Rosales",
    version="1.0.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=False,
    same_site="lax",
    max_age=3600,
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# =========================================================
# 4. REGISTRO DE MÓDULOS
# =========================================================

# Activa las rutas del módulo de pacientes.
app.include_router(pacientes.router)


# =========================================================
# 5. CREACIÓN DE TABLAS
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# 6. USUARIO DE DEMOSTRACIÓN
# =========================================================

def crear_usuario_demo():
    """Crea el administrador si todavía no existe."""
    db = SessionLocal()

    try:
        usuario = (
            db.query(Usuario)
            .filter(Usuario.username == "admin")
            .first()
        )

        if usuario is None:
            usuario = Usuario(
                username="admin",
                password=crear_hash("123456"),
                nombre="Administrador",
                rol="Administrador",
            )

            db.add(usuario)
            db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


crear_usuario_demo()


# =========================================================
# 7. PÁGINA DE INICIO
# =========================================================

@app.get("/")
def inicio(request: Request):
    """Muestra el formulario de inicio de sesión."""
    if request.session.get("usuario"):
        return RedirectResponse(
            url="/dashboard",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None},
    )


# =========================================================
# 8. INICIO DE SESIÓN
# =========================================================

@app.post("/login")
def iniciar_sesion(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Valida las credenciales y crea la sesión."""
    db = SessionLocal()

    try:
        usuario = (
            db.query(Usuario)
            .filter(Usuario.username == username.strip())
            .first()
        )

        if usuario is None or not verificar_password(
            password,
            usuario.password,
        ):
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "error": "Usuario o contraseña incorrectos."
                },
                status_code=401,
            )

        # Actualiza contraseñas antiguas al iniciar sesión.
        if not usuario.password.startswith("pbkdf2_sha256$"):
            usuario.password = crear_hash(password)
            db.commit()

        request.session.clear()
        request.session["usuario"] = usuario.username
        request.session["nombre"] = usuario.nombre
        request.session["rol"] = usuario.rol

        return RedirectResponse(
            url="/dashboard",
            status_code=303,
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# =========================================================
# 9. PANEL PRINCIPAL
# =========================================================

@app.get("/dashboard")
def dashboard(request: Request):
    """Muestra el panel principal del sistema."""
    if not request.session.get("usuario"):
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    db = SessionLocal()

    try:
        total_pacientes = db.query(Paciente).count()
        total_medicos = db.query(Medico).count()
        total_citas = db.query(Cita).count()

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "nombre": request.session.get(
                    "nombre",
                    "Administrador",
                ),
                "rol": request.session.get(
                    "rol",
                    "Administrador",
                ),
                "total_pacientes": total_pacientes,
                "total_medicos": total_medicos,
                "total_citas": total_citas,
            },
        )

    finally:
        db.close()


# =========================================================
# 10. CIERRE DE SESIÓN
# =========================================================

@app.get("/logout")
def cerrar_sesion(request: Request):
    """Elimina la sesión activa."""
    request.session.clear()

    return RedirectResponse(
        url="/",
        status_code=303,
    )


# =========================================================
# 11. COMPROBACIÓN DEL SISTEMA
# =========================================================

@app.get("/estado")
def estado():
    """Comprueba que la aplicación esté funcionando."""
    return {
        "sistema": "SISMED",
        "estado": "funcionando",
    }