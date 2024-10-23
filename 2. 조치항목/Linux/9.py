import os
import sys
import subprocess
import json
from datetime import datetime

# /etc/hosts 파일 소유자 및 권한 조치 함수
def remediate_hosts_file_permissions():
    try:
        # /etc/hosts 파일 소유자를 root로 변경 및 권한을 600으로 설정
        subprocess.run(['chown', 'root', '/etc/hosts'], check=False)
        subprocess.run(['chmod', '600', '/etc/hosts'], check=False)

        # 설정이 정상적으로 완료되었는지 재확인
        hosts_stat = os.stat('/etc/hosts')

        if hosts_stat.st_uid == 0 and oct(hosts_stat.st_mode)[-3:] == '600':
            return "완료"  # 소유자가 root이고 권한이 600으로 설정된 경우 완료
        else:
            return "미완료"  # 설정이 제대로 적용되지 않은 경우 미완료

    except Exception as e:
        return "미완료"

# /etc/hosts 파일 소유자 및 권한 확인 함수 (재진단)
def check_hosts_file_permissions():
    try:
        # 첫 번째 시도: /etc/hosts 파일의 소유자 및 권한 확인
        hosts_stat = os.stat('/etc/hosts')

        # 파일 소유자 UID가 root(0)인지 확인
        if hosts_stat.st_uid != 0:
            return {"status": "취약", "message": "파일 소유자가 root가 아닙니다."}

        # 파일 권한 확인 (600 = rw-------)
        file_permissions = oct(hosts_stat.st_mode)[-3:]
        if file_permissions != '600' and file_permissions != '400':
            return {"status": "취약", "message": "파일 권한이 600 이하가 아닙니다."}

        return {"status": "양호", "message": "/etc/hosts 파일의 소유자가 root이고, 권한이 600 이하로 설정되어 있습니다."}

    except FileNotFoundError:
        try:
            # 두 번째 시도: AIX 또는 다른 시스템에서 /etc/hosts 파일 경로 확인
            result = subprocess.run(['ls', '-l', '/etc/hosts'], capture_output=True, text=True)
            if 'root' not in result.stdout or ('rw-------' not in result.stdout and 'r--------' not in result.stdout):
                return {"status": "취약", "message": "AIX 또는 다른 시스템에서 소유자가 root가 아니거나 권한이 600 이하가 아닙니다."}
            return {"status": "양호", "message": "/etc/hosts 파일의 소유자가 root이고, 권한이 600 이하로 설정되어 있습니다."}
        except Exception as e:
            return {"status": "점검불가", "message": "파일을 확인할 수 없습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": "파일을 확인할 수 없습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_hosts_file_permissions()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_hosts_file_permissions()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉터리 관리",
        "항목 설명": "/etc/hosts 파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "9.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-09"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
