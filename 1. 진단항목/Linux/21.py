import os
import sys
import json
from datetime import datetime
import subprocess

# r 계열 서비스 비활성화 여부를 점검하는 함수
def check_r_command_services():
    try:
        # 점검할 r 계열 서비스 목록
        r_services = ['rsh', 'rlogin', 'rexec']
        r_services_active = False
        services_exist = False

        # systemctl 또는 service 명령어로 r 서비스 상태 확인 (Linux)
        for service in r_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if service_status.returncode == 0:  # 서비스가 존재하고 있는 경우
                    services_exist = True
                    if 'active' in service_status.stdout:
                        r_services_active = True
                        break
                else:
                    print(f"Service {service} not found or inactive.")  # Debugging information
        
        # inetd 또는 xinetd에서 r 서비스 확인 (Solaris, AIX, HP-UX)
        if not r_services_active:
            inetd_check = subprocess.run(['grep', '-iE', 'rsh|rlogin|rexec', '/etc/inetd.conf'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            xinetd_check = subprocess.run(['grep', '-iE', 'rsh|rlogin|rexec', '/etc/xinetd.d/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if inetd_check.returncode == 0 or xinetd_check.returncode == 0:
                services_exist = True
                r_services_active = True
            else:
                print(f"inetd or xinetd services not found.")  # Debugging information

        # r 계열 서비스가 아예 존재하지 않으면 양호로 처리
        if not services_exist:
            return "양호", "r 계열 서비스가 시스템에 존재하지 않습니다."

        # r 계열 서비스가 존재하고 활성화된 경우 취약으로 처리
        if r_services_active:
            return "취약", "r 계열 서비스가 활성화되어 있습니다."
        else:
            return "양호", "r 계열 서비스가 비활성화되어 있습니다."

    except Exception as e:
        return "점검불가", f"r 계열 서비스 점검 중 오류가 발생했습니다: {str(e)}"

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # r 계열 서비스 상태 점검
    status, message = check_r_command_services()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "r 계열 서비스 비활성화 여부 점검",
        "중요도": "상",
        "진단 결과": status,
        "메시지": message,
        "진단 파일명": "21.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-21"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
