import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 불필요한 계정 및 의심스러운 계정 존재 여부 확인 함수
def check_unused_accounts():
    try:
        # PowerShell 명령어로 로컬 사용자 목록 가져오기
        result = subprocess.run(['powershell', '-Command', 'Get-LocalUser'],
                                capture_output=True, text=True, check=True)
        output = result.stdout

        # 불필요한 계정 목록 추출 (Test, test, Temp가 포함된 계정 추출)
        unused_accounts = []
        for line in output.splitlines():
            parts = line.split()  # 각 줄을 공백으로 분리
            if len(parts) > 0:    # 계정 이름이 있는지 확인
                account_name = parts[0]
                # 계정 이름에 Test, test, Temp가 포함된 경우
                if 'Test' in account_name or 'test' in account_name or 'Temp' in account_name:
                    unused_accounts.append(account_name)

        account_exists = len(unused_accounts) > 0
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

    if account_exists:
        return "취약"
    else:
        return "양호"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    # check_unused_accounts 결과를 기반으로 진단 상태 결정
    status = check_unused_accounts()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정관리",
        "항목 설명": "'불필요한 계정 및 의심스러운 계정 존재 여부 확인'",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": f"{file_name}.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-03"  # 코드 고정
    }
    
    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
