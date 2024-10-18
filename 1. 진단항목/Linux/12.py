import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# /etc/services 파일 소유자 및 권한 확인 함수 (서버별로 다르게 진단)
def check_services_file_permissions():
    file_to_check = '/etc/services'  # 점검할 파일 경로
    try:
        if os.path.exists(file_to_check):
            # 파일의 소유자 및 권한 확인
            file_stat = os.stat(file_to_check)

            # 파일 소유자 UID 확인 (root(0), bin(1), sys(3) 중 하나여야 함)
            if file_stat.st_uid not in [0, 1, 3]:
                return "취약"  # 소유자가 root, bin 또는 sys가 아닌 경우

            # 파일 권한 확인 (644 = rw-r--r--)
            file_permissions = oct(file_stat.st_mode)[-3:]
            if file_permissions > '644':
                return "취약"  # 권한이 644 이하가 아닌 경우

            return "양호"  # 소유자가 root, bin 또는 sys이고 권한이 644 이하인 경우

        return "취약"  # 파일이 존재하지 않는 경우 취약 처리
    except Exception as e:
        return "취약"  # 기타 오류 발생 시 취약 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # /etc/services 파일 소유자 및 권한 점검
    status = check_services_file_permissions()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "/etc/services 파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "12.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-12"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))