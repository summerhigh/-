import os
import json
import subprocess
import sys
from datetime import datetime

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
            return {"status": "취약", "message": "Everyone에 수정 권한 또는 모든 권한이 부여되어 있습니다."}
        else:
            return {"status": "양호", "message": "Everyone에 수정 권한 또는 모든 권한이 부여되지 않았습니다."}

    except subprocess.CalledProcessError as e:
        # 디렉토리가 존재하지 않는 경우 처리
        if "ItemNotFoundException" in str(e) or "경로는 존재하지 않으므로 찾을 수 없습니다." in str(e):
            return {"status": "양호", "message": "C:\\inetpub\\scripts 경로가 존재하지 않습니다."}
        else:
            return {"status": "점검불가", "message": f"권한 확인 중 오류가 발생했습니다: {str(e)}"}

# CGI 디렉토리 권한 수정 조치 함수
def remediate_cgi_directory_permissions():
    try:
        # PowerShell 명령어로 Everyone의 권한을 제거하고 Administrators 및 System 그룹 추가
        subprocess.run(['powershell', '-Command', 
                         'Remove-Acl "C:\\inetpub\\scripts" -AccountName "Everyone"; '
                         'Set-Acl "C:\\inetpub\\scripts" -AccountName "Administrators" -AccessRights FullControl; '
                         'Set-Acl "C:\\inetpub\\scripts" -AccountName "System" -AccessRights FullControl'], 
                        capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "Everyone의 권한이 제거되고 Administrators 및 System 그룹에 모든 권한이 부여되었습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "CGI 디렉토리 권한 수정에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    cgi_permissions_check_result = check_cgi_directory_permissions()

    # CGI 디렉토리에 잘못된 권한이 있는 경우에만 수정 조치 수행
    if cgi_permissions_check_result["status"] == "취약":
        remediation_result = remediate_cgi_directory_permissions()
    else:
        remediation_result = {"status": "양호", "message": "Everyone에 부여된 잘못된 권한이 없습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    if remediation_result["status"] == "완료":
        diagnosis_result = check_cgi_directory_permissions()
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 최종 출력에 포함할 정보
    cgi_final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS CGI 실행 제한",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"],  
        "메시지": diagnosis_result["message"],
        "조치 파일명": "12.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date,  
        "코드": "W-12"  
    }

    # 최종 결과 출력
    print(json.dumps(cgi_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
