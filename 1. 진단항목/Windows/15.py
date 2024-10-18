import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# 웹 프로세스 권한 제한 설정 여부 확인 함수
def check_web_process_permissions():
    try:
        # PowerShell 명령어로 IIS Application Pool의 Identity 설정 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-WebConfigurationProperty -Filter system.applicationHost/applicationPools/add -Name processModel.identityType'], 
                                capture_output=True, text=True, check=True)
        
        identity_type = result.stdout.strip()

        # Identity 설정이 ApplicationPoolIdentity나 최소 권한 계정인 경우 양호, 그렇지 않으면 취약
        if "ApplicationPoolIdentity" in identity_type or "NetworkService" in identity_type or "LocalService" in identity_type:
            return "양호"
        else:
            return "취약"

    except subprocess.CalledProcessError as e:
        # IIS 서비스가 존재하지 않는 경우 등 에러 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return "양호"  # IIS가 설치되지 않은 경우 양호로 처리
        else:
            return "점검불가"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 결과 생성
    status = check_web_process_permissions()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS 웹 프로세스 권한 제한",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "15.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-15" 
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
