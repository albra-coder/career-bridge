# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'careerconnect-secret-key-2024'
    
    # MySQL 5.5 Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'root'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'careerconnect'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }