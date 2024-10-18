import os
import json
import subprocess
import sys
from datetime import datetime

# 최신 Hotfix 적용 여부 확인 함수
def check_hotfix():
    try:
        # PowerShell 명령어로 설치된 최신 Hotfix 확인
        result = subprocess.run(['powershell', '-Command',
                                  'Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1'], 
                                capture_output=True, text=True, check=True)
        output = result.stdout.strip()

        if "KB" in output:  # 최신 Hotfix가 있으면 양호
            return {"status": "양호", "message": "최신 Hotfix가 적용되어 있습니다."}
        else:
            return {"status": "취약", "message": "최신 Hotfix가 적용되지 않았습니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "최신 Hotfix 정보를 가져오는 중 오류가 발생했습니다."}

# 최신 Hotfix 적용 함수
def remediate_hotfix():
    try:
        # PowerShell 명령어로 최신 Hotfix 다운로드 및 설치 (예: 특정 Hotfix)
        # 여기에 Hotfix 설치에 대한 명령어가 들어가야 하지만, 예시로 명령어를 추가합니다.
        result = subprocess.run(['powershell', '-Command',
                                  'Start-Process "powershell.exe" -ArgumentList "Install-WindowsUpdate -KBArticleID KBXXXXX" -Verb RunAs'], 
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "최신 Hotfix를 성공적으로 설치했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "최신 Hotfix 설치에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    hotfix_result = check_hotfix()

    # Hotfix가 적용되지 않은 경우에만 조치 수행
    if hotfix_result["status"] == "취약":
        remediation_result = remediate_hotfix()
    else:
        remediation_result = {"status": "양호", "message": "최신 Hotfix가 이미 적용되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행 시간 기록
    if remediation_result["status"] == "완료":
        diagnosis_result = check_hotfix()
        diagnosis_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    hotfix_final_result = {
        "카테고리": "패치 관리",
        "항목 설명": "최신 Hotfix 적용",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "32.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date, 
        "코드": "W-32"  
    }

    # 최종 결과 출력
    print(json.dumps(hotfix_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
