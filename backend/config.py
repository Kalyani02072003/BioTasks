import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    LOG_FOLDER = os.path.join(os.getcwd(), "logs")
    ALLOWED_EXTENSIONS = {"pdb"}

config = Config()
