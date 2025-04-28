from fastapi import APIRouter
from api.system.infos import get_system_info, get_running_processes, get_resource_usage

router = APIRouter()

@router.get("/info")
async def system_info():
    """Retourne les informations système"""
    return get_system_info()

@router.get("/processes")
async def running_processes():
    """Retourne la liste des processus actifs"""
    return get_running_processes()

@router.get("/resources")
async def resource_usage():
    """Retourne l'utilisation CPU/Mémoire"""
    return get_resource_usage()
