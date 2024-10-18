import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# 백신 최신 업데이트 여부 확인 함수
def check_antivirus_update():
    try:
        # PowerShell 명령어로 Windows Defender의 최신 업데이트 확인
        result = subprocess.run(['powershell', '-Command',
                                  'Get-MpComputerStatus | Select-Object -ExpandProperty AntivirusSignatureLastUpdated'], 
                                capture_output=True, text=True, check=True)
        last_update = result.stdout.strip()
        
        if last_update:  # 업데이트 정보가 있으면 양호
            return "양호"
        else:
            return "취약"  # 업데이트 정보가 없거나 문제가 있을 경우 취약
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 결과 생성
    status = check_antivirus_update()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "패치 관리",
        "항목 설명": "백신 프로그램 업데이트",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "33.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-33"
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
