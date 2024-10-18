import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# root 계정의 PATH 환경변수에서 "."의 위치 확인 함수 (서버별로 다르게 진단)
def check_root_path_variable():
    try:
        # 첫 번째 시도: os.environ에서 root 계정의 PATH 환경변수 가져오기
        root_path = os.environ.get('PATH')

        if not root_path:
            # 두 번째 시도: 유닉스 시스템에서 `echo $PATH` 명령어로 PATH 환경변수 확인
            result = subprocess.run(['echo', '$PATH'], capture_output=True, text=True)
            root_path = result.stdout.strip()

        if not root_path:
            return "점검불가"  # PATH 환경변수가 없는 경우

        # PATH를 콜론(:)으로 구분하여 리스트로 변환
        path_elements = root_path.split(':')

        # PATH의 각 요소를 확인하여 "."이 맨 앞이나 중간에 있는지 점검
        if '.' in path_elements and path_elements.index('.') != len(path_elements) - 1:
            return "취약"  # "."이 PATH의 맨 앞이나 중간에 포함된 경우
        else:
            return "양호"  # "."이 없거나, PATH의 마지막에만 있는 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # root 계정의 PATH 환경변수 점검
    status = check_root_path_variable()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "파일 및 디렉터리 관리",
        "항목 설명": "root홈, 패스 디렉터리 권한 및 패스 설정",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "5.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-05" 
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
