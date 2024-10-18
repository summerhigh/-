import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 공유 디렉토리 내 Everyone 권한 존재 여부 확인 함수
def check_everyone_permission():
    try:
        # PowerShell 명령어로 공유 폴더 확인 (C$, D$, Admin$, IPC$ 제외)
        result = subprocess.run(['powershell', '-Command',
                                  r'Get-SmbShare | Where-Object {($_.Name -notmatch "C\$|D\$|Admin\$|IPC\$")}'], 
                                capture_output=True, text=True, check=True)
        shares = result.stdout.splitlines()

        # 공유 폴더가 없을 경우, '양호' 반환
        if not shares:
            return "양호"

        # 권한 확인
        result = subprocess.run(['powershell', '-Command',
                                  r'Get-SmbShare | Where-Object {($_.Name -notmatch "C\$|D\$|Admin\$|IPC\$")} | ForEach-Object { Get-SmbShareAccess -Name $_.Name }'], 
                                capture_output=True, text=True, check=True)
        share_access = result.stdout.splitlines()

        # Everyone 권한이 있는 공유 폴더 확인
        everyone_shares = [line for line in share_access if "Everyone" in line]
        
        # Everyone 권한이 있는 경우 취약, 없으면 양호
        return "취약" if everyone_shares else "양호"
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # check_everyone_permission 결과를 기반으로 진단 상태 결정
    status = check_everyone_permission()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "공유 권한 및 사용자 그룹 설정",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "7.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-07" 
    }
    
    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
