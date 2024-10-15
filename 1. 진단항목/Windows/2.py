import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Guest 계정 비활성화 여부 확인 함수
def check_guest_account():
    try:
        result = subprocess.run(['powershell', '-Command',
                                '(Get-LocalUser | Where-Object {$_.Name -eq "Guest"}).Enabled'], 
                                capture_output=True, text=True, check=True)
        guest_account_enabled = 'True' in result.stdout
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

    if guest_account_enabled:
        return "취약"
    else:
        return "양호"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    # check_guest_account 결과를 기반으로 진단 상태 결정
    status = check_guest_account()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정관리",
        "항목 설명": "'Guest 계정 비활성화 여부 확인'",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": f"{file_name}.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-02" 
    }
    
    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
