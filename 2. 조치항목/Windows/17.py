import os
import json
import subprocess
import sys
from datetime import datetime

# 파일 업로드 및 다운로드 제한 설정 여부 확인 함수
def check_file_upload_download_limits():
    try:
        # PowerShell 명령어로 IIS에서 파일 업로드/다운로드 제한 설정 여부 확인
        result = subprocess.run(['powershell', '-Command', 
                                  '(Get-WebConfigurationProperty -Filter system.webServer/security/requestLimits -Name maxAllowedContentLength).Value'], 
                                capture_output=True, text=True, check=True)
        
        upload_download_limit = result.stdout.strip()

        # 파일 업로드 및 다운로드 용량 제한이 설정되어 있으면 양호, 설정되지 않은 경우 취약
        if upload_download_limit and int(upload_download_limit) > 0:
            return {"status": "양호", "message": f"업로드 및 다운로드 제한이 {upload_download_limit} 바이트로 설정되어 있습니다.", "limit_value": upload_download_limit}
        else:
            return {"status": "취약", "message": "업로드 및 다운로드 제한이 설정되어 있지 않습니다.", "limit_value": upload_download_limit}
    except subprocess.CalledProcessError as e:
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return {"status": "양호", "message": "IIS 서비스가 설치되지 않았습니다."}
        else:
            return {"status": "점검불가", "message": f"파일 업로드/다운로드 제한 설정 확인 중 오류가 발생했습니다: {str(e)}"}

# 파일 업로드 및 다운로드 제한 설정 조치 함수
def remediate_file_upload_download_limits(limit_value):
    try:
        # PowerShell 명령어로 업로드 및 다운로드 제한을 30MB로 설정
        subprocess.run(['powershell', '-Command', 
                        'Set-WebConfigurationProperty -Filter system.webServer/security/requestLimits -Name maxAllowedContentLength -Value 31457280'],  # 30MB
                       capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "파일 업로드 및 다운로드 용량이 30MB로 성공적으로 설정되었습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "파일 업로드 및 다운로드 제한 설정에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    limit_check_result = check_file_upload_download_limits()

    # 파일 업로드 및 다운로드 제한이 설정되지 않은 경우에만 설정 조치 수행
    if limit_check_result["status"] == "취약":
        remediation_result = remediate_file_upload_download_limits(limit_check_result.get("limit_value", 0))
    else:
        remediation_result = {"status": "양호", "message": "파일 업로드 및 다운로드 제한이 이미 설정되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    if remediation_result["status"] == "완료":
        diagnosis_result = check_file_upload_download_limits()
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 최종 출력에 포함할 정보
    final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS 파일 업로드 및 다운로드 제한",
        "중요도": "상",
        "진단 결과": "취약", 
        "조치 결과": remediation_result["status"], 
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "17.py",
        "조치 담당자": 담당자, 
        "조치 시각": remediation_date, 
        "코드": "W-17" 
    }

    # 최종 결과 출력
    print(json.dumps(final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
