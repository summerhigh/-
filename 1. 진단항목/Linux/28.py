import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# NIS 및 NIS+ 서비스 비활성화 여부를 점검하는 함수
def check_nis_services():
    try:
        # NIS 및 NIS+ 관련 서비스 목록
        nis_services = ['ypserv', 'ypbind', 'yppasswdd', 'ypxfrd', 'rpc.yppasswdd', 'nisd']
        nis_active = False
        nis_plus_active = False

        # 리눅스 및 유닉스 시스템에서 NIS 관련 서비스 상태 확인 (systemctl 또는 service 명령)
        for service in nis_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                if 'active' in service_status.stdout:
                    nis_active = True

        # NIS+가 활성화되었는지 확인 (NIS+가 활성화된 경우 안전)
        nis_plus_status = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
        if 'nisd' in nis_plus_status.stdout:
            nis_plus_active = True

        if nis_active and not nis_plus_active:
            return "취약"  # NIS 서비스가 활성화되고, NIS+가 활성화되지 않은 경우
        else:
            return "양호"  # NIS 서비스가 비활성화되었거나, NIS+가 활성화된 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # NIS 및 NIS+ 서비스 상태 점검
    status = check_nis_services()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "NIS, NIS+ 점검",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "28.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-28"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
