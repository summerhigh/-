import json
import subprocess
import sys
from datetime import datetime

# 공유 디렉토리 내 Everyone 권한 존재 여부 확인 함수
def check_everyone_permission():
    try:
        # PowerShell 명령어로 공유 폴더 확인 (C$, D$, Admin$, IPC$ 제외)
        result = subprocess.run(['powershell', '-Command',
                                  r'Get-SmbShare | Where-Object {($_.Name -notmatch "C\$|D\$|Admin\$|IPC\$")}'], 
                                capture_output=True, text=True, check=True)
        shares = result.stdout.splitlines()

        # 공유 폴더가 없을 경우, '양호' 반환
        if not shares:
            return {"status": "양호", "message": "공유 폴더가 없습니다."}

        # 권한 확인
        result = subprocess.run(['powershell', '-Command',
                                  r'Get-SmbShare | Where-Object {($_.Name -notmatch "C\$|D\$|Admin\$|IPC\$")} | ForEach-Object { Get-SmbShareAccess -Name $_.Name }'], 
                                capture_output=True, text=True, check=True)
        share_access = result.stdout.splitlines()

        # Everyone 권한이 있는 공유 폴더 확인
        everyone_shares = [line for line in share_access if "Everyone" in line]

        # Everyone 권한이 있는 경우 취약, 없으면 양호
        if everyone_shares:
            return {"status": "취약", "message": "Everyone 권한이 있는 공유 폴더가 발견되었습니다.", "everyone_shares": everyone_shares}
        else:
            return {"status": "양호", "message": "Everyone 권한이 설정된 공유 폴더가 없습니다."}
    
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "공유 폴더 정보를 가져오는 중 오류가 발생했습니다."}

# Everyone 권한 제거 함수
def remediate_everyone_permission(everyone_shares):
    removed_shares = []
    failed_shares = []
    
    for share in everyone_shares:
        try:
            # PowerShell 명령어로 공유 폴더에서 Everyone 권한 제거
            share_name = share.split()[0]  # 공유 폴더 이름 추출
            result = subprocess.run(['powershell', '-Command', f'Remove-SmbShareAccess -Name "{share_name}" -AccountName "Everyone" -Force'],
                                    capture_output=True, text=True, check=True)
            removed_shares.append(share_name)
        except subprocess.CalledProcessError:
            failed_shares.append(share_name)
    
    if removed_shares and not failed_shares:
        return {"status": "완료", "message": f"Everyone 권한이 모두 제거되었습니다: {', '.join(removed_shares)}"}
    elif removed_shares:
        return {"status": "부분완료", "message": f"일부 권한 제거에 실패했습니다. 성공: {', '.join(removed_shares)}, 실패: {', '.join(failed_shares)}"}
    else:
        return {"status": "미완료", "message": f"Everyone 권한 제거에 실패했습니다: {', '.join(failed_shares)}"}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    share_permission_result = check_everyone_permission()

    # Everyone 권한이 있는 경우에만 제거 조치 수행
    if share_permission_result["status"] == "취약":
        everyone_shares = share_permission_result.get("everyone_shares", [])
        remediation_result = remediate_everyone_permission(everyone_shares)
    else:
        remediation_result = {"status": "양호", "message": "Everyone 권한이 설정된 공유 폴더가 없습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_everyone_permission()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    share_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "공유 권한 및 사용자 그룹 설정",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"],  
        "메시지": diagnosis_result["message"],
        "조치 파일명": "7.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date, 
        "코드": "W-07"  
    }

    # 최종 결과 출력
    print(json.dumps(share_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
