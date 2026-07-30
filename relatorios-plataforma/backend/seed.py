"""Cria o time e o usuário admin iniciais, se ainda não existirem."""
from app.database import Base, engine, SessionLocal
from app.models import Team, User, Role
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    team = db.query(Team).filter(Team.name == "Geral").first()
    if not team:
        team = Team(name="Geral")
        db.add(team)
        db.commit()
        db.refresh(team)
        print(f"Time criado: {team.name}")

    admin_email = "admin@empresa.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin = User(
            name="Administrador",
            email=admin_email,
            hashed_password=hash_password("admin123"),
            role=Role.ADMIN,
            team_id=team.id,
        )
        db.add(admin)
        db.commit()
        print(f"Usuário admin criado: {admin_email} / senha: admin123")
        print("IMPORTANTE: troque essa senha após o primeiro login.")
    else:
        print("Usuário admin já existe.")
finally:
    db.close()
