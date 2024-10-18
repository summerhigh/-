import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 패스워드 파일 보호 상태 확인 함수
def check_password_file_protection():
    try:
        # /etc/passwd 파일에서 확인
        with open('/etc/passwd', 'r') as passwd_file:
            passwd_content = passwd_file.read()

            # 패스워드가 평문으로 저장되어 있는지 확인
            if 'x' not in passwd_content:
                return "취약"  # 패스워드가 암호화되지 않고 저장된 경우

        # /etc/shadow 파일에서 패스워드 암호화 여부 확인
        with open('/etc/shadow', 'r') as shadow_file:
            shadow_content = shadow_file.read()

            # 패스워드가 암호화되어 있는지 확인
            if any(['!' in line.split(':')[1] or '*' in line.split(':')[1] for line in shadow_content.splitlines()]):
                return "양호"  # 패스워드가 암호화되어 있는 경우
            else:
                return "취약"  # 암호화되지 않은 경우

    except FileNotFoundError:
        return "점검불가"  # 파일이 없는 경우
    except Exception as e:
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 패스워드 파일 보호 상태 점검
    status = check_password_file_protection()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정 관리",
        "항목 설명": "패스워드 파일 보호",
        "중요도": "상",
        "진단 결과": status,  
        "진단 파일명": "4.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-04" 
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
