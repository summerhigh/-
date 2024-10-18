import os
import json
import subprocess
import sys
from datetime import datetime

# 원격 레지스트리 서비스 사용 여부 확인 함수
def check_remote_registry_service():
    try:
        # PowerShell 명령어로 Remote Registry 서비스 상태 확인
        result = subprocess.run(['powershell', '-Command',
                                  'Get-Service -Name RemoteRegistry | Select-Object -ExpandProperty Status'], 
                                capture_output=True, text=True, check=True)
        service_status = result.stdout.strip()

        # 서비스 상태가 Stopped면 양호, Running이면 취약
        if service_status == "Stopped":
            return {"status": "양호", "message": "Remote Registry 서비스가 중지되어 있습니다."}
        else:
            return {"status": "취약", "message": "Remote Registry 서비스가 실행 중입니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "Remote Registry 서비스 정보를 가져오는 중 오류가 발생했습니다."}

# 원격 레지스트리 서비스 중지 조치 함수
def remediate_remote_registry_service():
    try:
        # PowerShell 명령어로 Remote Registry 서비스를 중지
        result = subprocess.run(['powershell', '-Command',
                                  'Stop-Service -Name RemoteRegistry -Force'], 
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "Remote Registry 서비스를 성공적으로 중지했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "Remote Registry 서비스 중지에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remote_registry_result = check_remote_registry_service()

    # 서비스가 실행 중인 경우에만 중지 조치 수행
    if remote_registry_result["status"] == "취약":
        remediation_result = remediate_remote_registry_service()
    else:
        remediation_result = {"status": "양호", "message": "Remote Registry 서비스가 이미 중지되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행 시간 기록
    diagnosis_date = None
    if remediation_result["status"] == "완료":
        diagnosis_result = check_remote_registry_service()
        diagnosis_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    remote_registry_final_result = {
        "카테고리": "로그 관리",
        "항목 설명": "원격으로 액세스 할 수 있는 레지스트리 경로",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "35.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date,  
        "코드": "W-35"  
    }

    # 최종 결과 출력
    print(json.dumps(remote_registry_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
