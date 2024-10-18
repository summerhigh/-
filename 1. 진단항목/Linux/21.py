import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# r 계열 서비스 비활성화 여부를 점검하는 함수
def check_r_command_services():
    try:
        # 점검할 r 계열 서비스 목록
        r_services = ['rsh', 'rlogin', 'rexec']
        r_services_active = False

        # systemctl 또는 service 명령어로 r 서비스 상태 확인 (Linux)
        for service in r_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                if 'active' in service_status.stdout:
                    r_services_active = True
                    break
        
        # inetd 또는 xinetd에서 r 서비스 확인 (Solaris, AIX, HP-UX)
        if not r_services_active:
            inetd_check = subprocess.run(['grep', '-iE', 'rsh|rlogin|rexec', '/etc/inetd.conf'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            xinetd_check = subprocess.run(['grep', '-iE', 'rsh|rlogin|rexec', '/etc/xinetd.d/'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            if inetd_check.stdout or xinetd_check.stdout:
                r_services_active = True

        if r_services_active:
            return "취약"  # r 계열 서비스가 활성화된 경우
        else:
            return "양호"  # r 계열 서비스가 비활성화된 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 취약 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # r 계열 서비스 상태 점검
    status = check_r_command_services()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "r 계열 서비스 비활성화 여부 점검",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "21.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-21"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
