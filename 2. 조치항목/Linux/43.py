import os
import sys
import json
from datetime import datetime
import subprocess

# 로그 검토 및 보고 함수
def remediate_log_review_and_reporting():
    try:
        # 로그 파일 목록 설정 (시스템 로그와 보안 로그)
        log_files = [
            "/var/log/syslog",  # 시스템 로그 (리눅스)
            "/var/log/auth.log",  # 인증 관련 로그 (리눅스)
            "/var/log/messages",  # 메시지 로그 (리눅스/유닉스)
            "/var/adm/messages",  # 유닉스 시스템 로그 (SOLARIS)
            "/var/log/secure"  # 보안 관련 로그 (리눅스)
        ]
        
        # 로그 파일 검토 및 리포트 작성 경로 설정
        report_file = "/var/log/log_review_report.txt"
        
        with open(report_file, 'w') as report:
            for log_file in log_files:
                if os.path.exists(log_file):
                    # 로그 파일 읽기
                    with open(log_file, 'r') as f:
                        log_content = f.read()
                        report.write(f"\n--- {log_file} 로그 ---\n")
                        report.write(log_content)
        
        return "완료"

    except Exception as e:
        return "미완료"

# 로그 검토 및 보고 여부를 점검하는 함수 (재진단)
def check_log_review_and_reporting():
    try:
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
            return "양호"
        else:
            return "취약"

    except Exception as e:
        return "점검불가"

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_log_review_and_reporting()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_log_review_and_reporting()

    # 최종 출력
    account_result = {
        "카테고리": "로그 관리",
        "항목 설명": "로그의 정기적 검토 및 보고",
        "중요도": "상",
        "진단 결과": diagnosis_result,
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result,
        "조치 파일명": "43.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-43"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
