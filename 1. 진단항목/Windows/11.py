import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# IIS 디렉토리 리스팅 설정 여부 확인 함수
def check_directory_listing():
    try:
        # PowerShell 명령어로 IIS에서 디렉토리 리스팅 설정 여부 확인
        result = subprocess.run(['powershell', '-Command', 
                                  '(Get-WebConfigurationProperty -Filter system.webServer/directoryBrowse -Name enabled).Value'], 
                                capture_output=True, text=True, check=True)
        directory_listing_status = result.stdout.strip()

        # 결과가 True이면 취약, False이면 양호
        if directory_listing_status == "True":
            return "취약"
        else:
            return "양호"
    
    except subprocess.CalledProcessError as e:
        # IIS 서비스가 존재하지 않는 경우 등 에러 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in e.stderr:
            return "양호"  # 서비스가 없으면 디렉토리 리스팅 취약점이 없으므로 양호로 간주
        else:
            # 그 외의 에러는 점검불가로 처리
            return "점검불가"


if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 결과 생성
    status = check_directory_listing()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "디렉토리 리스팅 제거",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "11.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-11"
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
