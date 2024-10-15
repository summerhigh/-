import os
import sys
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# 결과 생성 함수
def generate_result(file_name, status, item):
    code = f"W-{file_name.zfill(2)}"
    importance = "상"
    return f"{code} {importance} {status} {item}"

# IIS 파일 업로드 및 다운로드 제한 설정 여부 확인 함수
def check_file_upload_download_limits():
    try:
        # PowerShell 명령어로 IIS에서 파일 업로드/다운로드 제한 설정 여부 확인
        result = subprocess.run(['powershell', '-Command', 
                                  '(Get-WebConfigurationProperty -Filter system.webServer/security/requestLimits -Name maxAllowedContentLength).Value'], 
                                capture_output=True, text=True, check=True)
        
        upload_download_limit = result.stdout.strip()

        # 파일 업로드 및 다운로드 용량 제한이 설정되어 있으면 양호, 설정되지 않은 경우 취약
        if upload_download_limit and int(upload_download_limit) > 0:
            return "양호"
        else:
            return "취약"

    except subprocess.CalledProcessError as e:
        # IIS 서비스가 설치되지 않았거나 다른 에러 발생 시 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return "양호"  # IIS가 설치되지 않은 경우 양호로 처리
        else:
            return "점검불가"


if __name__ == "__main__": 
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    item = "IIS 파일 업로드 및 다운로드 제한"

    # 결과 생성
    status = check_file_upload_download_limits()
    result = generate_result(file_name, status, item)

    # 결과 출력
    print(result)
