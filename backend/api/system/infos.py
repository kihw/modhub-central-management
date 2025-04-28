import psutil

def get_system_info():
    return {
        "cpu_count": psutil.cpu_count(),
        "total_memory": psutil.virtual_memory().total,
        "total_disk": psutil.disk_usage('/').total
    }

def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def get_resource_usage():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
