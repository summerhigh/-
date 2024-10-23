import os
import sys
import subprocess
import json
from datetime import datetime

# NFS 서비스 비활성화 함수
def remediate_nfs_service():
    try:
        # NFS 관련 데몬 목록 (nfsd, statd, mountd)
        nfs_services = ['nfsd', 'statd', 'mountd']

        # 리눅스 및 대부분의 유닉스 시스템에서 systemctl 또는 service 명령으로 서비스 중지
        for service in nfs_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                subprocess.run(['systemctl', 'stop', service], check=False)
                subprocess.run(['systemctl', 'disable', service], check=False)

        # inetd.conf에서 NFS 서비스 주석 처리 (Solaris, AIX, HP-UX 등)
        if os.path.exists('/etc/inetd.conf'):
            subprocess.run(['sed', '-i', 's/\\(nfsd\\|statd\\|mountd\\)/#\\1/g', '/etc/inetd.conf'], check=False)
            subprocess.run(['pkill', '-HUP', 'inetd'], check=False)

        # xinetd에서 NFS 서비스 비활성화
        xinetd_files = ['/etc/xinetd.d/nfs', '/etc/xinetd.d/statd', '/etc/xinetd.d/mountd']
        for xinetd_file in xinetd_files:
            if os.path.exists(xinetd_file):
                subprocess.run(['sed', '-i', 's/disable\\s*=\\s*no/disable = yes/', xinetd_file], check=False)
        subprocess.run(['systemctl', 'restart', 'xinetd'], check=False)

        return "완료"
    except Exception as e:
        return "미완료"

# NFS 서비스 비활성화 여부를 점검하는 함수 (재진단)
def check_nfs_service_status():
    try:
        # NFS 관련 데몬 목록 (nfsd, statd, mountd)
        nfs_services = ['nfsd', 'statd', 'mountd']
        nfs_active = False

        # 리눅스 및 대부분의 유닉스 시스템에서 systemctl 또는 service 명령으로 서비스 상태 확인
        for service in nfs_services:
            if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
                service_status = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                if 'active' in service_status.stdout:
                    nfs_active = True
                    break
        
        # inetd 또는 xinetd에서 NFS 서비스 확인 (Solaris, AIX, HP-UX)
        if not nfs_active:
            inetd_check = subprocess.run(['grep', '-iE', 'nfsd|statd|mountd', '/etc/inetd.conf'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            xinetd_check = subprocess.run(['grep', '-iE', 'nfsd|statd|mountd', '/etc/xinetd.d/'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            if inetd_check.stdout or xinetd_check.stdout:
                nfs_active = True

        if nfs_active:
            return {"status": "취약", "message": "NFS 서비스가 활성화되어 있습니다."}
        else:
            return {"status": "양호", "message": "NFS 서비스가 비활성화되어 있습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": "NFS 서비스 상태 점검 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_nfs_service()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_nfs_service_status()

    # 최종 출력
    account_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "NFS 서비스 비활성화",
        "중요도": "상",
        "진단 결과": diagnosis_result["status"],
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "24.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-24"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
