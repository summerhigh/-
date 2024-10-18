import os
import json
import subprocess
import sys
from datetime import datetime

# 웹 프로세스 권한 제한 설정 여부 확인 함수
def check_web_process_permissions():
    try:
        # PowerShell 명령어로 IIS Application Pool의 Identity 설정 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-WebConfigurationProperty -Filter system.applicationHost/applicationPools/add -Name processModel.identityType'], 
                                capture_output=True, text=True, check=True)
        
        identity_type = result.stdout.strip()

        # Identity 설정이 ApplicationPoolIdentity, NetworkService, LocalService 중 하나면 양호
        if "ApplicationPoolIdentity" in identity_type or "NetworkService" in identity_type or "LocalService" in identity_type:
            return {"status": "양호", "message": "웹 프로세스가 최소 권한으로 실행되고 있습니다."}
        else:
            return {"status": "취약", "message": "웹 프로세스가 관리자 권한으로 실행되고 있습니다."}

    except subprocess.CalledProcessError as e:
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return {"status": "양호", "message": "IIS 서비스가 설치되지 않았습니다."}
        else:
            return {"status": "점검불가", "message": f"웹 프로세스 권한 확인 중 오류가 발생했습니다: {str(e)}"}

# 웹 프로세스 권한 제한 조치 함수
def remediate_web_process_permissions():
    try:
        # PowerShell 명령어로 Application Pool의 Identity를 ApplicationPoolIdentity로 설정
        subprocess.run(['powershell', '-Command', 
                        'Set-WebConfigurationProperty -Filter system.applicationHost/applicationPools/add -Name processModel.identityType -Value "ApplicationPoolIdentity"'], 
                       capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "웹 프로세스가 최소 권한(ApplicationPoolIdentity)으로 성공적으로 설정되었습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "웹 프로세스 권한 설정에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    process_check_result = check_web_process_permissions()

    # 웹 프로세스가 관리자 권한으로 실행 중인 경우에만 최소 권한 설정 조치 수행
    if process_check_result["status"] == "취약":
        remediation_result = remediate_web_process_permissions()
    else:
        remediation_result = {"status": "양호", "message": "웹 프로세스가 이미 최소 권한으로 설정되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    if remediation_result["status"] == "완료":
        diagnosis_result = check_web_process_permissions()
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 최종 출력에 포함할 정보
    process_final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "웹 프로세스 권한 제한",
        "중요도": "상",
        "진단 결과": "취약", 
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "15.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date,  
        "코드": "W-15" 
    }

    # 최종 결과 출력
    print(json.dumps(process_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
