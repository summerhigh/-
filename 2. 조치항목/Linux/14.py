import os
import sys
import subprocess
import json
from datetime import datetime
import pwd

# 환경 변수 파일 목록
env_files = [".profile", ".kshrc", ".cshrc", ".bashrc", ".bash_profile", ".login", ".exrc", ".netrc"]

# 사용자, 시스템 시작 파일 및 환경 파일의 소유자 및 권한 조치 함수
def remediate_env_file_permissions():
    try:
        # 모든 사용자의 홈 디렉터리 확인
        users = pwd.getpwall()
        for user in users:
            home_dir = user.pw_dir
            if os.path.isdir(home_dir):
                # 홈 디렉터리 내의 환경변수 파일들 확인
                for env_file in env_files:
                    file_path = os.path.join(home_dir, env_file)
                    if os.path.exists(file_path):
                        file_stat = os.stat(file_path)

                        # 파일 소유자가 root 또는 해당 계정으로 되어 있는지 확인하고, 설정
                        if file_stat.st_uid != 0 and file_stat.st_uid != user.pw_uid:
                            result = subprocess.run(['chown', user.pw_name, file_path], check=True)
                            if result.returncode != 0:
                                return f"미완료: 소유자 변경 실패 - {file_path}"

                        # 다른 사용자 쓰기 권한 제거 (root와 소유자만 쓰기 권한을 가질 수 있음)
                        result = subprocess.run(['chmod', 'o-w', file_path], check=True)
                        if result.returncode != 0:
                            return f"미완료: 쓰기 권한 제거 실패 - {file_path}"

        return "완료"  # 모든 환경 변수 파일 권한 및 소유자 조치 완료
    except Exception as e:
        return f"미완료: {str(e)}"  # 오류 발생 시

# 환경 변수 파일 점검 함수 (재진단)
def check_env_file_permissions():
    try:
        # 모든 사용자의 홈 디렉터리 확인
        users = pwd.getpwall()
        for user in users:
            home_dir = user.pw_dir
            if os.path.isdir(home_dir):
                # 홈 디렉터리 내의 환경변수 파일들 확인
                for env_file in env_files:
                    file_path = os.path.join(home_dir, env_file)
                    if os.path.exists(file_path):
                        file_stat = os.stat(file_path)

                        # 파일 소유자가 root 또는 해당 계정이어야 함
                        if file_stat.st_uid != 0 and file_stat.st_uid != user.pw_uid:
                            return {"status": "취약", "message": f"{file_path} 파일의 소유자가 잘못되었습니다."}

                        # 파일 권한 확인 (쓰기 권한이 root와 소유자에게만 있어야 함)
                        file_permissions = oct(file_stat.st_mode)[-3:]
                        if file_permissions[1] != '0' or file_permissions[2] != '0':
                            return {"status": "취약", "message": f"{file_path} 파일에 다른 사용자에게 쓰기 권한이 있습니다."}

        return {"status": "양호", "message": "모든 환경 변수 파일이 적절히 설정되었습니다."}
    except Exception as e:
        return {"status": "점검불가", "message": f"환경 파일 점검 중 오류가 발생했습니다: {str(e)}"}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_env_file_permissions()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_env_file_permissions()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "사용자, 시스템 시작파일 및 환경파일 소유자 및 권한 설정",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "14.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-14"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
