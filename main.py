from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI()


# Mount static if you have CSS or JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")


DATABASE_URL = "sqlite:///./mood.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    mood = Column(String, unique=True, index=True)
    recipe = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed initial data (run only once or put in startup event)
def seed_data():
    db = SessionLocal()
    if db.query(Recipe).count() == 0:
        db.add_all([
            Recipe(mood="happy", recipe="Sunshine Salad"),
            Recipe(mood="sad", recipe="Comfort Mac & Cheese"),
            Recipe(mood="adventurous", recipe="Spicy Thai Curry"),
        ])
        db.commit()
    db.close()

seed_data()
@app.get("/")
def root():
    return {"status": "working"}

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "recipe": None})

@app.post("/", response_class=HTMLResponse)
def get_recipe(request: Request, mood: str = Form(...)):
    db = SessionLocal()
    recipe_obj = db.query(Recipe).filter(Recipe.mood == mood.lower()).first()
    db.close()
    recipe = recipe_obj.recipe if recipe_obj else "No recipe found for that mood."
    return templates.TemplateResponse("index.html", {"request": request, "recipe": recipe})
