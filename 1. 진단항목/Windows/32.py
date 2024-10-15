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

# 최신 Hotfix 적용 여부 확인 함수
def check_hotfix():
    try:
        # PowerShell 명령어로 설치된 최신 Hotfix 확인
        result = subprocess.run(['powershell', '-Command',
                                  'Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1'], 
                                capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        if "KB" in output:  # 최신 Hotfix가 있으면 양호
            return "양호"
        else:
            return "취약"  # Hotfix가 없거나 문제가 있을 경우 취약
    except subprocess.CalledProcessError:
        return "점검불가"  # 명령어 실패 시 점검불가 처리

if __name__ == "__main__":
    # 파일명에서 확장자 제거하고 기본 파일명 추출
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    
    item = "최신 Hot Fix 적용"
    
    # 결과 생성
    status = check_hotfix()
    result = generate_result(file_name, status, item)
    
    # 결과 출력
    print(result)
