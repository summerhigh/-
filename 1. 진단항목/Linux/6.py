import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 소유자가 없는 파일 및 디렉터리 확인 함수
def check_orphaned_files():
    try:
        # 소유자가 없는 파일을 찾기 위한 명령어 실행 (UID가 없는 파일 찾기)
        result = subprocess.run(['find', '/', '-nouser', '-o', '-nogroup'], capture_output=True, text=True)

        # 명령어 실행 결과 확인
        if result.returncode == 0 and result.stdout:
            # 소유자가 없는 파일 및 디렉터리 목록이 있는 경우 취약으로 처리
            return "취약"  # 취약
        else:
            # 소유자가 없는 파일 및 디렉터리가 없는 경우 양호로 처리
            return "양호"  # 양호
    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 상태 반환

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 소유자가 없는 파일 및 디렉터리 점검
    status = check_orphaned_files()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "파일 및 디렉터리 소유자 설정",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "6.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-06"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
