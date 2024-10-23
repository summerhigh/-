import os
import sys
import subprocess
import json
from datetime import datetime

# Finger 서비스 비활성화 함수
def remediate_finger_service():
    try:
        # 시스템에서 Finger 서비스 중지 (Linux, Solaris, AIX, HP-UX 등 처리)
        if os.path.exists('/etc/inetd.conf'):
            # inetd에서 Finger 서비스 주석 처리
            subprocess.run(['sed', '-i', 's/^finger/#finger/g', '/etc/inetd.conf'], check=False)
            subprocess.run(['pkill', '-HUP', 'inetd'], check=False)  # inetd 서비스 재시작
        elif os.path.exists('/etc/xinetd.d/finger'):
            # xinetd에서 Finger 서비스 비활성화
            subprocess.run(['sed', '-i', 's/disable\s*=\s*no/disable = yes/', '/etc/xinetd.d/finger'], check=False)
            subprocess.run(['systemctl', 'restart', 'xinetd'], check=False)

        return "완료"
    except Exception as e:
        return "미완료"

# Finger 서비스 비활성화 여부를 점검하는 함수 (재진단)
def check_finger_service_status():
    try:
        finger_service_active = False
        
        # 리눅스 시스템에서 systemctl이나 service로 finger 서비스 상태 확인
        if os.path.exists('/bin/systemctl') or os.path.exists('/usr/sbin/service'):
            finger_status = subprocess.run(['systemctl', 'is-active', 'finger'], capture_output=True, text=True)
            
            # 서비스가 존재하지 않으면 양호 처리
            if 'could not be found' in finger_status.stderr or 'inactive' in finger_status.stdout:
                return {"status": "양호", "message": "Finger 서비스가 존재하지 않거나 비활성화되었습니다."}
            elif 'active' in finger_status.stdout:
                finger_service_active = True

        # inetd 또는 xinetd 설정에서 finger 서비스 상태 확인
        if not finger_service_active:
            inetd_check = subprocess.run(['grep', '-i', 'finger', '/etc/inetd.conf'], capture_output=True, text=True)
            xinetd_check = subprocess.run(['grep', '-i', 'finger', '/etc/xinetd.d/finger'], capture_output=True, text=True, stderr=subprocess.DEVNULL)

            # inetd나 xinetd에 finger 서비스 설정이 없으면 양호 처리
            if not inetd_check.stdout and not xinetd_check.stdout:
                return {"status": "양호", "message": "Finger 서비스가 존재하지 않거나 비활성화되었습니다."}

            # finger 서비스 설정이 존재하면 활성화 상태로 처리
            if inetd_check.stdout or xinetd_check.stdout:
                finger_service_active = True
        
        # Finger 서비스가 활성화된 경우
        if finger_service_active:
            return {"status": "취약", "message": "Finger 서비스가 활성화되어 있습니다."}
        else:
            # Finger 서비스가 비활성화된 경우
            return {"status": "양호", "message": "Finger 서비스가 비활성화되어 있습니다."}

    except Exception as e:
        return {"status": "점검불가", "message": "Finger 서비스 상태 점검 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_finger_service()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_finger_service_status()

    # 최종 출력
    account_result = {
        "카테고리": "서비스 관리",
        "항목 설명": "Finger 서비스 비활성화",
        "중요도": "상",
        "진단 결과": diagnosis_result["status"],
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "19.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-19"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
