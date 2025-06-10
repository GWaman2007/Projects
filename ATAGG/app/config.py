import os
from dotenv import load_dotenv

load_dotenv(r"E:\Aman's Tech and Gaming Guide\.env")

class Config:
    UPLOAD_FOLDER = 'guides/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

    # Blog settings
    POSTS_PER_PAGE = 10
    BLOG_TITLE = "Aman's Tech and Gaming Guide"
    BLOG_DESCRIPTION = "Your go-to resource for tech tutorials and gaming guides"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
