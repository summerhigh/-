import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# SAM 파일 접근 권한 설정 여부 확인 함수
def check_sam_permissions():
    try:
        # icacls 명령어로 SAM 파일 권한 확인
        result = subprocess.run(['icacls', 'C:\\Windows\\System32\\config\\SAM'], 
                                capture_output=True, text=True)
        output = result.stdout.lower()

        # 'administrator'와 'system'만 포함되어 있는지 확인
        # 'everyone'이나 기타 그룹이 포함되지 않은 경우 양호로 간주
        if 'nt authority\\system' in output and 'builtin\\administrators' in output and 'everyone' not in output:
            return "양호"
        else:
            return "취약"
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return "점검불가"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 결과 생성
    status = check_sam_permissions()

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "보안 관리",
        "항목 설명": "SAM 파일 접근 통제 설정",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "37.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-37" 
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
