import os
import sys
import subprocess
import json
from datetime import datetime

# r-command 서비스 비활성화 함수
def remediate_r_command_services():
    try:
        # r-command 관련 서비스 중지 및 비활성화 처리
        r_services = ['rsh', 'rlogin', 'rexec']
        services_exist = False

        # systemctl 또는 service 명령어로 r 서비스 중지 (Linux)
        for service in r_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if service_status.returncode == 0:  # 서비스가 존재하고 있는 경우
                    services_exist = True
                    subprocess.run(['systemctl', 'stop', service], check=False)
                    subprocess.run(['systemctl', 'disable', service], check=False)

        # inetd.conf에서 r-command 서비스 주석 처리 (Solaris, HP-UX 등)
        if os.path.exists('/etc/inetd.conf'):
            subprocess.run(['sed', '-i', 's/\\(rsh\\|rlogin\\|rexec\\)/#\\1/g', '/etc/inetd.conf'], check=False)
            subprocess.run(['pkill', '-HUP', 'inetd'], check=False)
            services_exist = True

        # xinetd에서 r-command 서비스 비활성화
        xinetd_files = ['/etc/xinetd.d/rsh', '/etc/xinetd.d/rlogin', '/etc/xinetd.d/rexec']
        for xinetd_file in xinetd_files:
            if os.path.exists(xinetd_file):
                subprocess.run(['sed', '-i', 's/disable\\s*=\\s*no/disable = yes/', xinetd_file], check=False)
                services_exist = True
        subprocess.run(['systemctl', 'restart', 'xinetd'], check=False)

        # 서비스가 존재하지 않을 경우
        if not services_exist:
            return "완료", "r-command 서비스가 시스템에 존재하지 않습니다."

        return "완료", "r-command 서비스 비활성화가 완료되었습니다."
    except Exception as e:
        return "미완료", f"r-command 서비스 비활성화 중 오류가 발생했습니다: {str(e)}"

# r-command 서비스 비활성화 여부를 점검하는 함수 (재진단)
def check_r_command_services():
    try:
        # 점검할 r 계열 서비스 목록
        r_services = ['rsh', 'rlogin', 'rexec']
        r_services_active = False
        services_exist = False

        # systemctl 또는 service 명령어로 r 서비스 상태 확인 (Linux)
        for service in r_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if service_status.returncode == 0:  # 서비스가 존재하고 있는 경우
                    services_exist = True
                    if 'active' in service_status.stdout:
                        r_services_active = True
                        break
        
        # inetd 또는 xinetd에서 r 서비스 확인 (Solaris, AIX, HP-UX)
        if not r_services_active:
            inetd_check = subprocess.run(['grep', '-iE', 'rsh|rlogin|rexec', '/etc/inetd.conf'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            xinetd_check = subprocess.run(['grep', '-iE', 'rsh|rlogin|rexec', '/etc/xinetd.d/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if inetd_check.returncode == 0 or xinetd_check.returncode == 0:
                services_exist = True
                r_services_active = True

        # r-command 서비스가 존재하지 않는 경우 양호 처리
        if not services_exist:
            return {"status": "양호", "message": "r-command 서비스가 시스템에 존재하지 않습니다."}

        if r_services_active:
            return {"status": "취약", "message": "r-command 계열 서비스가 활성화되어 있습니다."}
        else:
            return {"status": "양호", "message": "r-command 계열 서비스가 비활성화되어 있습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": f"r-command 서비스 상태 점검 중 오류가 발생했습니다: {str(e)}"}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result, remediation_message = remediate_r_command_services()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_r_command_services()

    # 최종 출력
    account_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "r-command 서비스 비활성화",
        "중요도": "상",
        "진단 결과": diagnosis_result["status"],
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": remediation_message if remediation_result == "미완료" else diagnosis_result["message"],
        "조치 파일명": "21.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-21"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
