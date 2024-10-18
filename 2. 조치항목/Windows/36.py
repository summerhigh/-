import os
import json
import subprocess
import sys
from datetime import datetime

# 백신 프로그램 설치 여부 확인 함수
def check_antivirus_installed():
    try:
        # PowerShell 명령어로 시스템에 설치된 백신 프로그램 확인
        result = subprocess.run(['powershell', '-Command',
                                  'Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct'], 
                                capture_output=True, text=True, check=True)
        antivirus_info = result.stdout.strip()

        # 백신 정보가 있으면 양호, 없으면 취약
        if antivirus_info:
            return {"status": "양호", "message": "백신 프로그램이 설치되어 있습니다."}
        else:
            return {"status": "취약", "message": "백신 프로그램이 설치되어 있지 않습니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "백신 설치 정보를 가져오는 중 오류가 발생했습니다."}

# 백신 설치 조치 함수 (예시)
def remediate_antivirus_installation():
    try:
        # PowerShell 명령어로 백신 프로그램 설치 (실제 설치 명령어가 필요)
        # 예시로서 명령어 추가, 실제 백신 설치 명령어는 상황에 맞게 변경해야 함
        result = subprocess.run(['powershell', '-Command',
                                  'Start-Process -FilePath "백신 설치 경로" -ArgumentList "/S" -NoNewWindow -Wait'], 
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "백신 프로그램을 성공적으로 설치했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "백신 프로그램 설치에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    antivirus_result = check_antivirus_installed()

    # 백신이 설치되어 있지 않은 경우에만 조치 수행
    if antivirus_result["status"] == "취약":
        remediation_result = remediate_antivirus_installation()
    else:
        remediation_result = {"status": "양호", "message": "백신 프로그램이 이미 설치되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행 시간 기록
    diagnosis_date = None
    if remediation_result["status"] == "완료" or remediation_result["status"] == "부분완료":
        diagnosis_result = check_antivirus_installed()
        diagnosis_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 조치 결과와 진단 결과를 결합하여 최종 출력
    antivirus_final_result = {
        "카테고리": "보안 관리",
        "항목 설명": "백신 프로그램 설치",
        "중요도": "상",
        "진단 결과": antivirus_result["status"], 
        "조치 결과": remediation_result["status"], 
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "36.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date, 
        "코드": "W-36" 
    }

    # 최종 결과 출력
    print(json.dumps(antivirus_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
