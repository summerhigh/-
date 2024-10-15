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

# SAM 파일 접근 권한 설정 여부 확인 함수
def check_sam_permissions():
    try:
        # icacls 명령어로 SAM 파일 권한 확인
        result = subprocess.run(['icacls', 'C:\\Windows\\System32\\config\\SAM'], 
                                capture_output=True, text=True)
        output = result.stdout.lower()

        # 'administrator'와 'system'만 포함되어 있는지 확인
        # 'everyone'이나 기타 그룹이 포함되지 않은 경우 양호로 간주
        if 'nt authority\\system' in output and 'builtin\\administrators' in output and 'everyone' not in output:
            return "양호"
        else:
            return "취약"
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return "점검불가"

if __name__ == "__main__":
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    item = "SAM 파일 접근 통제 설정"
    
    # 결과 생성
    status = check_sam_permissions()
    result = generate_result(file_name, status, item)
    
    # 결과 출력
    print(result)
