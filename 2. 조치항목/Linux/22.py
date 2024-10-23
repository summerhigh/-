import os
import sys
import subprocess
import json
from datetime import datetime

# crond 파일 소유자 및 권한 설정 조치 함수
def remediate_cron_permissions():
    try:
        # 점검할 cron 관련 파일 목록
        cron_files = {
            '/usr/bin/crontab': '750',
            '/etc/cron.allow': '640',
            '/etc/cron.deny': '640',
            '/etc/crontab': '640',
            '/var/spool/cron': '640',
            '/etc/cron.d': '640'
        }

        for file, permission in cron_files.items():
            if os.path.exists(file):
                # 소유자를 root로 설정
                subprocess.run(['chown', 'root', file], check=False)
                # 파일 권한을 지정된 값으로 설정
                subprocess.run(['chmod', permission, file], check=False)

        return "완료", "crond 관련 파일 소유자 및 권한이 적절히 설정되었습니다."
    except Exception as e:
        return "미완료", f"crond 파일 소유자 및 권한 설정 중 오류가 발생했습니다: {str(e)}"

# crond 파일 소유자 및 권한 설정 여부를 점검하는 함수 (재진단)
def check_cron_permissions():
    try:
        # 점검할 cron 관련 파일 목록
        cron_files = {
            '/usr/bin/crontab': '750',
            '/etc/cron.allow': '640',
            '/etc/cron.deny': '640',
            '/etc/crontab': '640',
            '/var/spool/cron': '640',
            '/etc/cron.d': '640'
        }

        for file, permission in cron_files.items():
            if os.path.exists(file):
                # 파일 소유자가 root(0)인지 확인
                file_stat = os.stat(file)
                if file_stat.st_uid != 0:
                    return {"status": "취약", "message": f"{file}의 소유자가 root가 아닙니다."}

                # 파일 권한이 640 이하인지 확인
                file_permissions = oct(file_stat.st_mode)[-3:]
                if file_permissions > permission:
                    return {"status": "취약", "message": f"{file}의 권한이 {permission} 이상입니다."}

        # cron.allow 파일이 있으면, 사용 가능한 사용자 확인
        if os.path.exists('/etc/cron.allow'):
            with open('/etc/cron.allow', 'r') as f:
                if f.read().strip():  # cron.allow 파일에 사용자가 정의되어 있으면 취약
                    return {"status": "취약", "message": "/etc/cron.allow 파일에 사용자가 정의되어 있습니다."}

        # cron.deny 파일이 있으면, deny 파일이 정의되어 있지 않으면 취약
        if os.path.exists('/etc/cron.deny'):
            with open('/etc/cron.deny', 'r') as f:
                if not f.read().strip():  # cron.deny 파일에 사용자가 없으면 취약
                    return {"status": "취약", "message": "/etc/cron.deny 파일에 사용자가 정의되어 있지 않습니다."}

        return {"status": "양호", "message": "crond 관련 파일 소유자 및 권한이 적절히 설정되었습니다."}
    except Exception as e:
        return {"status": "점검불가", "message": f"crond 파일 소유자 및 권한 점검 중 오류가 발생했습니다: {str(e)}"}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result, remediation_message = remediate_cron_permissions()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_cron_permissions()

    # 최종 출력
    account_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "crond 파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": diagnosis_result["status"],
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": remediation_message if remediation_result == "미완료" else diagnosis_result["message"],
        "조치 파일명": "22.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-22"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
