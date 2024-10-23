import os
import sys
import subprocess
import json
from datetime import datetime

# 패스워드 복잡성 설정 조치 함수
def remediate_password_complexity():
    try:
        # 첫 번째 시도: /etc/security/pwquality.conf 파일 수정 (리눅스 기반)
        pwquality_conf_path = '/etc/security/pwquality.conf'
        if os.path.exists(pwquality_conf_path):
            with open(pwquality_conf_path, 'a') as file:
                file.write("\nminlen=8\nlcredit=-1\nucredit=-1\ndcredit=-1\nocredit=-1\n")
            return "완료"

        # 두 번째 시도: /etc/login.defs 파일 수정 (리눅스 대체 경로)
        login_defs_path = '/etc/login.defs'
        if os.path.exists(login_defs_path):
            with open(login_defs_path, 'a') as file:
                file.write("\nPASS_MIN_LEN 8\n")
            return "완료"

        # 세 번째 시도: /etc/security/user 파일 수정 (AIX 기반)
        security_user_path = '/etc/security/user'
        if os.path.exists(security_user_path):
            with open(security_user_path, 'a') as file:
                file.write("\nminlen=8\nminalpha=2\nminother=2\n")
            return "완료"

        # 네 번째 시도: /tcb/files/auth/system/default 파일 수정 (HP-UX 기반)
        hpux_default_path = '/tcb/files/auth/system/default'
        if os.path.exists(hpux_default_path):
            with open(hpux_default_path, 'a') as file:
                file.write("\nMIN_PASSWORD_LENGTH=8\n")
            return "완료"

        # 다섯 번째 시도: /etc/default/passwd 파일 수정 (솔라리스)
        solaris_passwd_path = '/etc/default/passwd'
        if os.path.exists(solaris_passwd_path):
            with open(solaris_passwd_path, 'a') as file:
                file.write("\nMINLEN=8\n")
            return "완료"

        return "완료"  # 아무 파일도 존재하지 않으면 완료로 처리 (서비스 사용 안함)
    except Exception as e:
        return "미완료"

# 패스워드 복잡성 설정 여부 확인 함수 (재진단)
def check_password_complexity():
    try:
        # 첫 번째 시도: /etc/security/pwquality.conf 파일에서 복잡성 확인
        result = subprocess.run(['grep', 'minlen', '/etc/security/pwquality.conf'], capture_output=True, text=True)
        minlen = int(result.stdout.split('=')[-1].strip()) if result.stdout else 0
        
        if minlen == 0:
            result = subprocess.run(['grep', 'PASS_MIN_LEN', '/etc/login.defs'], capture_output=True, text=True)
            minlen = int(result.stdout.split()[-1]) if result.stdout else 0

        if minlen == 0:
            result = subprocess.run(['grep', 'minlen', '/etc/security/user'], capture_output=True, text=True)
            minlen = int(result.stdout.split('=')[-1].strip()) if result.stdout else 0

        if minlen == 0:
            result = subprocess.run(['grep', 'MIN_PASSWORD_LENGTH', '/tcb/files/auth/system/default'], capture_output=True, text=True)
            minlen = int(result.stdout.split('=')[-1].strip()) if result.stdout else 0

        if minlen == 0:
            result = subprocess.run(['grep', 'PASSLENGTH', '/etc/default/passwd'], capture_output=True, text=True)
            minlen = int(result.stdout.split('=')[-1].strip()) if result.stdout else 0

        if minlen >= 8:
            return {"status": "양호", "message": "패스워드 최소 길이가 8자 이상입니다."}
        else:
            return {"status": "취약", "message": "패스워드 최소 길이가 8자 미만입니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "패스워드 복잡성 설정을 확인할 수 없습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_password_complexity()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_password_complexity()

    # 최종 출력
    account_result = {
        "카테고리": "계정 관리",
        "항목 설명": "패스워드 복잡성 설정",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "2.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-02"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
