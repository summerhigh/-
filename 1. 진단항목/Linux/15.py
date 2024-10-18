import os
import sys
import json
from datetime import datetime
import subprocess

# World Writable 파일 점검 함수 (서버별로 다르게 진단)
def check_world_writable_files():
    try:
        # World writable 파일을 찾기 위한 명령어 실행
        result = subprocess.run(
            ['find', '/', '-xdev', '-type', 'f', '-perm', '-0002', '-ls'], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # 예외: 명령어 실행 후 반환 코드가 0이 아닐 경우 오류 처리
        if result.returncode != 0:
            return "점검불가"

        # 결과가 있으면 취약한 상태 (world writable 파일이 존재)
        if result.stdout.strip():  # 결과가 비어있지 않으면 취약
            return "취약"

        return "양호"  # World writable 파일이 존재하지 않는 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검 불가로 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # World writable 파일 점검
    status = check_world_writable_files()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "World Writable 파일 점검",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "15.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-15"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
