import os
import sys
import subprocess
import json
from datetime import datetime

# NFS 접근 통제 조치 함수
def remediate_nfs_access_control():
    try:
        # NFS 관련 설정 파일 경로
        nfs_export_files = ['/etc/exports', '/etc/dfs/dfstab']
        modified = False

        # NFS 설정 파일에서 everyone 접근 설정 제거
        for export_file in nfs_export_files:
            if os.path.exists(export_file):
                with open(export_file, 'r') as f:
                    content = f.read()

                # everyone 또는 no_root_squash를 제거하는 방식으로 설정 수정
                if 'everyone' in content or 'no_root_squash' in content:
                    modified = True
                    content = content.replace('everyone', '').replace('no_root_squash', 'root_squash')

                    # 수정된 내용을 다시 파일에 씀
                    with open(export_file, 'w') as f:
                        f.write(content)

        # 설정 변경이 있으면 NFS 서비스 재구동
        if modified:
            subprocess.run(['exportfs', '-a'], check=False)
            return "완료"
        
        return "완료"
    
    except Exception as e:
        return "미완료"

# NFS 서비스 비활성화 여부를 점검하는 함수 (재진단)
def check_nfs_access_control():
    try:
        # NFS 관련 설정 파일 경로
        nfs_export_files = ['/etc/exports', '/etc/dfs/dfstab']

        everyone_shared = False
        service_found = False

        # NFS 설정 파일에서 everyone 접근 제한 여부 확인
        for export_file in nfs_export_files:
            if os.path.exists(export_file):
                service_found = True
                with open(export_file, 'r') as f:
                    content = f.read().lower()
                    if 'everyone' in content or 'no_root_squash' in content:
                        everyone_shared = True
                        break

        if not service_found:
            return {"status": "양호"}
        
        if everyone_shared:
            return {"status": "취약"}
        else:
            return {"status": "양호"}

    except Exception as e:
        return {"status": "점검불가"}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_nfs_access_control()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_nfs_access_control()

    # 최종 출력
    account_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "NFS 접근 통제",
        "중요도": "상",
        "진단 결과": diagnosis_result["status"],
        "조치 결과": remediation_result,  
        "재진단 결과": diagnosis_result["status"],
        "조치 파일명": "25.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-25"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
