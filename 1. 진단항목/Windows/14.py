import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# 불필요한 IIS 기본 파일 제거 여부 확인 함수
def check_iis_default_files():
    try:
        # PowerShell 명령어로 IISSamples와 IISHelp 가상 디렉토리 존재 여부 확인
        result_samples = subprocess.run(['powershell', '-Command', 
                                         '(Get-WebVirtualDirectory -Site "Default Web Site" -Name "IISSamples").PhysicalPath'], 
                                        capture_output=True, text=True)

        result_help = subprocess.run(['powershell', '-Command', 
                                      '(Get-WebVirtualDirectory -Site "Default Web Site" -Name "IISHelp").PhysicalPath'], 
                                     capture_output=True, text=True)

        # IISSamples 또는 IISHelp 디렉토리가 존재하는지 확인
        samples_status = result_samples.stdout.strip()
        help_status = result_help.stdout.strip()

        # IISSamples 또는 IISHelp 디렉토리가 존재하면 취약, 존재하지 않으면 양호
        if samples_status or help_status:
            return "취약"
        else:
            return "양호"
    
    except subprocess.CalledProcessError as e:
        # IIS 서비스가 존재하지 않는 경우 등 에러 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return "양호"  # IIS가 설치되지 않은 경우 양호로 처리
        else:
            # 그 외의 에러는 점검불가로 처리
            return "점검불가"


if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 결과 생성
    status = check_iis_default_files()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS 불필요한 파일 제거",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "14.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-14"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
