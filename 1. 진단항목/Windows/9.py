import os
import sys
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# 결과 생성 함수
def generate_result(file_name, status, item):
    code = f"W-{file_name.zfill(2)}"
    importance = "상"
    return f"{code} {importance} {status} {item}"


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
                # 서비스가 존재하지 않는 경우
                if "Cannot find any service with service name" in e.stderr:
                    pass  # 서비스가 없으면 양호로 간주
                else:
                    # 다른 오류는 점검불가로 처리
                    return "점검불가", None

        # 불필요한 서비스가 실행 중인 경우 취약, 실행 중인 서비스가 없으면 양호
        if running_services:
            return "취약", None
        else:
            return "양호", None

    except Exception:
        return "점검불가", None

if __name__ == "__main__":
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    item = "불필요한 서비스 제거"

    # 결과 생성
    status, _ = check_unnecessary_services()
    result = generate_result(file_name, status, item)
    
    # 결과 출력
    print(result)
