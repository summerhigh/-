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
            return "취약"
        else:
            return "양호"
    
    except subprocess.CalledProcessError as e:
        # 서비스가 존재하지 않는 경우 (서비스를 찾을 수 없을 때)
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in e.stderr:
            return "양호"
        else:
            # 그 외의 에러는 점검불가로 처리
            return "점검불가"

if __name__ == "__main__":
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    item = "IIS 서비스 구동 점검"
    
    # 결과 생성
    status = check_iis_service()
    result = generate_result(file_name, status, item)
    
    # 결과 출력
    print(result)