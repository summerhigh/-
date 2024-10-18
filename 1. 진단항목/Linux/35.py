import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Apache 설정 파일 경로 (기본적으로 /etc/httpd/conf/httpd.conf 또는 /etc/apache2/apache2.conf에서 점검)
APACHE_CONFIG_PATHS = ["/etc/httpd/conf/httpd.conf", "/etc/apache2/apache2.conf"]

# 웹서비스 디렉토리 리스팅 설정 점검 함수
def check_directory_listing():
    try:
        # Apache 설정 파일 경로 확인 (여러 경로 중 존재하는 파일 확인)
        config_file = None
        for path in APACHE_CONFIG_PATHS:
            if os.path.exists(path):
                config_file = path
                break

        # 설정 파일이 없는 경우 Apache 웹서버가 실행 중이지 않다고 가정
        if not config_file:
            return "양호"  # 웹 서버를 사용하지 않음

        with open(config_file, 'r') as f:
            content = f.read()

            # 디렉토리 리스팅 관련 설정 확인 (Options Indexes가 포함되어 있으면 디렉토리 리스팅이 허용된 상태)
            if 'Options Indexes' in content:
                return "취약"  # 디렉토리 리스팅이 활성화된 경우
            else:
                return "양호"  # 디렉토리 리스팅이 비활성화된 경우

    except Exception as e:
        print(f"오류 발생: {e}")
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 디렉토리 리스팅 설정 점검
    status = check_directory_listing()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "웹서비스 디렉토리 리스팅 제거",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "35.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-35"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
