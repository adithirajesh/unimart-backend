from app import app
from database import init_db
from models import User, Product

init_db(app)
print("Database and tables created!")