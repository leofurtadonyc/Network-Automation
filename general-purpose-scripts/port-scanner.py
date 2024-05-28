import pyfiglet
import socket
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import os

COMMON_UDP_PORTS = [53, 67, 68, 69, 123, 161, 162, 500, 514, 520, 1812, 1813, 2049, 3306, 5060, 5353, 8080]
IANA_URL = "https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.txt"

def print_banner():
    ascii_banner = pyfiglet.figlet_format("PORT SCANNER")
    print(ascii_banner)
    print("https://github.com/leofurtadonyc/Network-Automation")

def validate_args():
    parser = argparse.ArgumentParser(description="Port Scanner")
    parser.add_argument("target", help="Target IP address or hostname")
    parser.add_argument("--udp", action="store_true", help="Include UDP ports in the service discovery")
    parser.add_argument("--check-iana", action="store_true", help="Check IANA website for service names and port numbers")
    args = parser.parse_args()
    
    try:
        addr_info = socket.getaddrinfo(args.target, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
        return addr_info, args.udp, args.check_iana
    except socket.gaierror:
        print("Hostname could not be resolved")
        sys.exit()

def fetch_iana_service_names():
    try:
        response = requests.get(IANA_URL)
        response.raise_for_status()
        iana_data = response.text
        service_mapping = {}
        for line in iana_data.splitlines():
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) > 1:
                    port = parts[-1]
                    service = parts[0]
                    protocol = parts[-2]
                    if protocol in ("tcp", "udp") and port.isdigit():
                        service_mapping[(int(port), protocol)] = service
        return service_mapping
    except requests.RequestException:
        return None

def get_service_name(port, protocol, service_mapping):
    if service_mapping:
        return service_mapping.get((port, protocol), "Unknown")
    else:
        try:
            service = socket.getservbyport(port, protocol)
        except OSError:
            service = "Unknown"
        return service

def get_local_ip(target):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((target, 1))
            return s.getsockname()[0]
    except Exception:
        return "Unknown"

def scan_port(addr, port, protocol, service_mapping):
    try:
        family, socktype, proto, _, sockaddr = addr
        s = socket.socket(family, socktype, proto)
        socket.setdefaulttimeout(1)
        
        if protocol == "tcp":
            result = s.connect_ex((sockaddr[0], port))
            if result == 0:
                service = get_service_name(port, protocol, service_mapping)
                return port, service, protocol
        else:
            try:
                s.sendto(b"", (sockaddr[0], port))
                s.recvfrom(1024)
                service = get_service_name(port, protocol, service_mapping)
                return port, service, protocol
            except socket.timeout:
                return None
            except Exception:
                return None
        s.close()
    except Exception as e:
        return port, "Error: " + str(e), protocol
    return None

def scan_ports(addr_info, udp=False, check_iana=False):
    user = os.getlogin()
    target_ip = addr_info[0][4][0]
    source_ip = get_local_ip(target_ip)
    start_time = datetime.now()
    print("-" * 50)
    print(f"Scanning Target: {target_ip} from Source: {source_ip} by user: {user}")
    print("Scanning started at: " + str(start_time))
    print("-" * 50)

    service_mapping = fetch_iana_service_names() if check_iana else None

    open_ports = []
    no_response_udp_ports = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_port, addr, port, "tcp", service_mapping): port for addr in addr_info for port in range(1, 65536)}
        if udp:
            futures.update({executor.submit(scan_port, addr, port, "udp", service_mapping): port for addr in addr_info for port in COMMON_UDP_PORTS})
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                port, service, protocol = result
                if protocol == "udp" and service.startswith("Error"):
                    no_response_udp_ports.append((port, protocol, service))
                else:
                    print(f"Port {port}/{protocol} is open ({service})")
                    open_ports.append(result)

    if no_response_udp_ports:
        for port, protocol, service in no_response_udp_ports:
            print(f"Port {port}/{protocol} did not respond (possibly closed or filtered)")

    end_time = datetime.now()
    duration = end_time - start_time
    print("-" * 50)
    print(f"Scanning completed in: {duration}")
    print("-" * 50)

    return open_ports

def main():
    print_banner()
    addr_info, udp, check_iana = validate_args()
    scan_ports(addr_info, udp, check_iana)

if __name__ == "__main__":
    main()
