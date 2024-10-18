import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# /dev에 존재하지 않는 device 파일 점검 함수
def check_invalid_device_files():
    try:
        # /dev 디렉토리에서 major, minor number가 없는 파일 검색 (정확한 명령어로 수정)
        result = subprocess.run(
            ['find', '/dev', '-type', 'f', '!', '-type', 'b', '!', '-type', 'c', '-ls'], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # 명령어 실행 후 반환 코드가 0이 아닐 경우 오류 처리
        if result.returncode != 0:
            return "점검불가"

        # 결과가 있으면 취약한 상태 (존재하지 않는 device 파일이 있음)
        if result.stdout.strip():  # 결과가 비어있지 않으면 취약
            return "취약"

        return "양호"  # 존재하지 않는 device 파일이 없는 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검 불가로 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # /dev 디렉토리의 존재하지 않는 device 파일 점검
    status = check_invalid_device_files()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "/dev 디렉토리의 존재하지 않는 device 파일 점검",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "16.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-16"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
