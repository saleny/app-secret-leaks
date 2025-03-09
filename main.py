from fastapi import FastAPI
from app.routers import auth, users, projects
from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
from app.utils.security import get_password_hash
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=["http://localhost:3000"],  # Адрес фронтенда
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
    expose_headers=["*"]

)

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(projects.router, prefix="/projects")



@app.on_event("startup")
def create_admin_user():
    with SessionLocal() as db:  # Используем менеджер контекста
        try:
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                hashed_password = get_password_hash("admin")
                admin_user = User(
                    username="admin",
                    hashed_password=hashed_password,
                    is_admin=True,
                    disabled=False,
                )
                db.add(admin_user)
                db.commit()
                print("✅ Admin user created successfully")
            else:
                print("ℹ️ Admin user already exists")
        except Exception as e:
            db.rollback()
            print(f"❌ Error creating admin user: {e}")
        finally:
            db.close()

@app.get("/")
async def root():
    return {"message": "Secret Scanner API"}

