import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 로그 검토 및 보고 여부를 확인하는 함수
def check_log_review_and_reporting():
    try:
        # 로그 파일 목록 설정 (시스템 로그와 보안 로그)
        log_files = [
            "/var/log/syslog",  # 시스템 로그 (리눅스)
            "/var/log/auth.log",  # 인증 관련 로그 (리눅스)
            "/var/log/messages",  # 메시지 로그 (리눅스/유닉스)
            "/var/adm/messages",  # 유닉스 시스템 로그 (SOLARIS)
            "/var/log/secure"  # 보안 관련 로그 (리눅스)
        ]
        
        log_reviewed = False
        for log_file in log_files:
            if os.path.exists(log_file):
                # 최근 로그 파일 수정 시각 확인
                last_modified_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                current_time = datetime.now()

                # 최근 로그 검토 여부 확인 (7일 이내에 검토되었는지 확인)
                if (current_time - last_modified_time).days <= 7:
                    log_reviewed = True
                    break
        
        if log_reviewed:
            return "양호"  # 정기적으로 로그 검토가 이루어지는 경우
        else:
            return "취약"  # 정기적인 로그 검토가 이루어지지 않는 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 로그 검토 및 보고 여부 점검
    status = check_log_review_and_reporting()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "로그 관리",
        "항목 설명": "로그의 정기적 검토 및 보고",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "43.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-43"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
