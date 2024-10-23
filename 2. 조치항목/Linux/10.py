import os
import sys
import subprocess
import json
from datetime import datetime

# /etc/(x)inetd.conf 파일 소유자 및 권한 조치 함수
def remediate_inetd_conf_permissions():
    files_to_fix = ['/etc/inetd.conf', '/etc/xinetd.conf']  # 조치할 파일 목록
    try:
        for file_path in files_to_fix:
            if os.path.exists(file_path):
                # 파일 소유자를 root로 설정
                subprocess.run(['chown', 'root', file_path], check=False)

                # 파일 권한을 600으로 설정
                subprocess.run(['chmod', '600', file_path], check=False)

        # /etc/xinetd.d/ 하위 디렉터리 내 모든 파일의 소유자 및 권한 변경 (xinetd 사용 시)
        xinetd_dir = '/etc/xinetd.d/'
        if os.path.exists(xinetd_dir):
            subprocess.run(['chown', '-R', 'root', xinetd_dir], check=False)
            subprocess.run(['chmod', '-R', '600', xinetd_dir], check=False)

        return "완료"
    except Exception as e:
        return "미완료"

# /etc/(x)inetd.conf 파일 소유자 및 권한 확인 함수 (재진단)
def check_inetd_conf_permissions():
    files_to_check = ['/etc/inetd.conf', '/etc/xinetd.conf']  # 점검할 파일 목록
    try:
        for file_path in files_to_check:
            if os.path.exists(file_path):
                # 파일 소유자 및 권한 확인
                file_stat = os.stat(file_path)

                # 파일 소유자가 root(0)인지 확인
                if file_stat.st_uid != 0:
                    return {"status": "취약", "message": f"{file_path}의 소유자가 root가 아닙니다."}

                # 파일 권한 확인 (600 = rw-------)
                file_permissions = oct(file_stat.st_mode)[-3:]
                if file_permissions != '600':
                    return {"status": "취약", "message": f"{file_path}의 권한이 600이 아닙니다."}

        # /etc/xinetd.d/ 디렉터리 내 파일도 확인 (xinetd 사용 시)
        xinetd_dir = '/etc/xinetd.d/'
        if os.path.exists(xinetd_dir):
            result = subprocess.run(['ls', '-l', xinetd_dir], capture_output=True, text=True)
            if 'root' not in result.stdout or 'rw-------' not in result.stdout:
                return {"status": "취약", "message": "/etc/xinetd.d/ 하위 파일의 소유자 또는 권한이 부적절합니다."}

        return {"status": "양호", "message": "소유자와 권한이 적절하게 설정되었습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": "파일을 확인할 수 없습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_inetd_conf_permissions()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_inetd_conf_permissions()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "/etc/(x)inetd.conf 파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "10.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-10"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
