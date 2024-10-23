import os
import sys
import subprocess
import json
from datetime import datetime

# /etc/services 파일 소유자 및 권한 조치 함수
def remediate_services_file_permissions():
    file_to_fix = '/etc/services'  # 조치할 파일 경로
    try:
        if os.path.exists(file_to_fix):
            # 파일 소유자를 root로 설정
            subprocess.run(['chown', 'root', file_to_fix], check=False)

            # 파일 권한을 644로 설정
            subprocess.run(['chmod', '644', file_to_fix], check=False)

        return "완료"
    except Exception as e:
        return "미완료"

# /etc/services 파일 소유자 및 권한 확인 함수 (재진단)
def check_services_file_permissions():
    file_to_check = '/etc/services'  # 점검할 파일 경로
    try:
        if os.path.exists(file_to_check):
            # 파일의 소유자 및 권한 확인
            file_stat = os.stat(file_to_check)

            # 파일 소유자 UID 확인 (root(0), bin(1), sys(3) 중 하나여야 함)
            if file_stat.st_uid not in [0, 1, 3]:
                return {"status": "취약", "message": f"{file_to_check}의 소유자가 root, bin 또는 sys가 아닙니다."}

            # 파일 권한 확인 (644 = rw-r--r--)
            file_permissions = oct(file_stat.st_mode)[-3:]
            if file_permissions > '644':
                return {"status": "취약", "message": f"{file_to_check}의 권한이 644 이하가 아닙니다."}

            return {"status": "양호", "message": f"{file_to_check}의 소유자와 권한이 적절합니다."}

        return {"status": "점검불가", "message": "파일이 존재하지 않습니다."}
    except Exception as e:
        return {"status": "점검불가", "message": "파일을 확인하는 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_services_file_permissions()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_services_file_permissions()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "/etc/services 파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "12.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-12"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
