import os
import sys
import subprocess
import json
from datetime import datetime

# 패스워드 파일 보호 설정 조치 함수
def remediate_password_file_protection():
    try:
        # 첫 번째 시도: Linux/Solaris에서 쉐도우 패스워드 사용 적용
        if os.path.exists('/etc/passwd'):
            result = subprocess.run(['pwconv'], check=True)
            if result.returncode == 0:
                return "완료"

        # 두 번째 시도: AIX에서 패스워드 암호화 확인 및 적용
        if os.path.exists('/etc/security/passwd'):
            # 기본적으로 AIX는 패스워드를 암호화하여 저장하므로 특별한 조치가 필요 없음
            return "완료"

        # 세 번째 시도: HP-UX에서 Trusted Mode로 전환하여 패스워드 암호화 적용
        if os.path.exists('/tcb/files/auth/system/default'):
            result = subprocess.run(['/etc/tsconvert'], check=True)
            if result.returncode == 0:
                return "완료"

        return "완료"  # 파일이 없는 경우 완료로 처리 (서비스 사용 안함)
    except Exception as e:
        return "미완료"

# 패스워드 파일 보호 설정 여부 확인 함수 (재진단)
def check_password_file_protection():
    try:
        # 첫 번째 시도: /etc/passwd 파일에서 확인
        with open('/etc/passwd', 'r') as passwd_file:
            passwd_content = passwd_file.read()

            # 패스워드가 평문으로 저장되어 있는지 확인 (리눅스/유닉스 공통)
            if 'x' not in passwd_content:
                return {"status": "취약", "message": "패스워드가 암호화되지 않고 저장되어 있습니다."}

        # 두 번째 시도: /etc/shadow 파일에서 패스워드 암호화 여부 확인 (리눅스)
        try:
            with open('/etc/shadow', 'r') as shadow_file:
                shadow_content = shadow_file.read()

                if any(['!' in line.split(':')[1] or '*' in line.split(':')[1] for line in shadow_content.splitlines()]):
                    return {"status": "양호", "message": "패스워드가 암호화되어 있습니다."}
                else:
                    return {"status": "취약", "message": "패스워드가 암호화되지 않고 저장되어 있습니다."}
        except FileNotFoundError:
            pass

        # 세 번째 시도: /tcb/files/auth/system/default 파일 확인 (HP-UX)
        try:
            with open('/tcb/files/auth/system/default', 'r') as auth_file:
                auth_content = auth_file.read()

                if 'u_pwd=!' in auth_content or 'u_pwd=*' in auth_content:
                    return {"status": "양호", "message": "HP-UX에서 패스워드가 암호화되어 있습니다."}
                else:
                    return {"status": "취약", "message": "패스워드가 암호화되지 않았습니다."}
        except FileNotFoundError:
            pass

        # 네 번째 시도: AIX의 /etc/security/passwd 파일에서 암호화 확인
        try:
            with open('/etc/security/passwd', 'r') as passwd_file:
                passwd_content = passwd_file.read()

                if '!' in passwd_content or '*' in passwd_content:
                    return {"status": "양호", "message": "AIX에서 패스워드가 암호화되어 있습니다."}
                else:
                    return {"status": "취약", "message": "AIX에서 패스워드가 암호화되지 않았습니다."}
        except FileNotFoundError:
            pass

        return {"status": "점검불가", "message": "패스워드 보호 설정을 확인할 수 없습니다."}
    except Exception as e:
        return {"status": "점검불가", "message": "패스워드 파일 보호 상태를 확인할 수 없습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_password_file_protection()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_password_file_protection()

    # 최종 출력
    account_result = {
        "카테고리": "계정 관리",
        "항목 설명": "패스워드 파일 보호",
        "중요도": "상",
        "진단 결과": "취약", 
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "4.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-04"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()