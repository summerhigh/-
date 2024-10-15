import json
import subprocess
import sys
from datetime import datetime

# Guest 계정 비활성화 여부 확인 함수
def check_guest_account_status():
    try:
        # PowerShell 명령어로 Guest 계정 상태 확인 (Enabled 상태를 포함하여 가져옴)
        result = subprocess.run(['powershell', '-Command', '(Get-LocalUser -Name "Guest").Enabled'],
                                capture_output=True, text=True, check=True)
        # 결과에서 Enabled 값이 True인지 확인
        account_enabled = 'True' in result.stdout.strip()
        guest_account_exists = True  # 계정이 존재하는 경우에만 이 코드가 실행되므로 True로 설정
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "Guest 계정 정보를 가져오지 못했습니다."}

    # Guest 계정이 활성화된 경우 취약으로 설정
    if guest_account_exists and account_enabled:
        return {"status": "취약", "message": "Guest 계정이 활성화되어 있습니다."}
    else:
        # 게스트 계정이 존재하지만 비활성화된 경우 양호로 설정
        return {"status": "양호", "message": "Guest 계정이 비활성화되어 있습니다."}


# Guest 계정 비활성화 함수
def remediate_guest_account():
    try:
        # PowerShell 명령어로 Guest 계정 비활성화
        result = subprocess.run(['powershell', '-Command', 'Disable-LocalUser -Name "Guest"'],
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "Guest 계정을 비활성화했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "Guest 계정 비활성화에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_guest_account()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_guest_account_status()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력 (런처에 맞는 형식)
    account_result = {
        "카테고리": "계정관리",
        "항목 설명": "'Guest 계정 비활성화 여부 확인'",
        "중요도": "상",
        "진단 결과": "취약",  # 진단 결과는 취약으로 고정
        "조치 결과": remediation_result["status"],  # 조치 결과
        "재진단 결과": diagnosis_result["status"],  # 재진단 결과
        "메시지": diagnosis_result["message"],
        "조치 파일명": "2.py",
        "조치 담당자": 담당자,  # 전달받은 담당자
        "조치 시각": remediation_date,  # 조치 일자
        "코드": "W-02"  # 고정된 코드
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
