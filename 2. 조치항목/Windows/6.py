import json
import subprocess
import sys
from datetime import datetime

# Administrators 그룹 구성원 확인 함수
def check_administrators_group():
    try:
        # PowerShell 명령어로 Administrators 그룹 구성원 확인
        result = subprocess.run(['powershell', '-Command',
                                 'Get-LocalGroupMember -Group "Administrators" | Select-Object -ExpandProperty Name'],
                                capture_output=True, text=True, check=True)
        admin_group_members = result.stdout.splitlines()

        # 필요 사용자 목록 (Administrator와 kisia 계정을 필요 사용자로 지정)
        unnecessary_accounts = [member for member in admin_group_members if "Administrator" not in member and "kisia" not in member]
        has_unnecessary_accounts = len(unnecessary_accounts) > 0

        if has_unnecessary_accounts:
            return {"status": "취약", "message": f"Administrators 그룹에 불필요한 계정이 있습니다: {', '.join(unnecessary_accounts)}", "unnecessary_accounts": unnecessary_accounts}
        else:
            return {"status": "양호", "message": "Administrators 그룹에 불필요한 계정이 없습니다."}

    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "Administrators 그룹 정보를 가져오는 중 오류가 발생했습니다."}

# 불필요한 관리자 계정 제거 함수
def remediate_unnecessary_admins(unnecessary_accounts):
    removed_admins = []
    failed_admins = []
    
    for admin in unnecessary_accounts:
        try:
            # PowerShell 명령어로 불필요한 관리자 계정 제거
            result = subprocess.run(['powershell', '-Command', f'Remove-LocalGroupMember -Group "Administrators" -Member "{admin}"'],
                                    capture_output=True, text=True, check=True)
            removed_admins.append(admin)
        except subprocess.CalledProcessError:
            failed_admins.append(admin)
    
    if removed_admins and not failed_admins:
        return {"status": "완료", "message": f"불필요한 관리자 계정이 모두 제거되었습니다: {', '.join(removed_admins)}"}
    elif removed_admins:
        return {"status": "부분완료", "message": f"일부 관리자 계정이 제거되지 않았습니다. 성공: {', '.join(removed_admins)}, 실패: {', '.join(failed_admins)}"}
    else:
        return {"status": "미완료", "message": f"관리자 계정 제거에 실패했습니다: {', '.join(failed_admins)}"}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    admin_group_result = check_administrators_group()

    # 불필요한 관리자 계정이 있는 경우에만 제거 조치 수행
    if admin_group_result["status"] == "취약":
        unnecessary_accounts = admin_group_result.get("unnecessary_accounts", [])
        remediation_result = remediate_unnecessary_admins(unnecessary_accounts)
    else:
        remediation_result = {"status": "양호", "message": "Administrators 그룹에 불필요한 계정이 없습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_administrators_group()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력 (런처에 맞는 형식)
    admin_result = {
        "카테고리": "계정관리",
        "항목 설명": "'Administrators 그룹 불필요한 계정 존재 여부 확인'",
        "중요도": "상",
        "진단 결과": "취약",  # 진단 결과는 취약으로 고정
        "조치 결과": remediation_result["status"],  # 조치 결과
        "재진단 결과": diagnosis_result["status"],  # 재진단 결과
        "메시지": diagnosis_result["message"],
        "조치 파일명": "6.py",
        "조치 담당자": 담당자,  # 전달받은 담당자
        "조치 시각": remediation_date,  # 조치 일자
        "코드": "W-06"  # 고정된 코드
    }

    # 최종 결과 출력
    print(json.dumps(admin_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
