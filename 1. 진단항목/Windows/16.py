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


# IIS 링크 사용금지 설정 여부 확인 함수
def check_iis_links_usage():
    try:
        # PowerShell 명령어로 IIS에서 심볼릭 링크, aliases, 바로가기 파일 여부 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-ChildItem -Recurse -Force -Filter *.lnk -Path C:\\inetpub\\wwwroot'], 
                                capture_output=True, text=True, check=True)
        
        link_files = result.stdout.strip()

        # 링크 파일이 있으면 취약, 없으면 양호
        if link_files:
            return "취약"
        else:
            return "양호"

    except subprocess.CalledProcessError as e:
        # IIS 서비스가 설치되지 않거나 다른 에러가 발생한 경우 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return "양호"  # IIS가 설치되지 않은 경우 양호로 처리
        else:
            return "점검불가"


if __name__ == "__main__": 
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    item = "IIS 링크 사용금지"

    # 결과 생성
    status = check_iis_links_usage()
    result = generate_result(file_name, status, item)

    # 결과 출력
    print(result)
