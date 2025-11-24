# backend/app/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from .database import Base, engine, get_db
from . import models, schemas, auth, llm, docx_export, pptx_export
from .config import settings


# =========================================================
# 1️⃣  SINGLE FASTAPI INSTANCE — DO NOT REPEAT
# =========================================================
app = FastAPI(title="AI-Assisted Document Authoring Platform")


# =========================================================
# 2️⃣  CORS MUST COME IMMEDIATELY AFTER APP CREATION
# =========================================================
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# 3️⃣  HOME ROUTE
# =========================================================
@app.get("/")
def home():
    return {"message": "AI Document Platform API is running 🚀"}


# =========================================================
# 4️⃣  CREATE DATABASE TABLES (AFTER APP + CORS)
# =========================================================
Base.metadata.create_all(bind=engine)


# =========================================================
# 5️⃣  AUTH ROUTES
# =========================================================

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth.get_password_hash(user_in.password)

    new_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = auth.create_access_token(
        data={"sub": user.id},
        expires_delta=expires,
    )

    return {"access_token": token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# =========================================================
# 6️⃣  PROJECT ROUTES
# =========================================================

@app.get("/projects", response_model=list[schemas.ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Project).filter(
        models.Project.owner_id == current_user.id
    ).all()


@app.post("/projects", response_model=schemas.ProjectOut)
def create_project(
    project_in: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if project_in.doc_type not in ("docx", "pptx"):
        raise HTTPException(status_code=400, detail="Invalid doc_type")

    project = models.Project(
        title=project_in.title,
        topic=project_in.topic,
        doc_type=project_in.doc_type,
        owner_id=current_user.id,
    )

    db.add(project)
    db.flush()  # so project.id becomes available

    for section in project_in.sections:
        db.add(models.Section(
            title=section.title,
            order=section.order,
            project_id=project.id,
        ))

    db.commit()
    db.refresh(project)

    return project


@app.get("/projects/{project_id}", response_model=schemas.ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project

@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # 1. Load the project
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Find all sections in this project
    sections = db.query(models.Section).filter(
        models.Section.project_id == project_id
    ).all()

    section_ids = [s.id for s in sections]

    # 3. DELETE comments for each section
    db.query(models.Comment).filter(
        models.Comment.section_id.in_(section_ids)
    ).delete(synchronize_session=False)

    # 4. DELETE refinement history for each section
    db.query(models.RefinementHistory).filter(
        models.RefinementHistory.section_id.in_(section_ids)
    ).delete(synchronize_session=False)

    # 5. DELETE sections
    db.query(models.Section).filter(
        models.Section.project_id == project_id
    ).delete(synchronize_session=False)

    # 6. DELETE the project
    db.delete(project)

    db.commit()

    return {"message": "Project and all related data deleted successfully"}

@app.post("/projects/{project_id}/generate", response_model=schemas.ProjectOut)
def generate_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sections = db.query(models.Section).filter(
        models.Section.project_id == project.id
    ).all()

    for sec in sections:
        new_text = llm.generate_llm_content(
            section_title=sec.title,
            topic=project.topic
        )

        db.add(models.RefinementHistory(
            section_id=sec.id,
            old_content=sec.content,
            new_content=new_text,
            prompt="Initial generation",
        ))

        sec.content = new_text

    db.commit()
    db.refresh(project)

    return project


# =========================================================
# 7️⃣  SECTION REFINEMENT + COMMENTS + FEEDBACK
# =========================================================

@app.post("/sections/{section_id}/refine", response_model=schemas.SectionOut)
def refine_section(
    section_id: int,
    req: schemas.RefinementRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    section = db.query(models.Section).join(models.Project).filter(
        models.Section.id == section_id,
        models.Project.owner_id == current_user.id
    ).first()

    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    new_text = llm.refine_llm_content(
        current_content=section.content or "",
        prompt=req.prompt
    )

    db.add(models.RefinementHistory(
        section_id=section.id,
        old_content=section.content,
        new_content=new_text,
        prompt=req.prompt,
    ))

    section.content = new_text

    db.commit()
    db.refresh(section)

    return section


@app.post("/sections/{section_id}/feedback")
def save_feedback(
    section_id: int,
    req: schemas.FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    section = db.query(models.Section).join(models.Project).filter(
        models.Section.id == section_id,
        models.Project.owner_id == current_user.id
    ).first()

    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    latest = db.query(models.RefinementHistory).filter(
        models.RefinementHistory.section_id == section.id
    ).order_by(models.RefinementHistory.created_at.desc()).first()

    if latest:
        latest.liked = req.liked
        db.commit()

    return {"message": "Feedback saved"}


@app.post("/sections/{section_id}/comment")
def save_comment(
    section_id: int,
    req: schemas.CommentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    section = db.query(models.Section).join(models.Project).filter(
        models.Section.id == section_id,
        models.Project.owner_id == current_user.id
    ).first()

    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    db.add(models.Comment(
        section_id=section.id,
        text=req.text,
    ))

    db.commit()

    return {"message": "Comment added"}


# =========================================================
# 8️⃣  EXPORT ROUTES — DOCX + PPTX
# =========================================================

@app.get("/projects/{project_id}/export/docx")
def export_docx(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.doc_type != "docx":
        raise HTTPException(status_code=400, detail="Project type is not docx")

    stream = docx_export.build_docx(project)

    return StreamingResponse(
        stream,
        headers={"Content-Disposition": f'attachment; filename="{project.title}.docx"'},
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.get("/projects/{project_id}/export/pptx")
def export_pptx(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.doc_type != "pptx":
        raise HTTPException(status_code=400, detail="Project type is not pptx")

    stream = pptx_export.build_pptx(project)

    return StreamingResponse(
        stream,
        headers={"Content-Disposition": f'attachment; filename="{project.title}.pptx"'},
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
