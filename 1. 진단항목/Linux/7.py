import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# /etc/passwd 파일 소유자 및 권한 확인 함수
def check_passwd_file_permissions():
    try:
        # /etc/passwd 파일의 소유자 확인
        passwd_stat = os.stat('/etc/passwd')

        # 파일 소유자 UID가 root(0)인지 확인
        if passwd_stat.st_uid != 0:
            return "취약"  # 파일 소유자가 root가 아닌 경우

        # 파일 권한 확인 (644 = rw-r--r--)
        file_permissions = oct(passwd_stat.st_mode)[-3:]
        if file_permissions != '644':
            return "취약"  # 권한이 644가 아닌 경우

        return "양호"  # 소유자가 root이고 권한이 644인 경우
    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 상태 반환

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # /etc/passwd 파일 소유자 및 권한 점검
    status = check_passwd_file_permissions()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "/etc/passwd 파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "7.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-07"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
