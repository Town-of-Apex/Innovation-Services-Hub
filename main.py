from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os

from starlette.middleware.base import BaseHTTPMiddleware

# AAS-1.0: BASE_PATH support
BASE_PATH = os.getenv("BASE_PATH", "").rstrip('/')

app = FastAPI(
    title="Innovation Services Hub",
    root_path=BASE_PATH
)

# Setup DB
DATABASE_URL = "sqlite:///./services.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ServiceLink(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    url = Column(String)
    icon_svg = Column(Text)
    color = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Setup templates and static
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# AAS-1.0: Inject BASE_PATH into template globals
templates.env.globals["BASE_PATH"] = BASE_PATH

@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(get_db)):
    services = db.query(ServiceLink).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"services": services})

@app.get("/admin", response_class=HTMLResponse)
async def read_admin(request: Request, db: Session = Depends(get_db)):
    services = db.query(ServiceLink).all()
    return templates.TemplateResponse(request=request, name="admin.html", context={"services": services})

@app.post("/admin/add")
async def add_service(
    name: str = Form(...),
    description: str = Form(""),
    url: str = Form(...),
    icon_svg: str = Form(""),
    color: str = Form("#005a70"),
    db: Session = Depends(get_db)
):
    new_service = ServiceLink(name=name, description=description, url=url, icon_svg=icon_svg, color=color)
    db.add(new_service)
    db.commit()
    # AAS-1.0: Truly relative redirect
    return RedirectResponse(url="./", status_code=303)

@app.post("/admin/delete/{service_id}")
async def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(ServiceLink).filter(ServiceLink.id == service_id).first()
    if service:
        db.delete(service)
        db.commit()
    # AAS-1.0: Truly relative redirect back to admin root
    return RedirectResponse(url="../", status_code=303)

@app.post("/admin/edit/{service_id}")
async def edit_service(
    service_id: int,
    name: str = Form(...),
    description: str = Form(""),
    url: str = Form(...),
    icon_svg: str = Form(""),
    color: str = Form("#005a70"),
    db: Session = Depends(get_db)
):
    service = db.query(ServiceLink).filter(ServiceLink.id == service_id).first()
    if service:
        service.name = name
        service.description = description
        service.url = url
        service.icon_svg = icon_svg
        service.color = color
        db.commit()
    # AAS-1.0: Truly relative redirect
    return RedirectResponse(url="../", status_code=303)

if __name__ == "__main__":
    import uvicorn
    # AAS-1.0: Port 8080
    uvicorn.run(app, host="0.0.0.0", port=8080)
