import os
import sys
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Apache 상위 디렉토리 접근 금지 설정 여부 점검 함수
def check_directory_traversal_protection():
    try:
        # Apache 설정 파일 경로 확인
        apache_config_paths = ["/etc/httpd/conf/httpd.conf", "/etc/apache2/apache2.conf"]

        config_file = None
        for path in apache_config_paths:
            if os.path.exists(path):
                config_file = path
                break

        # 설정 파일이 없는 경우 Apache가 설치되지 않은 것으로 간주
        if not config_file:
            return "양호"  # 웹서버 미사용

        with open(config_file, 'r') as f:
            content = f.read()

            # AllowOverride 설정 확인 (None이면 취약, AuthConfig 또는 All이면 양호)
            if 'AllowOverride None' in content:
                return "취약"  # 상위 디렉토리 이동이 가능함
            elif 'AllowOverride AuthConfig' in content or 'AllowOverride All' in content:
                return "양호"  # 상위 디렉토리 이동이 제한됨
            else:
                return "취약"  # 명시적인 설정이 없으면 취약

    except Exception as e:
        print(f"오류 발생: {e}")
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 상위 디렉토리 접근 금지 여부 점검
    status = check_directory_traversal_protection()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "웹서비스 상위 디렉토리 접근 금지",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "37.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-37"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
