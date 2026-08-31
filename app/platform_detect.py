import platform

def get_platform_info():
    system = platform.system().lower()
    release = platform.release()
    version = platform.version()
    architecture = platform.machine()
    hostname = platform.node()
    
    return {
        "os": system, # 'windows', 'linux', 'darwin'
        "release": release,
        "version": version,
        "architecture": architecture,
        "hostname": hostname
    }
