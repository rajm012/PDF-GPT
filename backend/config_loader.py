import os
import toml
import logging
from typing import Dict, Any, Union
from pathlib import Path

class ConfigLoader:
    """Enhanced configuration loader supporting TOML and environment variables"""
    
    def __init__(self, config_file: str = "config.toml"):
        self.config_file = config_file
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from TOML file and environment variables"""
        # Load TOML configuration
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config_data = toml.load(f)
                print(f"✅ Loaded configuration from {self.config_file}")
            except Exception as e:
                print(f"⚠️ Error loading TOML config: {e}")
                self.config_data = {}
        else:
            print(f"⚠️ Config file {self.config_file} not found, using environment variables only")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to environment variables"""
        # First try TOML config
        if section in self.config_data and key in self.config_data[section]:
            return self.config_data[section][key]
        
        # Fallback to environment variable
        env_key = f"{section.upper()}_{key.upper()}" if section else key.upper()
        env_value = os.getenv(env_key)
        
        if env_value is not None:
            # Try to convert to appropriate type
            return self._convert_type(env_value, default)
        
        # Fallback to default
        return default
    
    def get_flat(self, key: str, default: Any = None) -> Any:
        """Get configuration value without section (for backward compatibility)"""
        # Try environment variable first
        env_value = os.getenv(key)
        if env_value is not None:
            return self._convert_type(env_value, default)
        
        # Try to find in any section of TOML
        for section_data in self.config_data.values():
            if isinstance(section_data, dict) and key in section_data:
                return section_data[key]
        
        return default
    
    def _convert_type(self, value: str, default: Any) -> Any:
        """Convert string value to appropriate type based on default"""
        if default is None:
            return value
        
        target_type = type(default)
        
        try:
            if target_type == bool:
                return value.lower() in ('true', '1', 'yes', 'on')
            elif target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == list:
                # Handle comma-separated lists
                return [item.strip() for item in value.split(',')]
            else:
                return value
        except (ValueError, AttributeError):
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get all values from a section"""
        result = {}
        
        # Get from TOML
        if section in self.config_data:
            result.update(self.config_data[section])
        
        # Override with environment variables
        env_prefix = f"{section.upper()}_"
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                result[config_key] = value
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire configuration to dictionary"""
        result = {}
        
        # Add TOML data
        result.update(self.config_data)
        
        # Add environment variables
        for key, value in os.environ.items():
            if '_' in key:
                parts = key.lower().split('_', 1)
                section, config_key = parts[0], parts[1]
                
                if section not in result:
                    result[section] = {}
                
                result[section][config_key] = value
        
        return result

# Global configuration instance
config = ConfigLoader()

# Legacy configuration class for backward compatibility
class Config:
    """Base configuration class with TOML support"""
    
    def __init__(self):
        self.SECRET_KEY = config.get_flat('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.UPLOAD_FOLDER = config.get_flat('UPLOAD_FOLDER', 'data/uploads')
        self.VECTOR_DB_PATH = config.get_flat('VECTOR_DB_PATH', 'data/vector_db')
        self.MAX_FILE_SIZE = config.get_flat('MAX_FILE_SIZE', 50) * 1024 * 1024  # Convert MB to bytes
        self.CHUNK_SIZE = config.get_flat('CHUNK_SIZE', 1000)
        self.CHUNK_OVERLAP = config.get_flat('CHUNK_OVERLAP', 200)
        
        # Ollama configuration
        self.OLLAMA_HOST = config.get_flat('OLLAMA_HOST', 'http://localhost:11434')
        self.OLLAMA_MODEL = config.get_flat('OLLAMA_MODEL', 'llama3')
        
        # Logging
        self.LOG_LEVEL = config.get_flat('LOG_LEVEL', 'INFO')
        self.LOG_FILE = config.get_flat('LOG_FILE', 'logs/app.log')
        
        # Performance
        self.WORKERS = config.get_flat('WORKERS', 4)
        self.THREADS = config.get_flat('THREADS', 2)

class DevelopmentConfig(Config):
    """Development configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration with TOML support"""
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.FLASK_ENV = 'production'
        
        # Security settings from TOML
        self.ALLOWED_HOSTS = config.get('security', 'ALLOWED_HOSTS', ['localhost'])
        self.ENABLE_RATE_LIMITING = config.get('features', 'ENABLE_RATE_LIMITING', True)
        self.MAX_UPLOADS_PER_HOUR = config.get('features', 'MAX_UPLOADS_PER_HOUR', 10)
    
    @staticmethod
    def init_app(app):
        # Ensure log directory exists
        log_file = config.get_flat('LOG_FILE', 'logs/app.log')
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Set up rotating file handler
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('PDF GPT startup with TOML config')

class TestingConfig(Config):
    """Testing configuration"""
    def __init__(self):
        super().__init__()
        self.TESTING = True

# Configuration mapping
config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
