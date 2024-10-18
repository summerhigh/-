import os
import sys
import json
from datetime import datetime

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# NFS 접근 통제 여부를 점검하는 함수
def check_nfs_access_control():
    try:
        # NFS 관련 설정 파일 경로
        nfs_export_files = ['/etc/exports', '/etc/dfs/dfstab']

        everyone_shared = False

        # NFS 설정 파일에서 everyone 접근 제한 여부 확인
        for export_file in nfs_export_files:
            if os.path.exists(export_file):
                with open(export_file, 'r') as f:
                    content = f.read().lower()
                    if 'everyone' in content or 'no_root_squash' in content:
                        everyone_shared = True
                        break

        if everyone_shared:
            return "취약"  # everyone 공유가 설정된 경우
        else:
            return "양호"  # everyone 공유가 설정되지 않은 경우

    except Exception as e:
        return "점검불가"  # 오류 발생 시 점검불가 처리

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # NFS 접근 통제 점검
    status = check_nfs_access_control()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "NFS 접근 통제",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "25.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-25"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
