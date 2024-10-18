import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# /etc/(x)inetd.conf 파일 소유자 및 권한 확인 함수 (서버별로 다르게 진단)
def check_inetd_conf_permissions():
    files_to_check = ['/etc/inetd.conf', '/etc/xinetd.conf']  # 점검할 파일 목록
    try:
        for file_path in files_to_check:
            if os.path.exists(file_path):
                # 첫 번째 시도: /etc/(x)inetd.conf 파일의 소유자 및 권한 확인
                file_stat = os.stat(file_path)

                # 파일 소유자 UID가 root(0)인지 확인
                if file_stat.st_uid != 0:
                    return "취약"  # 파일 소유자가 root가 아닌 경우

                # 파일 권한 확인 (600 = rw-------)
                file_permissions = oct(file_stat.st_mode)[-3:]
                if file_permissions != '600':
                    return "취약"  # 권한이 600이 아닌 경우

                return "양호"  # 소유자가 root이고 권한이 600인 경우

        return "점검불가"  # 파일이 존재하지 않는 경우
    except Exception as e:
        return "점검불가"  

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # /etc/(x)inetd.conf 파일 소유자 및 권한 점검
    status = check_inetd_conf_permissions()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "/etc/(x)inetd.conf 파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "10.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-10"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
