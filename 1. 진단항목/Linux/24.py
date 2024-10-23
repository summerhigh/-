import os
import sys
import json
from datetime import datetime
import subprocess

# NFS 서비스 비활성화 여부를 점검하는 함수
def check_nfs_service_status():
    try:
        # NFS 관련 데몬 목록 (nfsd, statd, mountd)
        nfs_services = ['nfsd', 'statd', 'mountd']
        nfs_active = False
        service_found = False

        # 리눅스 및 대부분의 유닉스 시스템에서 systemctl 또는 service 명령으로 서비스 상태 확인
        for service in nfs_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                if service_status.returncode == 0:
                    service_found = True
                if 'active' in service_status.stdout:
                    nfs_active = True
                    break
        
        # inetd 또는 xinetd에서 NFS 서비스 확인 (Solaris, AIX, HP-UX)
        if not nfs_active:
            inetd_check = subprocess.run(['grep', '-iE', 'nfsd|statd|mountd', '/etc/inetd.conf'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            xinetd_check = subprocess.run(['grep', '-iE', 'nfsd|statd|mountd', '/etc/xinetd.d/'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            if inetd_check.stdout or xinetd_check.stdout:
                nfs_active = True
            if inetd_check.stdout or xinetd_check.stdout:
                service_found = True

        # 서비스가 없으면 "양호"로 처리
        if not service_found:
            return "양호", "NFS 관련 서비스가 존재하지 않습니다."
        elif nfs_active:
            return "취약", "NFS 서비스가 활성화되어 있습니다."
        else:
            return "양호", "NFS 서비스가 비활성화되어 있습니다."

    except Exception as e:
        return "점검불가", f"오류 발생: {str(e)}"

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # NFS 서비스 상태 점검
    status, message = check_nfs_service_status()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "NFS 서비스 비활성화 여부 점검",
        "중요도": "상",
        "진단 결과": status, 
        "메시지": message,
        "진단 파일명": "24.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-24"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
