# backend/api/main.py

import logging
import pkgutil
import importlib
import pathlib
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FaultWatch API")


def auto_include_routers():
    """
    Scan each subdirectory under backend/api for a 'controller.py',
    import its 'router' object, and include it.
    """
    # 1) Path to this file's directory: backend/api
    base_path = pathlib.Path(__file__).parent
    # 2) The module path for imports: e.g. 'backend.api'
    pkg = __package__  # should be 'backend.api'
    
    for finder, name, is_pkg in pkgutil.iter_modules([str(base_path)]):
        if not is_pkg:
            continue
        
        controller_mod = f"{pkg}.{name}.controller"
        try:
            module = importlib.import_module(controller_mod)
        except ModuleNotFoundError:
            logger.debug(f"No controller module in {name}, skipping.")
            continue
        except Exception as e:
            logger.error(f"Error importing {controller_mod}: {e}")
            continue

        router = getattr(module, "router", None)
        if router is None:
            logger.warning(f"Found {controller_mod} but no 'router' attribute.")
            continue

        app.include_router(router)
        logger.info(f"✅ Auto-included router from {controller_mod} at /{name}")


# wire up everything
auto_include_routers()

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def list_routes():
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ",".join(route.methods)
            logger.info(f"🛣️  {methods:10s} -> {route.path}")
