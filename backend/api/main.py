# backend/api/main.py
import os
import importlib
from fastapi import FastAPI

app = FastAPI()

def auto_include_routers():
    """Automatically discover and include routers from all subdirectories in api/"""
    api_dir = os.path.dirname(__file__)
    
    # Get all subdirectories in the api folder
    for item in os.listdir(api_dir):
        item_path = os.path.join(api_dir, item)
        
        # Check if it's a directory and not a special directory
        if os.path.isdir(item_path) and not item.startswith('__'):
            controller_path = os.path.join(item_path, 'controller.py')
            
            # Check if controller.py exists in this directory
            if os.path.exists(controller_path):
                try:
                    # Import the router from the controller module
                    module_name = f"api.{item}.controller"
                    module = importlib.import_module(module_name)
                    
                    # Try different common router naming patterns
                    router = None
                    router_names = ['router', f'{item}_router', 'api_router']
                    
                    for router_name in router_names:
                        if hasattr(module, router_name):
                            router = getattr(module, router_name)
                            break
                    
                    if router:
                        app.include_router(router)
                        print(f"✅ Auto-included router from: {module_name}")
                    else:
                        print(f"⚠️  No router found in: {module_name} (tried: {router_names})")
                        
                except ImportError as e:
                    print(f"❌ Failed to import router from {item}: {e}")
                except Exception as e:
                    print(f"❌ Error including router from {item}: {e}")

# Auto-include all routers
auto_include_routers()

@app.get("/health")
async def health():
    return {"status": "ok"}
