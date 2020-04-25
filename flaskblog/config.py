import os
from dotenv import load_dotenv


class Config:
    load_dotenv()
    SECRET_KEY = 'jwhegfjhwegfjhwe'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    DEBUG = True
