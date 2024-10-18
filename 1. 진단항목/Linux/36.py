import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Apache 프로세스 권한 제한 여부 점검 함수
def check_apache_process_permission():
    try:
        # ps 명령어를 사용하여 Apache 프로세스 확인
        result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
        
        # 'httpd' 또는 'apache2'로 실행 중인 프로세스에서 root 권한을 사용하는지 확인
        if 'apache2' in result.stdout or 'httpd' in result.stdout:
            for line in result.stdout.splitlines():
                if 'apache2' in line or 'httpd' in line:
                    # 프로세스 소유자 확인 (root로 실행된 경우 취약)
                    if 'root' in line.split():
                        return "취약"  # root 권한으로 실행된 경우
            return "양호"  # root가 아닌 다른 사용자 권한으로 실행된 경우
        else:
            return "양호"  # Apache가 실행되지 않으면 양호로 처리

    except Exception as e:
        print(f"오류 발생: {e}")
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # Apache 프로세스 권한 제한 여부 점검
    status = check_apache_process_permission()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "웹서비스 웹 프로세스 권한 제한",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "36.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-36"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
