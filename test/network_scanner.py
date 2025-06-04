# network_scanner.py
import socket
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_hostname_by_ip(ip_address):
    """
    주어진 IP 주소에 대한 호스트 이름을 가져옵니다.
    """
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        logging.info(f"Resolved IP {ip_address} to hostname: {hostname}")
        return hostname
    except socket.herror as e:
        logging.warning(f"Could not resolve hostname for IP {ip_address}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while resolving IP {ip_address}: {e}")
        return None

def get_ip_by_hostname(hostname):
    """
    주어진 호스트 이름에 대한 IP 주소를 가져옵니다.
    """
    try:
        ip_address = socket.gethostbyname(hostname)
        logging.info(f"Resolved hostname {hostname} to IP: {ip_address}")
        return ip_address
    except socket.gaierror as e:
        logging.warning(f"Could not resolve IP for hostname {hostname}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while resolving hostname {hostname}: {e}")
        return None

def check_port_open(host, port, timeout=1):
    """
    주어진 호스트의 특정 포트가 열려 있는지 확인합니다.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            logging.info(f"Port {port} on {host} is OPEN.")
            return True
        else:
            logging.info(f"Port {port} on {host} is CLOSED or filtered. Error code: {result}")
            return False
    except socket.error as e:
        logging.error(f"Socket error while checking port {port} on {host}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking port {port} on {host}: {e}")
        return False

# 예시 사용
if __name__ == "__main__":
    # 호스트 이름으로 IP 얻기
    google_ip = get_ip_by_hostname("www.google.com")
    if google_ip:
        print(f"Google's IP: {google_ip}")

    # IP로 호스트 이름 얻기 (역방향 DNS 조회)
    # 로컬 네트워크나 공용 IP에 따라 결과가 없을 수 있습니다.
    local_ip = "127.0.0.1" # 로컬 호스트
    local_hostname = get_hostname_by_ip(local_ip)
    if local_hostname:
        print(f"Hostname for {local_ip}: {local_hostname}")

    # 포트 열림 여부 확인
    print("\nChecking common ports:")
    target_host = "google.com" # 또는 "172.217.17.14" 같은 IP 주소
    print(f"Checking {target_host}:")
    print(f"Port 80 (HTTP) open: {check_port_open(target_host, 80)}")
    print(f"Port 443 (HTTPS) open: {check_port_open(target_host, 443)}")
    print(f"Port 22 (SSH) open: {check_port_open(target_host, 22)}")
    print(f"Port 8080 (Custom) open: {check_port_open(target_host, 8080)}")
