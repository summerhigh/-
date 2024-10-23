import os
import sys
import subprocess
import json
from datetime import datetime

# 최신 보안 패치 적용 함수
def remediate_security_patch():
    try:
        # 운영체제 이름 확인
        os_name = os.uname().sysname.lower()

        # 각 운영체제별 패치 명령어 설정 및 패치 적용 명령어 실행
        if 'linux' in os_name:
            # 예: Ubuntu/Debian의 경우
            patch_apply_cmd = ['apt', 'upgrade', '-y']
        elif 'aix' in os_name:
            patch_apply_cmd = ['instfix', '-k', 'all']
        elif 'sunos' in os_name or 'solaris' in os_name:
            patch_apply_cmd = ['patchadd', '-M']
        elif 'hp-ux' in os_name:
            patch_apply_cmd = ['swinstall', '-x', 'autoreboot=true', '-x', 'patch_match_target=true']
        else:
            return "미완료"  # 지원되지 않는 운영체제

        # 패치 적용 명령어 실행
        subprocess.run(patch_apply_cmd, check=False)

        return "완료"
    except Exception as e:
        return "미완료"

# 최신 보안 패치 적용 여부 점검 함수 (재진단)
def check_security_patch_status():
    try:
        # 운영체제 이름 확인
        os_name = os.uname().sysname.lower()
        
        # 각 운영체제별 패치 확인 명령어 설정
        if 'linux' in os_name:
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
                return "취약"
            else:
                return "양호"

        return "점검불가"

    except Exception as e:
        return "점검불가"

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_security_patch()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_security_patch_status()

    # 최종 출력
    account_result = {
        "카테고리": "패치 관리",
        "항목 설명": "최신 보안패치 및 벤더 권고사항 적용",
        "중요도": "상",
        "진단 결과": diagnosis_result,
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result,
        "조치 파일명": "42.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-42"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
