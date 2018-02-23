"""
    Default Configuration for Flask Config
"""
import os

class Config:
    """
        Config base class
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    @staticmethod
    def init_app(app):
        """
            For Flask Standard
        """
        pass

class DevelopmentConfig(Config):
    """
        Config for debug environment
    """
    DEBUG = True

class TestingConfig(Config):
    """
        Config for test environment
    """
    TESTING = True

class ProductionConfig(Config):
    """
        Config for production environment
    """
    PRODUCTION = True

CONFIG = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
