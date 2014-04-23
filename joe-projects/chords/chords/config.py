class DevelopmentConfig(object):
    DATABASE_URI = "sqlite:///chords-development.db"
    DEBUG = True
    UPLOAD_FOLDER = "chords/uploads"

class TestingConfig(object):
    DATABASE_URI = "sqlite://"
    DEBUG = True
    UPLOAD_FOLDER = "chords/test-uploads"
