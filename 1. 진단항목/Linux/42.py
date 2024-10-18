import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 시스템 최신 보안 패치 적용 여부 점검 함수
def check_security_patch_status():
    try:
        # 운영체제 이름 확인
        os_name = os.uname().sysname.lower()
        
        # 각 운영체제별 패치 확인 명령어 설정
        if 'linux' in os_name:
            # 예: Ubuntu/Debian의 경우
            patch_check_cmd = ['apt', 'list', '--upgradable']
        elif 'aix' in os_name:
            patch_check_cmd = ['instfix', '-i']
        elif 'sunos' in os_name or 'solaris' in os_name:
            patch_check_cmd = ['showrev', '-p']
        elif 'hp-ux' in os_name:
            patch_check_cmd = ['swlist', '-l', 'patch']
        else:
            return "점검불가"  # 지원되지 않는 운영체제

        # 패치 상태 확인 명령어 실행
        result = subprocess.run(patch_check_cmd, capture_output=True, text=True)

        # 결과 확인
        if result.returncode == 0:
            output = result.stdout.strip()

            # 패치가 필요한 경우 (업그레이드 가능한 항목이 있을 경우)
            if output:
                return "취약"  # 패치가 필요한 경우
            else:
                return "양호"  # 최신 보안 패치가 적용된 경우

        return "점검불가"  # 명령어 실행 오류 또는 알 수 없는 오류

    except Exception as e:
        print(f"오류 발생: {e}")
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # 최신 보안 패치 적용 여부 점검
    status = check_security_patch_status()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "패치 관리",
        "항목 설명": "최신 보안패치 및 벤더 권고사항 적용",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "42.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-42"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
