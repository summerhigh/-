import json
import subprocess
import sys
from datetime import datetime

# 하드디스크 기본 공유 제거 여부 확인 함수
def check_autoshare():
    try:
        # PowerShell 명령어로 레지스트리 AutoShareServer 값 확인 (0이면 양호, 1이면 취약)
        result = subprocess.run(['powershell', '-Command',
                                  'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" | Select-Object -ExpandProperty "AutoShareServer"'], 
                                capture_output=True, text=True, check=True)
        autoshare_value = int(result.stdout.strip()) if result.stdout.strip().isdigit() else None
    except subprocess.CalledProcessError:
        autoshare_value = None  # 속성이 없으면 None으로 설정

    # AutoShareServer 값이 0이면 양호, 1이면 취약, 값이 없으면 양호로 간주
    if autoshare_value == 0 or autoshare_value is None:
        return {"status": "양호", "message": "하드디스크 기본 공유가 제거되어 있습니다."}
    else:
        return {"status": "취약", "message": "하드디스크 기본 공유가 활성화되어 있습니다."}

# 하드디스크 기본 공유 제거 함수
def remediate_autoshare():
    try:
        # PowerShell 명령어로 AutoShareServer 값을 0으로 설정하여 기본 공유 제거
        result = subprocess.run(['powershell', '-Command',
                                  'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" -Name "AutoShareServer" -Value 0'], 
                                capture_output=True, text=True, check=True)
        return {"status": "완료", "message": "하드디스크 기본 공유를 제거했습니다."}
    except subprocess.CalledProcessError:
        return {"status": "미완료", "message": "하드디스크 기본 공유 제거에 실패했습니다."}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    autoshare_result = check_autoshare()

    # AutoShareServer 값이 잘못 설정된 경우에만 조치 수행
    if autoshare_result["status"] == "취약":
        remediation_result = remediate_autoshare()
    else:
        remediation_result = {"status": "양호", "message": "하드디스크 기본 공유가 적절히 설정되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_autoshare()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    autoshare_final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "하드디스크 기본 공유 제거",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "8.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date,  
        "코드": "W-08" 
    }

    # 최종 결과 출력
    print(json.dumps(autoshare_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
