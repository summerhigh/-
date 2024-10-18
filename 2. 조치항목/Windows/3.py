import json
import subprocess
import sys
from datetime import datetime

# 불필요한 계정 존재 여부 확인 함수
def check_unused_accounts():
    try:
        # PowerShell 명령어로 로컬 사용자 목록 가져오기
        result = subprocess.run(['powershell', '-Command', 'Get-LocalUser'],
                                capture_output=True, text=True, check=True)
        output = result.stdout

        # 불필요한 계정 목록 추출 (Test, test, Temp가 포함된 계정 추출)
        unused_accounts = []
        for line in output.splitlines():
            parts = line.split()  # 각 줄을 공백으로 분리
            if len(parts) > 0:    # 계정 이름이 있는지 확인
                account_name = parts[0]
                # 계정 이름에 Test, test, Temp가 포함된 경우
                if 'Test' in account_name or 'test' in account_name or 'Temp' in account_name:
                    unused_accounts.append(account_name)

        account_exists = len(unused_accounts) > 0

        if account_exists:
            return {"status": "취약", "message": f"불필요한 계정이 발견되었습니다: {', '.join(unused_accounts)}", "accounts": unused_accounts}
        else:
            return {"status": "양호", "message": "불필요한 계정이 없습니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "계정 정보를 가져오는 중 오류가 발생했습니다."}

# 불필요한 계정 삭제 함수
def remediate_unused_accounts(unused_accounts):
    removed_accounts = []
    failed_accounts = []
    
    for account in unused_accounts:
        try:
            # PowerShell 명령어로 불필요한 계정 삭제
            result = subprocess.run(['powershell', '-Command', f'Remove-LocalUser -Name "{account}"'],
                                    capture_output=True, text=True, check=True)
            removed_accounts.append(account)
        except subprocess.CalledProcessError:
            failed_accounts.append(account)
    
    if removed_accounts and not failed_accounts:
        return {"status": "완료", "message": f"불필요한 계정이 모두 삭제되었습니다: {', '.join(removed_accounts)}"}
    elif removed_accounts:
        return {"status": "부분완료", "message": f"일부 계정이 삭제되지 않았습니다. 성공: {', '.join(removed_accounts)}, 실패: {', '.join(failed_accounts)}"}
    else:
        return {"status": "미완료", "message": f"계정 삭제에 실패했습니다: {', '.join(failed_accounts)}"}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 진단을 통해 필요없는 계정 리스트를 추출
    unused_accounts = check_unused_accounts().get("accounts", [])
    remediation_result = None

    if unused_accounts:
        remediation_result = remediate_unused_accounts(unused_accounts)
    else:
        remediation_result = {"status": "양호", "message": "불필요한 계정이 없습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_unused_accounts()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    account_result = {
        "카테고리": "계정 관리",
        "항목 설명": "불필요한 계정 제거",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"], 
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "3.py",
        "조치 담당자": 담당자, 
        "조치 시각": remediation_date, 
        "코드": "W-03"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
