import os
import json
import subprocess
import sys
from datetime import datetime

# 불필요한 서비스 목록
UNNECESSARY_SERVICES = [
    'Alerter',                      # 네트워크 관리용 경고 메시지 전송
    'Automatic Updates',            # 윈도우 업데이트
    'Clipbook',                     # 클립북 공유
    'Computer Browser',             # 네트워크 컴퓨터 목록 관리
    'Cryptographic Services',       # 윈도우 파일 서명 확인
    'DHCP Client',                  # DHCP 서버로부터 IP주소 받기
    'Distributed Link Tracking Client', # NTFS 파일간 연결 관리
    'DNS Client',                   # DNS 이름 확인 및 캐시
    'Error Reporting Service',      # 응용 프로그램 오류 보고
    'Human Interface Device Access',# HID 장치 지원
    'IMAPI CD-Burning COM Service', # CD/DVD-RW 백업
    'Messenger',                    # 네트워크 메시지 전송
    'NetMeeting Remote Desktop Sharing', # 넷미팅 원격 접속
    'Portable Media Serial Number', # 이동성 음악기기 등록번호 복원
    'Print Spooler',                # 프린터 스풀링 관리
    'Remote Registry',              # 원격 레지스트리 수정
    'Simple TCP/IP Services',       # Echo, Discard 등 TCP/IP 서비스
    'Wireless Zero Configuration',  # 무선 네트워크 설정
]

# 불필요한 서비스 실행 여부 확인 함수
def check_unnecessary_services():
    try:
        running_services = []
        for service in UNNECESSARY_SERVICES:
            try:
                # PowerShell 명령어로 각 서비스 상태 확인
                result = subprocess.run(['powershell', '-Command', 
                                          f'Get-Service -Name {service} | Select-Object -ExpandProperty Status'], 
                                         capture_output=True, text=True)
                service_status = result.stdout.strip()

                # 서비스가 'Running' 상태이면 리스트에 추가
                if service_status == "Running":
                    running_services.append(service)

            except subprocess.CalledProcessError as e:
                # 서비스가 존재하지 않는 경우 무시
                if "Cannot find any service with service name" in e.stderr:
                    continue
                else:
                    return {"status": "점검불가", "message": f"서비스 확인 중 오류가 발생했습니다: {str(e)}"}

        if running_services:
            return {"status": "취약", "message": f"다음 서비스가 실행 중입니다: {', '.join(running_services)}", "running_services": running_services}
        else:
            return {"status": "양호", "message": "모든 불필요한 서비스가 중지되었거나 존재하지 않습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": f"서비스 상태를 확인하는 중 알 수 없는 오류가 발생했습니다: {str(e)}"}

# 불필요한 서비스 중지 조치 함수
def remediate_unnecessary_services(running_services):
    stopped_services = []
    failed_services = []

    for service in running_services:
        try:
            # PowerShell 명령어로 서비스 중지
            result = subprocess.run(['powershell', '-Command', f'Stop-Service -Name {service} -Force'], 
                                    capture_output=True, text=True, check=True)
            stopped_services.append(service)
        except subprocess.CalledProcessError:
            failed_services.append(service)

    if stopped_services and not failed_services:
        return {"status": "완료", "message": f"다음 서비스가 성공적으로 중지되었습니다: {', '.join(stopped_services)}"}
    elif stopped_services:
        return {"status": "부분완료", "message": f"일부 서비스 중지에 실패했습니다. 성공: {', '.join(stopped_services)}, 실패: {', '.join(failed_services)}"}
    else:
        return {"status": "미완료", "message": f"서비스 중지에 실패했습니다: {', '.join(failed_services)}"}

def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    service_check_result = check_unnecessary_services()

    # 실행 중인 불필요한 서비스가 있는 경우에만 조치 수행
    if service_check_result["status"] == "취약":
        running_services = service_check_result.get("running_services", [])
        remediation_result = remediate_unnecessary_services(running_services)
    else:
        remediation_result = {"status": "양호", "message": "모든 불필요한 서비스가 이미 중지되어 있습니다."}

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_unnecessary_services()

    # 조치 결과와 재진단 결과를 결합하여 최종 출력
    service_final_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "불필요한 서비스 제거",
        "중요도": "상",
        "진단 결과": "취약",  
        "조치 결과": remediation_result["status"],  
        "재진단 결과": diagnosis_result["status"], 
        "메시지": diagnosis_result["message"],
        "조치 파일명": "9.py",
        "조치 담당자": 담당자,  
        "조치 시각": remediation_date, 
        "코드": "W-09"  
    }

    # 최종 결과 출력
    print(json.dumps(service_final_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
