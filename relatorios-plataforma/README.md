# Plataforma de Relatórios

MVP local para centralizar os relatórios que o time sobe diariamente, com controle de acesso por papel (Admin / Gestor / Membro) e por time.

## Arquitetura

- **Backend**: FastAPI + SQLAlchemy + SQLite, autenticação via JWT, arquivos salvos em disco local (`backend/uploads/<team_id>/`).
- **Frontend**: React + TypeScript (Vite), React Router, Axios.

## Modelo de permissões

| Papel   | Relatórios que vê                     | Gerenciamento |
|---------|----------------------------------------|---------------|
| Admin   | Todos, de todos os times               | Cria/edita/remove usuários e times |
| Gestor  | Todos os relatórios do seu time        | Apenas visualiza usuários do seu time |
| Membro  | Apenas os relatórios que ele mesmo enviou | Nenhum |

Todo usuário pertence a um time. Upload de relatório fica sempre associado ao time do usuário que enviou.

## Como rodar

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed.py          # cria o time "Geral" e o usuário admin inicial
uvicorn app.main:app --port 8000 --reload
```

Credenciais criadas pelo seed:
- **Email**: `admin@empresa.com`
- **Senha**: `admin123`

**Troque essa senha assim que fizer o primeiro login** (Administração > Usuários, ou via API).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse http://localhost:5173.

## Uso típico

1. Login como admin.
2. Em **Administração**, crie os times (ex.: um por área/departamento).
3. Crie os usuários do time, definindo papel (Admin/Gestor/Membro) e time.
4. Cada usuário loga e sobe seus relatórios diários pela tela **Relatórios** (título, descrição opcional, arquivo).
5. Gestores acompanham os relatórios do próprio time; admins acompanham tudo, com filtro por time.

## Limitações do MVP / próximos passos

- Armazenamento em disco local — para produção/nuvem, trocar por S3 (ou equivalente) é a mudança recomendada primeiro.
- Sem recuperação de senha por email (troca de senha só via painel do admin).
- Sem paginação na listagem de relatórios (ok para poucas dezenas/centenas de arquivos; revisar se o volume crescer muito).
- `SECRET_KEY` do JWT está com valor de desenvolvimento em `backend/app/core/config.py` — defina a variável de ambiente `SECRET_KEY` antes de qualquer deploy real.
