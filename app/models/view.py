from app.models import router
import importlib.resources as pkg_resources
import os

@router.get("/get_local_models")
def get_model_list():
    return list(filter(lambda x: x.endswith(".pkl") or x.endswith(".gguf"), os.listdir(pkg_resources.files("app.models"))))