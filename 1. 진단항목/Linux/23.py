import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# DoS 공격에 취약한 서비스 비활성화 여부를 점검하는 함수
def check_dos_vulnerable_services():
    try:
        # DoS 공격에 취약한 서비스 목록
        vulnerable_services = ['echo', 'discard', 'daytime', 'chargen', 'ntp', 'snmp', 'dns']

        service_active = False

        # 리눅스 및 대부분의 유닉스 시스템에서 systemctl 또는 service 명령으로 서비스 상태 확인
        for service in vulnerable_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                if 'active' in service_status.stdout:
                    service_active = True
                    break
        
        # inetd 또는 xinetd에서 서비스 설정 확인 (Solaris, AIX, HP-UX)
        if not service_active:
            inetd_check = subprocess.run(['grep', '-iE', 'echo|discard|daytime|chargen', '/etc/inetd.conf'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            xinetd_check = subprocess.run(['grep', '-iE', 'echo|discard|daytime|chargen', '/etc/xinetd.d/'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            if inetd_check.stdout or xinetd_check.stdout:
                service_active = True

        if service_active:
            return "취약"  # DoS 공격에 취약한 서비스가 활성화된 경우
        else:
            return "양호"  # DoS 공격에 취약한 서비스가 비활성화된 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # DoS 공격에 취약한 서비스 상태 점검
    status = check_dos_vulnerable_services()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "DoS 공격에 취약한 서비스 비활성화",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "23.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-23"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
