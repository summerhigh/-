import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# 접속 IP 및 포트 제한 설정 여부를 점검하는 함수
def check_ip_port_restrictions():
    try:
        # TCP Wrapper 설정 파일 (/etc/hosts.allow, /etc/hosts.deny) 점검
        tcp_wrapper_files = ['/etc/hosts.allow', '/etc/hosts.deny']
        tcp_wrapper_configured = False

        for file in tcp_wrapper_files:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    content = f.read().strip()
                    if content and '+' not in content:  # 설정이 있고, 모든 호스트 허용(+) 설정이 아닌 경우
                        tcp_wrapper_configured = True

        # iptables 명령이 있는지 확인
        if subprocess.run(['which', 'iptables'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
            return "점검불가"  # iptables 명령어가 없는 경우

        # iptables 규칙 확인 (리눅스 커널 방화벽)
        iptables_check = subprocess.run(['iptables', '-L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        iptables_configured = iptables_check.returncode == 0 and 'ACCEPT' in iptables_check.stdout

        # IPFilter, 다른 방화벽 설정 확인 (솔라리스, AIX 등, 리눅스가 아닌 경우에만 확인)
        ipfilter_configured = False
        if not os.path.exists('/etc/debian_version'):  # Linux(Debian 계열이 아닌 경우만 ipfstat 점검
            try:
                ipfilter_check = subprocess.run(['ipfstat', '-io'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                ipfilter_configured = ipfilter_check.returncode == 0 and ipfilter_check.stdout.strip() != ''
            except FileNotFoundError:
                return "점검불가"

        # 각 조건을 만족하는지 여부 확인
        if tcp_wrapper_configured or iptables_configured or ipfilter_configured:
            return "양호"  # 접속 IP 및 포트 제한 설정이 되어 있는 경우

        return "취약"  # 접속 IP 및 포트 제한 설정이 없는 경우
    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검 불가로 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 접속 IP 및 포트 제한 설정 여부 점검
    status = check_ip_port_restrictions()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "접속 IP 및 포트 제한",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "18.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-18"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
