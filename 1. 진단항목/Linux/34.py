import os
import sys
import json
from datetime import datetime
import subprocess

# 두 계층 상위 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# DNS 설정 파일 경로 (기본적으로 /etc/named.conf에서 점검)
DNS_CONFIG_PATH = "/etc/named.conf"

# DNS Zone Transfer 설정 점검 함수
def check_zone_transfer():
    try:
        # DNS 설정 파일이 존재하는지 확인
        if os.path.exists(DNS_CONFIG_PATH):
            with open(DNS_CONFIG_PATH, 'r') as f:
                content = f.read()

                # zone transfer 설정 확인 (allow-transfer 또는 allow-query 설정이 있는지 점검)
                if 'allow-transfer' in content or 'allow-query' in content:
                    if 'any' not in content:  # 'any'가 포함되지 않으면 허가된 서버에게만 전송
                        return "양호"  # 허가된 Secondary Name Server에게만 전송
                    else:
                        return "취약"  # 모든 사용자에게 Zone Transfer가 허용된 경우
                else:
                    return "취약"  # Zone Transfer 설정이 없는 경우 (기본적으로 취약)

        else:
            return "양호"  # DNS 설정 파일이 없으면 DNS 서비스를 사용하지 않는 것으로 간주

    except Exception as e:
        print(f"오류 발생: {e}")
        return "점검불가"  # 기타 오류 발생 시

if __name__ == "__main__":
    # 진단 담당자 입력 받기 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    
    # DNS Zone Transfer 설정 점검
    status = check_zone_transfer()
    
    # 진단 결과 JSON 형식으로 생성
    result = {
        "카테고리": "서비스 관리",
        "항목 설명": "DNS Zone Transfer 설정",
        "중요도": "상",
        "진단 결과": status, 
        "진단 파일명": "34.py",
        "진단 담당자": 담당자,
        "진단 시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "코드": "U-34"  
    }

    # 진단 결과 JSON 형식으로 출력
    print(json.dumps(result, ensure_ascii=False, indent=4))
