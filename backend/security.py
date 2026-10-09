from fastapi import Request


def usuario_actual(request: Request):
    return request.session.get("usuario")


def verificar_usuario(request: Request):
    return request.session.get("usuario") is not None


def cerrar_sesion(request: Request):
    request.session.clear()