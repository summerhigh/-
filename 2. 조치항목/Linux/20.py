import os
import sys
import subprocess
import json
from datetime import datetime

# Anonymous FTP 비활성화 조치 함수
def remediate_anonymous_ftp():
    try:
        # vsftpd 설정 파일에서 anonymous_enable 설정을 NO로 변경
        if os.path.exists('/etc/vsftpd.conf'):
            subprocess.run(['sed', '-i', 's/anonymous_enable=YES/anonymous_enable=NO/g', '/etc/vsftpd.conf'], check=False)
            subprocess.run(['systemctl', 'restart', 'vsftpd'], check=False)  # vsftpd 서비스 재시작

        # proftpd 설정 파일에서 Anonymous FTP 설정 주석 처리
        elif os.path.exists('/etc/proftpd/proftpd.conf'):
            subprocess.run(['sed', '-i', 's/\\<Anonymous ~ftp\\>/#Anonymous ~ftp/g', '/etc/proftpd/proftpd.conf'], check=False)
            subprocess.run(['sed', '-i', 's/\\<UserAlias anonymous ftp\\>/#UserAlias anonymous ftp/g', '/etc/proftpd/proftpd.conf'], check=False)
            subprocess.run(['systemctl', 'restart', 'proftpd'], check=False)  # proftpd 서비스 재시작

        # ftp 계정 제거
        if os.path.exists('/etc/passwd'):
            subprocess.run(['userdel', 'ftp'], check=False)

        return "완료"
    except Exception as e:
        return "미완료"

# Anonymous FTP 비활성화 여부를 점검하는 함수 (재진단)
def check_anonymous_ftp():
    try:
        # vsftpd.conf 또는 proftpd.conf에서 익명 FTP 설정 확인
        ftp_config_files = ['/etc/vsftpd.conf', '/etc/ftpaccess', '/etc/proftpd/proftpd.conf']
        anonymous_ftp_enabled = False

        for config_file in ftp_config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read().lower()
                    if 'anonymous_enable=yes'.lower() in content or 'anonftp' in content or 'guest_enable=yes'.lower() in content:
                        anonymous_ftp_enabled = True
                        break

        # ftp 계정 확인
        ftp_account_check = subprocess.run(['grep', 'ftp', '/etc/passwd'], stdout=subprocess.PIPE, text=True)
        if ftp_account_check.stdout.strip():
            anonymous_ftp_enabled = True

        # 익명 FTP가 활성화되어 있으면 취약 상태 반환
        if anonymous_ftp_enabled:
            return {"status": "취약", "message": "익명 FTP가 활성화되어 있습니다."}
        else:
            return {"status": "양호", "message": "익명 FTP가 비활성화되어 있습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": "익명 FTP 상태 점검 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_anonymous_ftp()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_anonymous_ftp()

    # 최종 출력
    account_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "Anonymous FTP 비활성화",
        "중요도": "상",
        "진단 결과": diagnosis_result["status"],
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "20.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-20"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
