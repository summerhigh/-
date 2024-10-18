import os
import sys
import subprocess
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# SSH 서비스가 실행 중인지 확인하는 함수
def check_ssh_service():
    try:
        # ps aux | grep ssh | grep -v grep 명령어로 ssh 프로세스가 실행 중인지 확인
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        filtered_processes = subprocess.run(['grep', 'ssh'], input=result.stdout, text=True, capture_output=True)
        filtered_processes = subprocess.run(['grep', '-v', 'grep'], input=filtered_processes.stdout, text=True, capture_output=True)
        
        # SSH가 실행 중인 경우
        if filtered_processes.stdout.strip():
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

# Telnet 서비스가 실행 중인지 확인하는 함수
def check_telnet_service():
    try:
        # ps aux | grep telnet | grep -v grep 명령어로 telnet 프로세스가 실행 중인지 확인
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        filtered_processes = subprocess.run(['grep', 'telnet'], input=result.stdout, text=True, capture_output=True)
        filtered_processes = subprocess.run(['grep', '-v', 'grep'], input=filtered_processes.stdout, text=True, capture_output=True)
        
        # Telnet이 실행 중인 경우
        if filtered_processes.stdout.strip():
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

# root 계정 원격 접속 제한 여부 확인 함수
def check_root_remote_access():
    try:
        # /etc/ssh/sshd_config 파일에서 PermitRootLogin 설정 확인
        result = subprocess.run(['grep', '^PermitRootLogin', '/etc/ssh/sshd_config'], capture_output=True, text=True, check=True)
        
        # PermitRootLogin 값 확인
        if 'no' in result.stdout:
            return "양호"  # root 계정의 원격 접속이 차단된 경우
        else:
            return "취약"  # root 계정의 원격 접속이 허용된 경우
    except subprocess.CalledProcessError:
        return "점검불가"  # 파일이나 명령어 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # SSH 서비스 상태 점검
    ssh_running = check_ssh_service()
    telnet_running = check_telnet_service()

    # SSH 서비스 실행 중일 때만 root 원격 접속 상태 점검
    if ssh_running:
        status = check_root_remote_access()
    else:
        status = "양호"

    # Telnet 서비스 상태 점검
    if telnet_running:
        status = "취약"  # Telnet이 실행 중이면 취약
    elif status != "취약":
        status = "양호"  # Telnet이 실행 중이지 않으면 양호

    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "계정 관리",
        "항목 설명": "root 계정 원격접속 및 Telnet 서비스 상태",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "1.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-01"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
