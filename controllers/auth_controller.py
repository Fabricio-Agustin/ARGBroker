from models.auth_model import buscar_usuario_por_id, registrar_usuario_db

def iniciar_sesion(id_usuario, password):
    if not id_usuario or not password:
        return {"exito": False, "mensaje": " Debes completar todos los campos."}
        
    usuario = buscar_usuario_por_id(id_usuario)
    if not usuario:
        return {"exito": False, "mensaje": " El ID de usuario no está registrado."}
    
    if usuario['password'] == password:
        return {
            "exito": True, 
            "mensaje": f" ¡Conexión establecida! Bienvenido.", 
            "usuario": usuario
        }
    else:
        return {"exito": False, "mensaje": " Contraseña incorrecta."}

def registrar_cuenta(id_usuario, nombre, email, password):
    if not id_usuario or not password or not nombre or not email:
        return " Todos los campos son obligatorios para el registro."
        
    if buscar_usuario_por_id(id_usuario):
        return " El ID de usuario ya se encuentra registrado."
        
    if registrar_usuario_db(id_usuario, nombre, email, password):
        return " Cuenta creada con éxito. Ya puedes iniciar sesión con tus $10,000 iniciales."
    return " Hubo un error interno al crear la cuenta en la base de datos."