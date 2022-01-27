import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = '/tmp/'

DEBUG = True
#LOG_FILE = '/var/log/exmyb/exmyb.log'
LOG_FILE = 'exmyb.log'
LOG_LEVEL = 'DEBUG'

#https://pypi.org/project/Flask-SQLAlchemy/
username = os.getenv("DB_USERNAME", "root")
password = os.getenv("DB_PASSWORD", "Vivek123")
server = os.getenv("DB_HOST", "localhost")
database = os.getenv("DB_NAME", "xexmyb")

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}".format(username, password, server, database)
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# mongo credentials
MONGO_SERVER = os.getenv("Mongo_DB_HOST", "localhost")
MONGO_REPLICA_SET = os.getenv("MONGO_REPLICA_SET", "")
MONGO_USER = os.getenv("MONGO_USER", None)
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", None)
MONGO_DATABASE = os.getenv("MONGO_DATABASE", 'exmybdb')
MONGO_PORT = os.getenv("MONGO_PORT", 27017)
CHARTER_COLL = 'charter_coll'
PROJECT_CHARTER_COLL = 'project_charter_coll'
PERMISSION_COLL = 'perms_coll'
REVIEW_QUESTIONS = 'review_questions_coll'


#https://flask-jwt-extended.readthedocs.io/en/latest/options.html#configuration-options
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "unjsJsdfoHppsdsowerLYU768gtgascF")
JWT_ACCESS_TOKEN_EXPIRES = 1*60*60
JWT_REFRESH_TOKEN_EXPIRES = 6*30*24*60*60
JWT_ERROR_MESSAGE_KEY = 'message'


PAGINATION_PER_PAGE = 10

PROFILE_PIC_PATH = 'static/profile/'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
IMAGE_BASE_URL = ''

S3_REGION_NAME = os.getenv("S3_REGION_NAME", "")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "")
S3_ACL = 'public-read'
S3_DIR = 'exmyb/'
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
S3_CACHE_CONTROL = os.getenv("S3_CACHE_CONTROL", "")

#mail

SMTP_SERVER_ADDRESS = os.getenv("SMTP_SERVER_ADDRESS", "smtp.googlemail.com")
SMTP_SERVER_PORT = os.getenv("SMTP_SERVER_PORT", 587)
MAIL_USE_TLS = True
EMAIL_FROM_ADDR = 'prakash@exmyb.com'
EMAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = 'ExMyB'
MAIL_FORGOT_PASSWORD_SUBJ = 'ExMyB: Forgot Password'
MAIL_SIGNUP_SUBJ = 'ExMyB: Welcome'


####### Email configuration for amazon ses 
AWS_SES_ACCESS_KEY_ID=os.getenv("AWS_SES_ACCESS_KEY_ID", "AKIAVTP2PDZ4MD3XNQXX")
AWS_SES_SECRET_ACCESS_KEY=os.getenv("AWS_SES_SECRET_ACCESS_KEY", "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")
AWS_FROM_EMAIL_ADDR = os.getenv("AWS_FROM_EMAIL_ADDR", "testingtech@exmyb.com")

#2Factor SMS
TF_SMS_URL = 'https://2factor.in/API/V1/'
TF_AUTH_KEY = os.getenv("TF_AUTH_KEY", '3a705033-5293-11ec-b710-0200cd936042')
TF_TEMP_NAME = os.getenv("TF_TEMP_NAME", 'exmyb_temp2')

#user type

USER_TYPE = ['client', 'vendor', 'exmyb']

# S3 Bucket credentials
AWS_S3_ACCESS_KEY_ID=os.getenv("AWS_S3_ACCESS_KEY_ID","AKIAVTP2PDZ4GAFMJV4X")
AWS_S3_SECRET_ACCESS_KEY=os.getenv("AWS_S3_SECRET_ACCESS_KEY","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")
AWS_ATTACHMENTS_BUCKET_NAME=os.getenv("AWS_ATTACHMENTS_BUCKET_NAME","flasktest10")


UPLOAD_TYPE = ['profile', 'project', 'business_logo', 'vendor', 'client']

ALLOWED_EXTENSIONS = {
                        'profile': ['jpg', 'jpeg', 'png', 'gif'],
                        'project': ['jpg', 'jpeg', 'png', 'gif', 'pdf'],
                        'business_logo': ['jpg', 'jpeg', 'png', 'gif'],
                        'vendor': ['jpg', 'jpeg', 'png', 'gif', 'pdf'],
                        'client': ['jpg', 'jpeg', 'png', 'gif', 'pdf']
                      }


########## Credentials are for developing environment
ZOHO_CRM_CODE=os.getenv("ZOHO_CRM_CODE","1000.b957263a61d41e21a5d5e7921db35adf.f6b6aa0f59c5c01f8f23ad07ef32c2b1")
ZOHO_CRM_CLIENT_ID=os.getenv("ZOHO_CRM_CLIENT_ID","1000.QWQ0XZZ5GEJW8J092NDQY857OEW0XF")
ZOHO_CRM_CLIENT_SECRET=os.getenv("ZOHO_CRM_CLIENT_SECRET","32a1d15fa15ac815820227a899c3b00cb7afcdcf23")
ZOHO_CRM_FLASK_AUTHORIZATION_HEADER=os.getenv("ZOHO_CRM_FLASK_AUTHORIZATION_HEADER","PHkN6EGYLJnrHkfah5InnOoKOj5cE11uGLhFIgVmz6v16bifVS76t3ybNGgS2NsexesOudkDgpEidzQmrn9iJeWO2j")

STATIC_FILE_URL = 'https://flasktest10.s3.ap-south-1.amazonaws.com/'
REST_PASSWORD_URL = 'https://develop.dz9m62pu3us3m.amplifyapp.com/reset-password?code='

