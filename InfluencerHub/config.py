from dotenv import load_dotenv
import os
from app import app

load_dotenv()

app.config["SECRET_KEY"]=os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv('SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['UPLOAD_FOLDER_CIMG']=os.getenv('UPLOAD_FOLDER_CIMG')
app.config['UPLOAD_FOLDER_PPIC']=os.getenv('UPLOAD_FOLDER_PPIC')
app.config['CACHE_TYPE'] = os.getenv('CACHE_TYPE')
app.config['CACHE_REDIS_HOST'] = os.getenv('CACHE_REDIS_HOST')
app.config['CACHE_REDIS_PORT'] = os.getenv('CACHE_REDIS_PORT') 
app.config['CACHE_REDIS_PASSWORD'] = os.getenv("CACHE_REDIS_PASSWORD")
app.config['CACHE_DEFAULT_TIMEOUT'] = os.getenv('CACHE_DEFAULT_TIMEOUT')
app.config['JWT_SECRET_KEY']=os.getenv('JWT_SECRET_KEY')