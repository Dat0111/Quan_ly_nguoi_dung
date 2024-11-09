class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:huyng1234@localhost:5432/database_name'
    SECRET_KEY = 'your_secret_key'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465  # Đổi thành 465 cho SSL
    MAIL_USERNAME = 'your_email@gmail.com'
    MAIL_PASSWORD = 'your_password'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
