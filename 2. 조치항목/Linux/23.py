import os
import sys
import subprocess
import json
from datetime import datetime

# DoS 공격에 취약한 서비스 비활성화 함수
def remediate_dos_vulnerable_services():
    try:
        # DoS 공격에 취약한 서비스 목록
        vulnerable_services = ['echo', 'discard', 'daytime', 'chargen', 'ntp', 'snmp', 'dns']

        # systemctl 또는 service 명령으로 서비스 비활성화 (Linux)
        for service in vulnerable_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                subprocess.run(['systemctl', 'stop', service], check=False)
                subprocess.run(['systemctl', 'disable', service], check=False)

        # inetd.conf에서 서비스 주석 처리 (Solaris, HP-UX 등)
        if os.path.exists('/etc/inetd.conf'):
            subprocess.run(['sed', '-i', 's/\\(echo\\|discard\\|daytime\\|chargen\\)/#\\1/g', '/etc/inetd.conf'], check=False)
            subprocess.run(['pkill', '-HUP', 'inetd'], check=False)

        # xinetd에서 서비스 비활성화
        xinetd_files = ['/etc/xinetd.d/echo', '/etc/xinetd.d/discard', '/etc/xinetd.d/daytime', '/etc/xinetd.d/chargen']
        for xinetd_file in xinetd_files:
            if os.path.exists(xinetd_file):
                subprocess.run(['sed', '-i', 's/disable\\s*=\\s*no/disable = yes/', xinetd_file], check=False)
        subprocess.run(['systemctl', 'restart', 'xinetd'], check=False)

        return "완료"
    except Exception as e:
        return "미완료", f"서비스 비활성화 중 오류가 발생했습니다: {str(e)}"

# DoS 공격에 취약한 서비스 비활성화 여부를 점검하는 함수 (재진단)
def check_dos_vulnerable_services():
    try:
        # DoS 공격에 취약한 서비스 목록
        vulnerable_services = ['echo', 'discard', 'daytime', 'chargen', 'ntp', 'snmp', 'dns']

        service_active = False

        # 리눅스 및 대부분의 유닉스 시스템에서 systemctl 또는 service 명령으로 서비스 상태 확인
        for service in vulnerable_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                if 'active' in service_status.stdout:
                    service_active = True
                    break
        
        # inetd 또는 xinetd에서 서비스 설정 확인 (Solaris, AIX, HP-UX)
        if not service_active:
            inetd_check = subprocess.run(['grep', '-iE', 'echo|discard|daytime|chargen', '/etc/inetd.conf'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            xinetd_check = subprocess.run(['grep', '-iE', 'echo|discard|daytime|chargen', '/etc/xinetd.d/'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            if inetd_check.stdout or xinetd_check.stdout:
                service_active = True

        if service_active:
            return {"status": "취약", "message": "DoS 공격에 취약한 서비스가 활성화되어 있습니다."}
        else:
            return {"status": "양호", "message": "DoS 공격에 취약한 서비스가 비활성화되어 있습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": f"서비스 상태 점검 중 오류가 발생했습니다: {str(e)}"}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result, remediation_message = remediate_dos_vulnerable_services()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_dos_vulnerable_services()

    # 최종 출력
    account_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "DoS 공격에 취약한 서비스 비활성화",
        "중요도": "상",
        "진단 결과": diagnosis_result["status"],
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": remediation_message if remediation_result == "미완료" else diagnosis_result["message"],
        "조치 파일명": "23.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-23"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
