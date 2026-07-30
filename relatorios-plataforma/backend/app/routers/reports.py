import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Team, Report, Role
from app.schemas import ReportOut
from app.deps import get_current_user
from app.core.config import UPLOAD_DIR, MAX_UPLOAD_SIZE_MB, ALLOWED_EXTENSIONS

router = APIRouter(prefix="/reports", tags=["reports"])


def _to_out(report: Report) -> ReportOut:
    out = ReportOut.model_validate(report)
    out.owner_name = report.owner.name if report.owner else None
    out.team_name = report.team.name if report.team else None
    return out


@router.get("", response_model=List[ReportOut])
def list_reports(
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Report)

    if current_user.role == Role.ADMIN:
        pass
    elif current_user.role == Role.GESTOR:
        query = query.filter(Report.team_id == current_user.team_id)
    else:
        query = query.filter(Report.owner_id == current_user.id)

    if team_id is not None:
        query = query.filter(Report.team_id == team_id)

    reports = query.order_by(Report.created_at.desc()).all()
    return [_to_out(r) for r in reports]


@router.post("", response_model=ReportOut, status_code=201)
async def upload_report(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.team_id:
        raise HTTPException(status_code=400, detail="Você precisa estar em um time para enviar relatórios")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo de arquivo não permitido: {ext}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"Arquivo excede o limite de {MAX_UPLOAD_SIZE_MB}MB")

    team_dir = UPLOAD_DIR / str(current_user.team_id)
    team_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = team_dir / stored_filename
    with open(dest_path, "wb") as f:
        f.write(contents)

    report = Report(
        title=title,
        description=description,
        original_filename=file.filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        size_bytes=len(contents),
        owner_id=current_user.id,
        team_id=current_user.team_id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return _to_out(report)


def _get_report_or_404(report_id: int, db: Session) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return report


def _check_access(report: Report, user: User):
    if user.role == Role.ADMIN:
        return
    if user.role == Role.GESTOR and report.team_id == user.team_id:
        return
    if report.owner_id == user.id:
        return
    raise HTTPException(status_code=403, detail="Você não tem permissão para acessar este relatório")


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_report_or_404(report_id, db)
    _check_access(report, current_user)

    file_path = UPLOAD_DIR / str(report.team_id) / report.stored_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no servidor")

    return FileResponse(
        path=file_path,
        filename=report.original_filename,
        media_type=report.content_type or "application/octet-stream",
    )


@router.delete("/{report_id}", status_code=204)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_report_or_404(report_id, db)
    _check_access(report, current_user)

    file_path = UPLOAD_DIR / str(report.team_id) / report.stored_filename
    if file_path.exists():
        file_path.unlink()

    db.delete(report)
    db.commit()
