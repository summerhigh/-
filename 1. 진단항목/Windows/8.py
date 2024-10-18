import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 하드디스크 기본 공유 제거 여부 확인 함수
def check_autoshare():
    try:
        # PowerShell 명령어로 레지스트리 AutoShareServer 값 확인 (0이면 양호, 1이면 취약)
        result = subprocess.run(['powershell', '-Command',
                                  'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" | Select-Object -ExpandProperty "AutoShareServer"'], 
                                capture_output=True, text=True, check=True)
        autoshare_value = int(result.stdout.strip()) if result.stdout.strip().isdigit() else None
    except subprocess.CalledProcessError:
        autoshare_value = None  # 속성이 없으면 None으로 설정

    # AutoShareServer 값이 0이면 양호, 1이면 취약, 값이 없으면 양호로 간주
    if autoshare_value == 0 or autoshare_value is None:
        return "양호"
    else:
        return "취약"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
      
    # check_autoshare 결과를 기반으로 진단 상태 결정
    status = check_autoshare()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "하드디스크 기본 공유 제거",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "8.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-08"
    }
    
    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
