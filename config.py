# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_secreta'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/dgspg'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
