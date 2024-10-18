import os
import json
import subprocess
import sys
from datetime import datetime

# 디렉토리 리스팅 설정 여부 확인 함수
def check_directory_listing():
    try:
        # PowerShell 명령어로 IIS에서 디렉토리 리스팅 설정 여부 확인
        result = subprocess.run(['powershell', '-Command', 
                                  '(Get-WebConfigurationProperty -Filter system.webServer/directoryBrowse -Name enabled).Value'], 
                                capture_output=True, text=True, check=True)
        directory_listing_status = result.stdout.strip()

        # 결과가 True이면 취약, False이면 양호
        if directory_listing_status == "True":
            return {"status": "취약", "message": "디렉토리 리스팅이 활성화되어 있습니다."}
        else:
            return {"status": "양호", "message": "디렉토리 리스팅이 비활성화되어 있습니다."}
    
    except subprocess.CalledProcessError as e:
        # IIS 서비스가 존재하지 않는 경우 등 에러 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return {"status": "양호", "message": "IIS 서비스가 설치되지 않았습니다."}
        else:
            # 그 외의 에러는 점검불가로 처리
            return {"status": "점검불가", "message": f"디렉토리 리스팅 상태 확인 중 오류가 발생했습니다: {str(e)}"}

# 디렉토리 리스팅 해제 조치 함수
def remediate_directory_listing():
    try:
        # PowerShell 명령어로 디렉토리 리스팅 비활성화
        result = subprocess.run(['powershell', '-Command', 
                                  'Set-WebConfigurationProperty -Filter system.webServer/directoryBrowse -Name enabled -Value False'], 
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "디렉토리 리스팅이 성공적으로 비활성화되었습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "디렉토리 리스팅 비활성화에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    directory_listing_check_result = check_directory_listing()

    # 디렉토리 리스팅이 활성화된 경우에만 비활성화 조치 수행
    if directory_listing_check_result["status"] == "취약":
        remediation_result = remediate_directory_listing()
    else:
        remediation_result = {"status": "양호", "message": "디렉토리 리스팅이 이미 비활성화되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    if remediation_result["status"] == "완료":
        diagnosis_result = check_directory_listing()
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 최종 출력에 포함할 코드와 설명 정보
    directory_listing_final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "디렉토리 리스팅 제거",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "11.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,  
        "코드": "W-11" 
    }

    # 최종 결과 출력
    print(json.dumps(directory_listing_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
