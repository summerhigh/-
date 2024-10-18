import os
import json
import subprocess
import sys
from datetime import datetime

# 백신 최신 업데이트 여부 확인 함수
def check_antivirus_update():
    try:
        # PowerShell 명령어로 Windows Defender의 최신 업데이트 확인
        result = subprocess.run(['powershell', '-Command',
                                  'Get-MpComputerStatus | Select-Object -ExpandProperty AntivirusSignatureLastUpdated'], 
                                capture_output=True, text=True, check=True)
        last_update = result.stdout.strip()

        if last_update:  # 업데이트 정보가 있으면 양호
            return {"status": "양호", "message": "백신 프로그램이 최신 업데이트 상태입니다."}
        else:
            return {"status": "취약", "message": "백신 프로그램이 최신 업데이트 상태가 아닙니다."}
    except subprocess.CalledProcessError:
        return {"status": "점검불가", "message": "백신 업데이트 정보를 가져오는 중 오류가 발생했습니다."}

# 백신 업데이트 적용 함수
def remediate_antivirus_update():
    try:
        # PowerShell 명령어로 Windows Defender 백신 업데이트 적용
        result = subprocess.run(['powershell', '-Command',
                                  'Update-MpSignature'], 
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "백신 프로그램 업데이트를 성공적으로 적용했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "백신 프로그램 업데이트에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    antivirus_result = check_antivirus_update()

    # 백신 업데이트가 최신이 아닌 경우에만 조치 수행
    if antivirus_result["status"] == "취약":
        remediation_result = remediate_antivirus_update()
    else:
        remediation_result = {"status": "양호", "message": "백신 프로그램이 이미 최신 업데이트 상태입니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행 시간 기록
    if remediation_result["status"] == "완료":
        diagnosis_result = check_antivirus_update()
        diagnosis_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        diagnosis_result = {"status": "점검불가", "message": "조치가 완료되지 않아 진단을 실행할 수 없습니다."}

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    antivirus_final_result = {
        "카테고리": "패치 관리",
        "항목 설명": "백신 프로그램 업데이트",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"], 
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "33.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date, 
        "코드": "W-33" 
    }

    # 최종 결과 출력
    print(json.dumps(antivirus_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
