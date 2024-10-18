import os
import sys
import json
from datetime import datetime
import pwd
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 환경 변수 파일 목록
env_files = [".profile", ".kshrc", ".cshrc", ".bashrc", ".bash_profile", ".login", ".exrc", ".netrc"]

# 사용자, 시스템 시작 파일 및 환경 파일의 소유자 및 권한 점검 함수
def check_env_file_permissions():
    try:
        # 모든 사용자의 홈 디렉터리 확인
        users = pwd.getpwall()
        for user in users:
            home_dir = user.pw_dir
            if os.path.isdir(home_dir):
                # 홈 디렉터리 내의 환경변수 파일들 확인
                for env_file in env_files:
                    file_path = os.path.join(home_dir, env_file)
                    if os.path.exists(file_path):
                        file_stat = os.stat(file_path)

                        # 파일 소유자가 root 또는 해당 계정이어야 함
                        if file_stat.st_uid != 0 and file_stat.st_uid != user.pw_uid:
                            return "취약"  # 소유자가 root 또는 해당 계정이 아닌 경우

                        # 파일 권한 확인 (쓰기 권한이 root와 소유자에게만 있어야 함)
                        file_permissions = oct(file_stat.st_mode)[-3:]
                        if file_permissions[1] != '0' or file_permissions[2] != '0':
                            return "취약"  # 다른 사용자에게 쓰기 권한이 있는 경우

        return "양호"  # 모든 환경 변수 파일이 적절히 설정된 경우
    except Exception as e:
        return "점검불가"  # 오류 발생 시 취약 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 사용자 및 환경 파일 소유자 및 권한 점검
    status = check_env_file_permissions()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "14.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-14"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
