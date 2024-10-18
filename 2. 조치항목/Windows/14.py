import os
import json
import subprocess
import sys
from datetime import datetime

# IIS 기본 파일 존재 여부 확인 함수
def check_iis_default_files():
    try:
        # PowerShell 명령어로 IISSamples와 IISHelp 가상 디렉토리 존재 여부 확인
        result_samples = subprocess.run(['powershell', '-Command', 
                                         '(Get-WebVirtualDirectory -Site "Default Web Site" -Name "IISSamples").PhysicalPath'], 
                                        capture_output=True, text=True)

        result_help = subprocess.run(['powershell', '-Command', 
                                      '(Get-WebVirtualDirectory -Site "Default Web Site" -Name "IISHelp").PhysicalPath'], 
                                     capture_output=True, text=True)

        # IISSamples 및 IISHelp 디렉토리가 존재하는지 확인
        samples_status = result_samples.stdout.strip()
        help_status = result_help.stdout.strip()

        if samples_status or help_status:
            return {"status": "취약", "message": "IISSamples 또는 IISHelp 가상 디렉토리가 존재합니다.", "samples_status": samples_status, "help_status": help_status}
        else:
            return {"status": "양호", "message": "IISSamples 및 IISHelp 가상 디렉토리가 존재하지 않습니다."}

    except subprocess.CalledProcessError as e:
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return {"status": "양호", "message": "IIS 서비스가 설치되지 않았습니다."}
        else:
            return {"status": "점검불가", "message": f"가상 디렉토리 확인 중 오류가 발생했습니다: {str(e)}"}

# IIS 기본 파일 삭제 조치 함수
def remediate_iis_default_files(samples_status, help_status):
    try:
        # IISSamples 가상 디렉토리가 존재하는 경우 삭제
        if samples_status:
            subprocess.run(['powershell', '-Command', 
                            'Remove-WebVirtualDirectory -Site "Default Web Site" -Name "IISSamples"'], 
                           capture_output=True, text=True, check=True)
        
        # IISHelp 가상 디렉토리가 존재하는 경우 삭제
        if help_status:
            subprocess.run(['powershell', '-Command', 
                            'Remove-WebVirtualDirectory -Site "Default Web Site" -Name "IISHelp"'], 
                           capture_output=True, text=True, check=True)
        
        return {"status": "완료", "message": "IISSamples 및 IISHelp 가상 디렉토리가 성공적으로 삭제되었습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "IISSamples 및 IISHelp 가상 디렉토리 삭제에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    iis_check_result = check_iis_default_files()

    # IISSamples 또는 IISHelp 디렉토리가 존재하는 경우에만 삭제 조치 수행
    if iis_check_result["status"] == "취약":
        samples_status = iis_check_result.get("samples_status", "")
        help_status = iis_check_result.get("help_status", "")
        remediation_result = remediate_iis_default_files(samples_status, help_status)
    else:
        remediation_result = {"status": "양호", "message": "IISSamples 및 IISHelp 가상 디렉토리가 이미 존재하지 않습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    if remediation_result["status"] == "완료":
        diagnosis_result = check_iis_default_files()
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 최종 출력에 포함할 정보
    iis_final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS 불필요한 파일 제거",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "14.py",
        "조치 담당자": 담당자, 
        "조치 시각": remediation_date,  
        "코드": "W-14" 
    }

    # 최종 결과 출력
    print(json.dumps(iis_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
