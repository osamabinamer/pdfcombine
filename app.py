"""
Vercel Entry Point - Routes to API handler
"""
from api.index import handler

# This is required for Vercel to find the entry point
__all__ = ['handler']
