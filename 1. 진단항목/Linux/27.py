import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 불필요한 RPC 서비스 목록
rpc_services = [
    'rpc.cmsd', 'rpc.ttdbserverd', 'sadmind', 'rusersd', 'walld', 'sprayd', 'rstatd',
    'rpc.nisd', 'rexd', 'rpc.pcnfsd', 'rpc.statd', 'rpc.ypupdated', 'rpc.rquotad',
    'kcms_server', 'cachefsd'
]

# RPC 서비스 비활성화 여부를 점검하는 함수
def check_rpc_services():
    try:
        rpc_active = False

        # 리눅스 및 대부분의 유닉스 시스템에서 systemctl 또는 service 명령으로 RPC 서비스 상태 확인
        for service in rpc_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                if 'active' in service_status.stdout:
                    rpc_active = True
                    break

        # Solaris, AIX, HP-UX에서는 inetd.conf 또는 xinetd에서 확인
        if not rpc_active:
            inetd_check = subprocess.run(['grep', '-iE', '|'.join(rpc_services), '/etc/inetd.conf'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            xinetd_check = subprocess.run(['grep', '-iE', '|'.join(rpc_services), '/etc/xinetd.d/'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            if inetd_check.stdout or xinetd_check.stdout:
                rpc_active = True

        if rpc_active:
            return "취약"  # 불필요한 RPC 서비스가 활성화된 경우
        else:
            return "양호"  # 불필요한 RPC 서비스가 비활성화된 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # RPC 서비스 상태 점검
    status = check_rpc_services()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "RPC 서비스 확인",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "27.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-27"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
