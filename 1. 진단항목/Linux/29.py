import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# tftp, talk, ntalk 서비스 비활성화 여부를 점검하는 함수
def check_tftp_talk_services():
    try:
        # 점검할 서비스 목록
        services = ['tftp', 'talk', 'ntalk']
        service_active = False

        # 리눅스 및 유닉스 시스템에서 systemctl 또는 service 명령을 사용해 서비스 상태 확인
        for service in services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                if 'active' in service_status.stdout:
                    service_active = True
                    break

        # inetd 또는 xinetd에서 서비스 상태 확인 (Solaris, AIX, HP-UX)
        if not service_active:
            inetd_check = subprocess.run(['grep', '-iE', 'tftp|talk|ntalk', '/etc/inetd.conf'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            xinetd_check = subprocess.run(['grep', '-iE', 'tftp|talk|ntalk', '/etc/xinetd.d/'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            if inetd_check.stdout or xinetd_check.stdout:
                service_active = True

        if service_active:
            return "취약"  # tftp, talk, ntalk 서비스가 활성화된 경우
        else:
            return "양호"  # tftp, talk, ntalk 서비스가 비활성화된 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # tftp, talk, ntalk 서비스 상태 점검
    status = check_tftp_talk_services()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "tftp, talk, ntalk 서비스 비활성화",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "29.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-29"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
