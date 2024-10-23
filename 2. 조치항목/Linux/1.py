import os
import sys
import subprocess
import json
from datetime import datetime

# SSH 설정 수정 함수 (PermitRootLogin 설정)
def remediate_ssh_config():
    sshd_config_path = "/etc/ssh/sshd_config"
    
    try:
        # SSH 설정 파일이 없으면 양호로 처리
        if not os.path.exists(sshd_config_path):
            return "완료"

        # SSH 설정 파일에서 PermitRootLogin 값을 'no'로 설정
        with open(sshd_config_path, 'r') as file:
            lines = file.readlines()

        with open(sshd_config_path, 'w') as file:
            for line in lines:
                if line.strip().startswith("PermitRootLogin"):
                    file.write("PermitRootLogin no\n")  # root 계정 원격접속 차단
                else:
                    file.write(line)

        # SSH 서비스 재시작
        subprocess.run(['systemctl', 'restart', 'ssh'], check=True)
        return "완료"
    except Exception as e:
        return "미완료"

# Telnet 설정 수정 함수 (securetty 파일 수정)
def remediate_telnet_config():
    securetty_path = "/etc/securetty"
    
    try:
        # securetty 파일이 없으면 양호로 처리
        if not os.path.exists(securetty_path):
            return "완료"

        # pts/x 관련 설정을 제거하여 root 계정의 Telnet 원격 접속 차단
        with open(securetty_path, 'r') as file:
            lines = file.readlines()

        with open(securetty_path, 'w') as file:
            for line in lines:
                if not line.startswith("pts/"):
                    file.write(line)

        # Telnet 서비스 재시작
        subprocess.run(['systemctl', 'restart', 'telnet'], check=True)
        return "완료"
    except Exception as e:
        return "미완료"

# root 계정 원격 접속 제한 여부 확인 함수 (SSH 설정 확인)
def check_root_remote_access():
    sshd_config_path = "/etc/ssh/sshd_config"
    try:
        # SSH 설정 파일이 없으면 양호로 처리
        if not os.path.exists(sshd_config_path):
            return {"status": "양호", "message": "SSH 서비스를 사용하지 않으므로 양호 상태입니다."}

        result = subprocess.run(['grep', '^PermitRootLogin', sshd_config_path], capture_output=True, text=True, check=True)
        if 'no' in result.stdout:
            return {"status": "양호", "message": "root 계정의 SSH 원격접속이 차단되었습니다."}
        else:
            return {"status": "취약", "message": "root 계정의 SSH 원격접속이 허용된 상태입니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "SSH 설정 파일을 확인할 수 없습니다."}

# Telnet 서비스 점검 여부 확인 함수
def check_telnet_access():
    securetty_path = "/etc/securetty"
    try:
        # securetty 파일이 없으면 양호로 처리
        if not os.path.exists(securetty_path):
            return {"status": "양호", "message": "Telnet 서비스를 사용하지 않으므로 양호 상태입니다."}

        result = subprocess.run(['cat', securetty_path], capture_output=True, text=True, check=True)
        if 'pts/' not in result.stdout:
            return {"status": "양호", "message": "root 계정의 Telnet 원격접속이 차단되었습니다."}
        else:
            return {"status": "취약", "message": "root 계정의 Telnet 원격접속이 허용된 상태입니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "Telnet 설정 파일을 확인할 수 없습니다."}

# 최종 조치 상태를 결정하는 함수
def determine_remediate_status(ssh_status, telnet_status):
    if ssh_status == "미완료" or telnet_status == "미완료":
        return "미완료"
    else:
        return "완료"
    
# 최종 진단 상태를 결정하는 함수
def determine_check_status(ssh_status, telnet_status):
    if ssh_status == "취약" or telnet_status == "취약":
        return "취약"
    elif ssh_status == "점검불가" or telnet_status == "점검불가":
        return "점검불가"
    else:
        return "양호"

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행 (SSH 및 Telnet 설정 수정)
    ssh_remediate_result = remediate_ssh_config()
    telnet_remediate_result = remediate_telnet_config()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행 (SSH 및 Telnet 재진단)
    ssh_diagnosis_result = check_root_remote_access()
    telnet_diagnosis_result = check_telnet_access()

    # 최종 출력
    account_result = {
        "카테고리": "계정 관리",
        "항목 설명": "root 계정 원격접속 및 Telnet 서비스 상태",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": determine_remediate_status(ssh_remediate_result, telnet_remediate_result),
        "재진단 결과": determine_check_status(ssh_diagnosis_result["status"], telnet_diagnosis_result["status"]),
        "메시지": f"SSH: {ssh_diagnosis_result['message']} | Telnet: {telnet_diagnosis_result['message']}",
        "조치 파일명": "1.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-01"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
