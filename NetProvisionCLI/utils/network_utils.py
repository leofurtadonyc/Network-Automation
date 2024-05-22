import socket
import getpass

def get_current_user() -> str:
    """Retrieve the current user's username for audit logging."""
    return getpass.getuser()

def get_ip_address() -> str:
    """Retrieve the IP address of the current machine for audit logging."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        return s.getsockname()[0]
    except Exception:
        return 'N/A'
    finally:
        s.close()
