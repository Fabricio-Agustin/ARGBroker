def iniciar_sesion(repo, id_usuario, password):
    if not id_usuario or not password:
        return {"exito": False, "mensaje": "Completa los campos."}
    usuario = repo.buscar_usuario(id_usuario)
    if not usuario:
        return {"exito": False, "mensaje": "ID no registrado."}
    if usuario['password'] == password:
        return {"exito": True, "mensaje": "Bienvenido.", "usuario": usuario}
    return {"exito": False, "mensaje": "Contraseña incorrecta."}

def registrar_cuenta(repo, id_usuario, nombre, email, password):
    if not all([id_usuario, nombre, email, password]):
        return "Todos los campos son obligatorios."
    if repo.buscar_usuario(id_usuario):
        return "El ID ya existe."
    if repo.registrar_usuario(id_usuario, nombre, email, password):
        return "Cuenta creada con éxito."
    return "Error interno."