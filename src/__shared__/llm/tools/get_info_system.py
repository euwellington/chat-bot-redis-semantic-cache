from langchain.tools import tool
import platform
import socket
import os
import psutil


@tool(return_direct=False)
def get_info_system() -> dict:
    """
        Você retorna dados do computador
    """
    return {
        "system": platform.system(),
        "system_version": platform.version(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "memory_total_gb": round(
            psutil.virtual_memory().total / (1024 ** 3),
            2
        ),
        "memory_available_gb": round(
            psutil.virtual_memory().available / (1024 ** 3),
            2
        ),
        "disk_total_gb": round(
            psutil.disk_usage("/").total / (1024 ** 3),
            2
        ),
        "disk_free_gb": round(
            psutil.disk_usage("/").free / (1024 ** 3),
            2
        ),
        "python_version": platform.python_version(),
        "current_user": os.getenv("USER")
    }