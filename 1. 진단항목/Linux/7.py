import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# /etc/passwd 파일 소유자 및 권한 확인 함수 (서버별로 다르게 진단)
def check_passwd_file_permissions():
    try:
        # 첫 번째 시도: /etc/passwd 파일의 소유자 및 권한 확인 (리눅스 및 대부분의 유닉스)
        passwd_stat = os.stat('/etc/passwd')

        # 파일 소유자 UID가 root(0)인지 확인
        if passwd_stat.st_uid != 0:
            return "취약"  # 파일 소유자가 root가 아닌 경우

        # 파일 권한 확인 (644 = rw-r--r--)
        file_permissions = oct(passwd_stat.st_mode)[-3:]
        if file_permissions != '644':
            return "취약"  # 권한이 644가 아닌 경우

        return "양호"  # 소유자가 root이고 권한이 644인 경우

    except FileNotFoundError:
        try:
            # 두 번째 시도: AIX 또는 다른 시스템에서 /etc/passwd 파일 경로 확인
            result = subprocess.run(['ls', '-l', '/etc/passwd'], capture_output=True, text=True)
            if 'root' not in result.stdout or 'rw-r--r--' not in result.stdout:
                return "취약"  # AIX에서 root 소유자 및 권한이 644가 아닌 경우
            return "양호"
        except Exception as e:
            return "점검불가"  # AIX에서 오류 발생 시

    except Exception as e:
        return "점검불가"  # 기타 오류 발생 시

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