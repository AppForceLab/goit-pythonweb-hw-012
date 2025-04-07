"""
Jinja2 Templates Service.

This module provides a global Jinja2Templates instance for rendering HTML templates.
The templates are loaded from the 'templates' directory in the project root.
"""

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
