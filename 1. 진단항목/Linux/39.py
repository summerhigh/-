import os
import sys
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Apache 심볼릭 링크 사용 여부 점검 함수
def check_symbolic_link_usage():
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

            # 심볼릭 링크 설정 확인 (FollowSymLinks 옵션이 설정되어 있으면 취약)
            if 'FollowSymLinks' in content:
                return "취약"  # 심볼릭 링크가 허용된 경우
            else:
                return "양호"  # 심볼릭 링크가 제한된 경우

    except Exception as e:
        print(f"오류 발생: {e}")
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 심볼릭 링크 사용 여부 점검
    status = check_symbolic_link_usage()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "웹서비스 링크 사용금지",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "39.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-39"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
