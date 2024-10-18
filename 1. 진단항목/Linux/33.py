import os
import sys
import json
from datetime import datetime
import subprocess
import re

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 최신 BIND 버전 정보 (예: 9.10.3-P2)
LATEST_BIND_VERSION = "9.10.3-P2"

# 버전 문자열을 정리하여 숫자로 변환하는 함수 (버전 비교를 위한 처리)
def version_to_tuple(version):
    # 예를 들어 '9.18.28-0ubuntu0.22.04.1-Ubuntu'를 '9.18.28'로 변환 후 숫자로 변환
    version = re.sub(r'[^0-9.]', '', version)
    return tuple(map(int, version.split('.')))

# BIND 버전이 최신 버전 이상인지 비교하는 함수
def is_version_gte(version1, version2):
    # 버전 문자열을 숫자 튜플로 변환한 뒤 비교
    return version_to_tuple(version1) >= version_to_tuple(version2)

# BIND 버전 확인 및 패치 여부를 점검하는 함수
def check_bind_version():
    try:
        # 각 운영체제에서 BIND 버전을 확인하는 명령어 및 파일 경로
        os_name = os.uname().sysname.lower()
        bind_version_cmd = None

        # Linux, Solaris, AIX, HP-UX 등 다양한 OS에 대한 명령 설정
        if 'linux' in os_name:
            bind_version_cmd = ['named', '-v']
        elif 'sunos' in os_name or 'solaris' in os_name:
            bind_version_cmd = ['/usr/sbin/named', '-v']  # Solaris의 BIND 경로
        elif 'aix' in os_name:
            bind_version_cmd = ['/usr/sbin/named', '-v']  # AIX에서 BIND 명령어
        elif 'hp-ux' in os_name:
            bind_version_cmd = ['/opt/named/sbin/named', '-v']  # HP-UX에서 BIND 경로

        # 명령어를 찾을 수 없는 경우 BIND가 설치되지 않았음
        if not bind_version_cmd:
            return "양호"  # BIND가 설치되어 있지 않음 (DNS 서비스 미사용)

        # BIND 버전 확인 명령어 실행
        bind_version_check = subprocess.run(bind_version_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if bind_version_check.returncode == 0:
            # BIND 버전 정보 출력에서 버전 추출
            output = bind_version_check.stdout
            current_version = output.split()[1]  # Version 정보 추출

            # 최신 버전과 비교하여 같거나 더 최신인 경우 양호 처리
            if is_version_gte(current_version, LATEST_BIND_VERSION):
                return "양호"  # 최신 버전 사용 중인 경우
            else:
                return "취약"  # 취약한 버전 사용 중인 경우
        else:
            return "양호"  # BIND 서비스가 실행되지 않음 (서비스 미사용)

    except FileNotFoundError as e:
        return "양호"  # BIND가 설치되어 있지 않음 (DNS 서비스 미사용)
    except Exception as e:
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # BIND 버전 점검
    status = check_bind_version()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "DNS 보안 버전 패치",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "33.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-33"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
