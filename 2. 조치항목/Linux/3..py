import os
import sys
import subprocess
import json
from datetime import datetime

# 계정 잠금 임계값 설정 조치 함수
def remediate_account_lock_threshold():
    try:
        # 첫 번째 시도: /etc/security/faillock.conf 파일 수정 (리눅스 기반)
        faillock_conf_path = '/etc/security/faillock.conf'
        if os.path.exists(faillock_conf_path):
            with open(faillock_conf_path, 'a') as file:
                file.write("\ndeny=5\n")
            return "완료"

        # 두 번째 시도: /etc/pam.d/system-auth 파일 수정 (리눅스 대체 경로)
        system_auth_path = '/etc/pam.d/system-auth'
        if os.path.exists(system_auth_path):
            with open(system_auth_path, 'a') as file:
                file.write("\nauth required pam_faillock.so deny=5 unlock_time=120\n")
            return "완료"

        # 세 번째 시도: /etc/default/login 파일 수정 (솔라리스 기반)
        login_conf_path = '/etc/default/login'
        if os.path.exists(login_conf_path):
            with open(login_conf_path, 'a') as file:
                file.write("\nRETRIES=5\n")
            return "완료"

        # 네 번째 시도: /etc/security/user 파일 수정 (AIX 기반)
        user_conf_path = '/etc/security/user'
        if os.path.exists(user_conf_path):
            with open(user_conf_path, 'a') as file:
                file.write("\nloginretries=5\n")
            return "완료"

        # 다섯 번째 시도: /tcb/files/auth/system/default 파일 수정 (HP-UX 기반)
        hpux_conf_path = '/tcb/files/auth/system/default'
        if os.path.exists(hpux_conf_path):
            with open(hpux_conf_path, 'a') as file:
                file.write("\nu_maxtries=5\n")
            return "완료"

        return "완료"  # 아무 파일도 존재하지 않으면 완료로 처리 (서비스 사용 안함)
    except Exception as e:
        return "미완료"

# 계정 잠금 임계값 설정 여부 확인 함수 (재진단)
def check_account_lock_threshold():
    try:
        # 첫 번째 시도: /etc/security/faillock.conf에서 계정 잠금 임계값 확인 (리눅스)
        result = subprocess.run(['grep', '^\s*deny', '/etc/security/faillock.conf'], capture_output=True, text=True)
        lock_value = int(result.stdout.split('=')[-1].strip()) if result.stdout else None
        
        # 두 번째 시도: /etc/pam.d/system-auth에서 pam_faillock.so의 deny 설정 확인 (리눅스 대체 경로)
        if lock_value is None:
            result = subprocess.run(['grep', 'pam_faillock.so', '/etc/pam.d/system-auth'], capture_output=True, text=True)
            if 'deny=' in result.stdout:
                lock_value = int(result.stdout.split('deny=')[-1].split()[0].strip())
        
        # 세 번째 시도: /etc/default/login에서 RETRIES 확인 (솔라리스 기반)
        if lock_value is None:
            result = subprocess.run(['grep', 'RETRIES', '/etc/default/login'], capture_output=True, text=True)
            lock_value = int(result.stdout.split('=')[-1].strip()) if result.stdout else None
        
        # 네 번째 시도: /etc/security/user에서 loginretries 확인 (AIX 기반)
        if lock_value is None:
            result = subprocess.run(['grep', 'loginretries', '/etc/security/user'], capture_output=True, text=True)
            lock_value = int(result.stdout.split('=')[-1].strip()) if result.stdout else None
        
        # 다섯 번째 시도: /tcb/files/auth/system/default에서 RETRIES 확인 (HP-UX 기반)
        if lock_value is None:
            result = subprocess.run(['grep', 'RETRIES', '/tcb/files/auth/system/default'], capture_output=True, text=True)
            lock_value = int(result.stdout.split('=')[-1].strip()) if result.stdout else None

        # 계정 잠금 임계값 설정 확인
        if lock_value is not None and lock_value <= 10:
            return {"status": "양호", "message": "계정 잠금 임계값이 10회 이하로 설정되었습니다."}
        else:
            return {"status": "취약", "message": "계정 잠금 임계값이 10회 초과로 설정되었거나 설정이 없습니다."}
    except Exception as e:
        return {"status": "점검불가", "message": "계정 잠금 임계값 설정을 확인할 수 없습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_account_lock_threshold()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_account_lock_threshold()

    # 최종 출력
    account_result = {
        "카테고리": "계정 관리",
        "항목 설명": "계정 잠금 임계값 설정",
        "중요도": "상",
        "진단 결과": "취약", 
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "3.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-03"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
