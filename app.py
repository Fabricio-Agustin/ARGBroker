from database.db_manager import DatabaseManager
from models.auth_model import AuthRepository 
from models.transaccion_model import TransaccionRepository
from controllers.auth_controller import AuthManager

def main():
    db = DatabaseManager()
    
    repo_auth = AuthRepository(db)
    repo_trans = TransaccionRepository(db)
    
    auth = AuthManager(repo_auth, repo_trans)
    
    try:
        auth.run()
    except Exception as e:
        print(f"\n[Error crítico al ejecutar la aplicación]: {e}")

if __name__ == "__main__":
    main()