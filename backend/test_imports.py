#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing FastAPI import...")
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__} imported successfully")
        
        print("Testing SQLAlchemy import...")
        from sqlalchemy.ext.asyncio import AsyncSession
        print("✓ SQLAlchemy AsyncSession imported successfully")
        
        print("Testing config import...")
        from config import settings
        print("✓ Config settings imported successfully")
        
        print("Testing database session import...")
        from db.session import get_db
        print("✓ Database session imported successfully")
        
        print("Testing API imports...")
        from api.errors.schema import ErrorPayload
        from api.errors.service import ErrorService
        from api.errors.controller import router
        print("✓ All API imports successful")
        
        print("Testing database models...")
        from db.models.errors import RawError
        from db.repositories.errors import ErrorRepository
        print("✓ All database imports successful")
        
        print("\n🎉 All imports successful! Auto-suggestions should work now.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_imports() 