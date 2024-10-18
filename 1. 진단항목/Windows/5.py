import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 평문 암호 저장 여부 확인 함수
def check_clear_text_passwords():
    try:
        result = subprocess.run(['powershell', '-Command',
                                  'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Lsa" | Select-Object -ExpandProperty "StoreClearTextPasswords"'], 
                                capture_output=True, text=True, check=True)
        value = result.stdout.strip()
        if value.isdigit() and int(value) == 0:
            return "양호"
        else:
            return "취약"
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            return "양호"  # 레지스트리 값이 없으면 기본적으로 양호로 간주
        else:
            return "점검불가"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # check_clear_text_passwords 결과를 기반으로 진단 상태 결정
    status = check_clear_text_passwords()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정 관리",
        "항목 설명": "해독 가능한 암호화를 사용하여 암호 저장 해제",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "5.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-05" 
    }
    
    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
