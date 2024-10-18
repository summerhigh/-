import os
import json
import subprocess
import sys
from datetime import datetime

# IIS 링크 사용 금지 설정 여부 확인 함수
def check_iis_links_usage():
    try:
        # PowerShell 명령어로 심볼릭 링크, aliases, 바로가기 파일 여부 확인
        result = subprocess.run(['powershell', '-Command', 
                                  'Get-ChildItem -Recurse -Force -Filter *.lnk -Path C:\\inetpub\\wwwroot'], 
                                capture_output=True, text=True, check=True)
        
        link_files = result.stdout.strip()

        # 링크 파일이 있으면 취약, 없으면 양호
        if link_files:
            return {"status": "취약", "message": "웹 디렉토리에 심볼릭 링크, aliases, 바로가기 파일이 존재합니다.", "link_files": link_files}
        else:
            return {"status": "양호", "message": "심볼릭 링크, aliases, 바로가기 파일이 존재하지 않습니다."}

    except subprocess.CalledProcessError as e:
        # IIS 서비스가 설치되지 않거나 다른 에러가 발생한 경우 처리
        if "서비스 이름이 'W3SVC'인 서비스를 찾을 수 없습니다." in str(e):
            return {"status": "양호", "message": "IIS 서비스가 설치되지 않았습니다."}
        else:
            return {"status": "점검불가", "message": f"심볼릭 링크 확인 중 오류가 발생했습니다: {str(e)}"}

# IIS 링크 삭제 조치 함수
def remediate_iis_links_usage(link_files):
    try:
        # 심볼릭 링크 파일 삭제
        for link in link_files.splitlines():
            subprocess.run(['powershell', '-Command', f'Remove-Item -Path "{link}" -Force'], 
                           capture_output=True, text=True, check=True)

        return {"status": "완료", "message": "심볼릭 링크, aliases, 바로가기 파일이 성공적으로 삭제되었습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "심볼릭 링크, aliases, 바로가기 파일 삭제에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    link_check_result = check_iis_links_usage()

    # 링크 파일이 존재하는 경우에만 삭제 조치 수행
    if link_check_result["status"] == "취약":
        link_files = link_check_result.get("link_files", "")
        remediation_result = remediate_iis_links_usage(link_files)
    else:
        remediation_result = {"status": "양호", "message": "심볼릭 링크, aliases, 바로가기 파일이 이미 존재하지 않습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    if remediation_result["status"] == "완료":
        diagnosis_result = check_iis_links_usage()
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 최종 출력에 포함할 정보
    link_final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "IIS 링크 사용금지",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result["status"],
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "16.py",
        "조치 담당자": 담당자, 
        "조치 시각": remediation_date,
        "코드": "W-16"
    }

    # 최종 결과 출력
    print(json.dumps(link_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
