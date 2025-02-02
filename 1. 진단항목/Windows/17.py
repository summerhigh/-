import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# IIS 파일 업로드 및 다운로드 제한 설정 여부 확인 함수
def check_file_upload_download_limits():
    try:
        # PowerShell 명령어로 IIS에서 파일 업로드/다운로드 제한 설정 여부 확인
        result = subprocess.run(['powershell', '-Command', 
                                  '(Get-WebConfigurationProperty -Filter system.webServer/security/requestLimits -Name maxAllowedContentLength).Value'], 
                                capture_output=True, text=True, check=True)
        
        upload_download_limit = result.stdout.strip()

        # 파일 업로드 및 다운로드 용량 제한이 설정되어 있으면 양호, 설정되지 않은 경우 취약
        if upload_download_limit and int(upload_download_limit) > 0:
            return "양호"
        else:
            return "취약"

    except subprocess.CalledProcessError as e:
        # IIS 서비스가 설치되지 않았거나 다른 에러 발생 시 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return "양호"  # IIS가 설치되지 않은 경우 양호로 처리
        else:
            return "점검불가"


if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 결과 생성
    status = check_file_upload_download_limits()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS 파일 업로드 및 다운로드 제한",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "17.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-17" 
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
