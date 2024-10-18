import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Administrator 계정 확인 함수
def check_admin_account():
    try:
        # PowerShell 실행하여 Administrator 계정정보 추출
        result = subprocess.run(['powershell', '-Command',
                                  'Get-LocalUser | Where-Object {$_.Name -eq "Administrator"}'], 
                                capture_output=True, text=True, check=True)
        admin_account_exists = 'Administrator' in result.stdout
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

    if admin_account_exists:
        return "취약"
    else:
        return "양호"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # check_admin_account 결과를 기반으로 진단 상태 결정
    status = check_admin_account()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정 관리",
        "항목 설명": "Administrator 계정 이름 변경 또는 보안성 강화",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "1.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-01"  
    }
    
    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
