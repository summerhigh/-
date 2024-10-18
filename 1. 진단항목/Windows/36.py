import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# 백신 프로그램 설치 여부 확인 함수
def check_antivirus_installed():
    try:
        # PowerShell 명령어로 시스템에 설치된 백신 프로그램 확인
        result = subprocess.run(['powershell', '-Command',
                                  'Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct'], 
                                capture_output=True, text=True, check=True)
        antivirus_info = result.stdout.strip()
        
        # 백신 정보가 있으면 양호, 없으면 취약
        if antivirus_info:
            return "양호"
        else:
            return "취약"
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 결과 생성
    status = check_antivirus_installed()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "보안 관리",
        "항목 설명": "백신 프로그램 설치",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "36.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-36"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
