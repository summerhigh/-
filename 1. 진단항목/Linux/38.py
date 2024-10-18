import os
import sys
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Apache 불필요한 파일 및 디렉터리 점검 함수
def check_unnecessary_files():
    # Apache 설치 경로에서 불필요한 파일/디렉터리 목록
    unnecessary_paths = [
        "/var/www/html/manual", 
        "/usr/share/doc/manual", 
        "/var/www/manual", 
        "/usr/local/apache2/htdocs/manual",
        "/etc/httpd/manual"
    ]

    try:
        # 불필요한 파일 및 디렉터리 존재 여부 점검
        for path in unnecessary_paths:
            if os.path.exists(path):
                return "취약"  # 불필요한 파일 또는 디렉터리가 존재하는 경우
        return "양호"  # 불필요한 파일 및 디렉터리가 없는 경우

    except Exception as e:
        print(f"오류 발생: {e}")
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 불필요한 파일 점검
    status = check_unnecessary_files()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "웹서비스 불필요한 파일 제거",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "38.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-38"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
