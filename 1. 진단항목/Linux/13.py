import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# SUID, SGID 설정 파일 점검 함수 (서버별로 다르게 진단)
def check_suid_sgid_files():
    try:
        # SUID, SGID 설정된 파일을 찾기 위한 명령어 실행 (stderr 무시)
        result = subprocess.run(
            ['find', '/', '-perm', '-4000', '-o', '-perm', '-2000', '-type', 'f', '-ls'], 
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )

        # 결과가 있으면 취약한 상태 (SUID/SGID 설정된 파일이 존재)
        if result.stdout.strip():  # 결과가 비어있지 않으면 취약
            return "취약"

        return "양호"  # SUID/SGID 파일이 존재하지 않는 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검 불가로 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # SUID, SGID 파일 점검
    status = check_suid_sgid_files()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "SUID, SGID 설정 파일점검",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "13.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-13"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
