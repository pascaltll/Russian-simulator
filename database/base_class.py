"""
Base class for SQLAlchemy declarative models.

This module provides the declarative base from which all SQLAlchemy models
in the application will inherit.
"""
# Group 1: Standard libraries
# None for now.

# Group 2: Third-party libraries
# Corrected: Use sqlalchemy.orm.declarative_base as recommended by SQLAlchemy 2.0+
from sqlalchemy.orm import declarative_base

# Group 3: First-party modules
# None for now.

# Initialize the declarative base.
# All SQLAlchemy models will inherit from this Base.
# This helps in defining tables and their mappings to Python classes.
Base = declarative_base()
