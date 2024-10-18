import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# automountd 서비스 비활성화 여부를 점검하는 함수
def check_automountd_service():
    try:
        # automountd 서비스 상태 확인
        service_name = 'automountd'
        service_active = False

        # systemctl 또는 service 명령어로 서비스 상태 확인 (Linux)
        if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
            service_status = subprocess.run(['systemctl', 'is-active', service_name], capture_output=True, text=True)
            if 'active' in service_status.stdout:
                service_active = True

        # Solaris, AIX, HP-UX에서 automountd 상태 확인 (inetd 또는 xinetd 사용 여부 확인)
        if not service_active:
            inetd_check = subprocess.run(['grep', '-i', 'automountd', '/etc/inetd.conf'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            xinetd_check = subprocess.run(['grep', '-i', 'automountd', '/etc/xinetd.d/'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            if inetd_check.stdout or xinetd_check.stdout:
                service_active = True

        if service_active:
            return "취약"  # automountd 서비스가 활성화된 경우
        else:
            return "양호"  # automountd 서비스가 비활성화된 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # automountd 서비스 상태 점검
    status = check_automountd_service()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "automountd 서비스 비활성화 여부 점검",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "26.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-26"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
