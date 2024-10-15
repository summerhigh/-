import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 관리자 그룹에 불필요한 사용자가 포함되어 있는지 점검하는 함수
def check_admin_group_members():
    try:
        result = subprocess.run(['powershell', '-Command',
                                  'Get-LocalGroupMember -Group "Administrators" | Select-Object -ExpandProperty Name'], 
                                capture_output=True, text=True, check=True)
        admin_group_members = result.stdout.splitlines()

        # Administrator와 kisia 계정을 관리자 그룹의 필요사용자로 지정
        unnecessary_accounts = [member for member in admin_group_members if "Administrator" not in member and "kisia" not in member]
        has_unnecessary_accounts = len(unnecessary_accounts) > 0
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

    if has_unnecessary_accounts:
        return "취약"
    else:
        return "양호"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    # check_admin_group_members 결과를 기반으로 진단 상태 결정
    status = check_admin_group_members()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정관리",
        "항목 설명": "'관리자 그룹에 최소한의 사용자 포함 여부 확인'",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": f"{file_name}.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-06"  # 코드 고정
    }
    
    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
