import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# IIS 서비스 상태 확인 함수
def check_iis_service():
    try:
        # PowerShell 명령어로 IIS 서비스(W3SVC) 상태 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-Service -Name W3SVC | Select-Object -ExpandProperty Status'], 
                                capture_output=True, text=True, check=True)
        service_status = result.stdout.strip()

        # 서비스가 'Running' 상태이면 취약, 그렇지 않으면 양호
        if service_status == "Running":
            return "취약"
        else:
            return "양호"
    
    except subprocess.CalledProcessError as e:
        # 서비스가 존재하지 않는 경우 (서비스를 찾을 수 없을 때)
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in e.stderr:
            return "양호"
        else:
            # 그 외의 에러는 점검불가로 처리
            return "점검불가"

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 결과 생성
    status = check_iis_service()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS 서비스 구동 점검",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "10.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-10"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
