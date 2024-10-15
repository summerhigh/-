import os
import json
import subprocess
import sys
from datetime import datetime

# IIS 서비스 상태 확인 함수
def check_iis_service():
    try:
        # PowerShell 명령어로 IIS 서비스(W3SVC) 상태 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-Service -Name W3SVC | Select-Object -ExpandProperty Status'], 
                                capture_output=True, text=True, check=True)
        service_status = result.stdout.strip()

        # 서비스가 'Running' 상태이면 취약, 그렇지 않으면 양호
        if service_status == "Running":
            return {"status": "취약", "message": "IIS 서비스(W3SVC)가 실행 중입니다.", "service_status": service_status}
        else:
            return {"status": "양호", "message": "IIS 서비스(W3SVC)가 중지되어 있습니다."}
    
    except subprocess.CalledProcessError as e:
        # 서비스가 존재하지 않는 경우를 양호로 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in e.stderr:
            return {"status": "양호", "message": "IIS 서비스(W3SVC)가 시스템에 설치되지 않았습니다."}
        else:
            # 그 외의 에러는 점검불가로 처리
            return {"status": "점검불가", "message": f"서비스 상태 확인 중 오류가 발생했습니다: {str(e)}"}

# IIS 서비스 중지 조치 함수
def remediate_iis_service():
    try:
        # PowerShell 명령어로 IIS 서비스 중지
        result = subprocess.run(['powershell', '-Command',
                                  'Stop-Service -Name W3SVC -Force'], 
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "IIS 서비스(W3SVC)가 성공적으로 중지되었습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "IIS 서비스(W3SVC) 중지에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    iis_check_result = check_iis_service()

    # IIS 서비스가 실행 중인 경우에만 중지 조치 수행
    if iis_check_result["status"] == "취약":
        remediation_result = remediate_iis_service()
    else:
        remediation_result = {"status": "양호", "message": "IIS 서비스(W3SVC)가 이미 중지되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_iis_service()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력 (런처에 맞는 형식)
    iis_final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "'IIS 서비스 상태 확인'",
        "중요도": "상",
        "진단 결과": "취약",  # 진단 결과는 취약으로 고정
        "조치 결과": remediation_result["status"],  # 조치 결과
        "재진단 결과": diagnosis_result["status"],  # 재진단 결과
        "메시지": diagnosis_result["message"],
        "조치 파일명": "10.py",
        "조치 담당자": 담당자,  # 전달받은 담당자
        "조치 시각": remediation_date,  # 조치 일자
        "코드": "W-10"  # 고정된 코드
    }

    # 최종 결과 출력
    print(json.dumps(iis_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
