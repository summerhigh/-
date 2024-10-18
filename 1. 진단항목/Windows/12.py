import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# CGI 디렉토리 권한 설정 여부 확인 함수
def check_cgi_directory_permissions():
    try:
        # PowerShell 명령어로 inetpub/scripts 디렉토리의 권한을 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-Acl "C:\\inetpub\\scripts" | Select-Object -ExpandProperty Access'], 
                                capture_output=True, text=True)
        permissions = result.stdout.strip()

        # 'Everyone'에 수정 권한 또는 모든 권한이 있는지 확인
        if "Everyone" in permissions and ("Modify" in permissions or "FullControl" in permissions or "Write" in permissions):
            return "취약"
        else:
            return "양호"
    
    except subprocess.CalledProcessError as e:
        # 디렉토리가 존재하지 않는 경우 처리
        if "ItemNotFoundException" in str(e) or "경로는 존재하지 않으므로 찾을 수 없습니다." in str(e):
            return "양호"  # 경로가 존재하지 않으면 취약점이 없으므로 양호로 간주
        else:
            # 그 외의 에러는 점검불가로 처리
            return "점검불가"


if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 결과 생성
    status = check_cgi_directory_permissions()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS CGI 실행 제한",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "12.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-12"  # 코드 생성
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
