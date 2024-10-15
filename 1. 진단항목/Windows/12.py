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

# CGI 디렉토리 권한 설정 여부 확인 함수
def check_cgi_directory_permissions():
    try:
        # PowerShell 명령어로 inetpub/scripts 디렉토리의 권한을 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-Acl "C:\\inetpub\\scripts" | Select-Object -ExpandProperty Access'], 
                                capture_output=True, text=True)
        permissions = result.stdout.strip()

        # 'Everyone'에 수정 권한 또는 모든 권한이 있는지 확인
        if "Everyone" in permissions and ("Modify" in permissions or "FullControl" in permissions or "Write" in permissions):
            return "취약"
        else:
            return "양호"
    
    except subprocess.CalledProcessError as e:
        # 디렉토리가 존재하지 않는 경우 처리
        if "ItemNotFoundException" in str(e) or "경로는 존재하지 않으므로 찾을 수 없습니다." in str(e):
            return "양호"  # 경로가 존재하지 않으면 취약점이 없으므로 양호로 간주
        else:
            # 그 외의 에러는 점검불가로 처리
            return "점검불가"


if __name__ == "__main__":
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    item = "CGI 실행 제한 설정 여부 점검"
    
    # 결과 생성
    status = check_cgi_directory_permissions()
    result = generate_result(file_name, status, item)
    
    # 결과 출력
    print(result)