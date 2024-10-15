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

# 웹 프로세스 권한 제한 설정 여부 확인 함수
def check_web_process_permissions():
    try:
        # PowerShell 명령어로 IIS Application Pool의 Identity 설정 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-WebConfigurationProperty -Filter system.applicationHost/applicationPools/add -Name processModel.identityType'], 
                                capture_output=True, text=True, check=True)
        
        identity_type = result.stdout.strip()

        # Identity 설정이 ApplicationPoolIdentity나 최소 권한 계정인 경우 양호, 그렇지 않으면 취약
        if "ApplicationPoolIdentity" in identity_type or "NetworkService" in identity_type or "LocalService" in identity_type:
            return "양호"
        else:
            return "취약"

    except subprocess.CalledProcessError as e:
        # IIS 서비스가 존재하지 않는 경우 등 에러 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return "양호"  # IIS가 설치되지 않은 경우 양호로 처리
        else:
            return "점검불가"

if __name__ == "__main__": 
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    item = "웹 프로세스 권한 제한 설정 여부 점검"

    # 결과 생성
    status = check_web_process_permissions()
    result = generate_result(file_name, status, item)

    # 결과 출력
    print(result)
