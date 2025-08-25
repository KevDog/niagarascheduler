"""
API Blueprints for Niagara University Scheduler
"""
from .config_bp import config_bp
from .departments_bp import departments_bp
from .courses_bp import courses_bp
from .offerings_bp import offerings_bp
from .schedule_bp import schedule_bp
from .syllabus_bp import syllabus_bp
from .health_bp import health_bp

__all__ = [
    'config_bp',
    'departments_bp',
    'courses_bp',
    'offerings_bp', 
    'schedule_bp',
    'syllabus_bp',
    'health_bp'
]