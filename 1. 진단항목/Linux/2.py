import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 패스워드 복잡성 설정 여부 확인 함수
def check_password_complexity():
    try:
        # /etc/security/pwquality.conf 파일에서 패스워드 복잡성 관련 설정 확인
        result = subprocess.run(['grep', 'minlen', '/etc/security/pwquality.conf'], capture_output=True, text=True, check=True)
        minlen = int(result.stdout.split('=')[-1].strip()) if result.stdout else 0
        
        # /etc/login.defs 파일에서 PASS_MIN_LEN 설정 확인 (대체 경로에서 확인하는 경우)
        if minlen == 0:
            result = subprocess.run(['grep', 'PASS_MIN_LEN', '/etc/login.defs'], capture_output=True, text=True, check=True)
            minlen = int(result.stdout.split()[-1]) if result.stdout else 0

        # 패스워드 복잡성 관련 설정 확인
        if minlen >= 8:
            return "양호"  # 최소 8자 이상의 길이 설정 확인
        else:
            return "취약"  # 패스워드 길이가 8자 이하인 경우
    except subprocess.CalledProcessError:
        return "점검불가"  # 파일이나 명령어 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 패스워드 복잡성 설정 점검
    status = check_password_complexity()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정 관리",
        "항목 설명": "패스워드 복잡성 설정",
        "중요도": "상",
        "진단 결과": status,  
        "진단 파일명": "2.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-02"
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))