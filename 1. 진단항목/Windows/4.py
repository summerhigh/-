import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 계정 잠금 임계값 설정 여부 확인 함수
def check_account_lockout_threshold():
    try:
        result = subprocess.run(['net', 'accounts'], capture_output=True, text=True, check=True)
        output = result.stdout.lower()

        # '잠금 임계값' 값을 찾기 위한 문자열 검색
        for line in output.splitlines():
            if '잠금 임계값' in line or 'lockout threshold' in line:
                threshold_value = int(line.split()[-1])  # 마지막 값이 임계값 숫자임
                break
        else:
            threshold_value = None  # 임계값을 찾지 못한 경우
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

    # 임계값이 5 이하이면 양호, 6 이상이면 취약
    if threshold_value is not None and threshold_value <= 5:
        return "양호"
    else:
        return "취약"

if __name__ == "__main__":    
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # check_account_lockout_threshold 결과를 기반으로 진단 상태 결정
    status = check_account_lockout_threshold()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정 관리",
        "항목 설명": "계정 잠금 임계값 설정",
        "중요도": "상",
        "진단 결과": status,
        "진단 파일명": "4.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "W-04" 
    }
    
    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
