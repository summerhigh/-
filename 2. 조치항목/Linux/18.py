import os
import sys
import subprocess
import json
from datetime import datetime

# 접속 IP 및 포트 제한 설정 조치 함수
def remediate_ip_port_restrictions():
    try:
        # TCP Wrapper 설정 - /etc/hosts.deny에서 모든 접속을 차단하고, /etc/hosts.allow에서 필요한 접속 허용
        with open('/etc/hosts.deny', 'w') as deny_file:
            deny_file.write("ALL:ALL\n")  # 모든 접속 차단
        with open('/etc/hosts.allow', 'w') as allow_file:
            allow_file.write("sshd: 192.168.0.148, 192.168.0.6\n")  # SSH 접속 허용 IP 추가

        # iptables 설정 - SSH 포트(22번 포트)에 대한 제한
        subprocess.run(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '22', '-s', '192.168.1.0/24', '-j', 'ACCEPT'], check=False)
        subprocess.run(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '22', '-j', 'DROP'], check=False)
        subprocess.run(['/etc/init.d/iptables', 'save'], check=False)

        # IPFilter 설정 (솔라리스, AIX 등 리눅스가 아닌 경우에만 설정)
        if not os.path.exists('/etc/debian_version'):  # Linux(Debian 계열이 아닌 경우에만 적용)
            with open('/etc/ipf/ipf.conf', 'a') as ipf_conf:
                ipf_conf.write("pass in quick proto tcp from 192.168.1.0/24 to any port = 22 keep state\n")
                ipf_conf.write("block in quick proto tcp from any to any port = 22 keep state\n")
            subprocess.run(['ipf', '-Fa', '-f', '/etc/ipf/ipf.conf'], check=False)  # IPFilter 재시작 명령

        return "완료"
    except Exception as e:
        return "미완료"

# 접속 IP 및 포트 제한 설정 점검 함수 (재진단)
def check_ip_port_restrictions():
    try:
        # TCP Wrapper 설정 파일 점검
        tcp_wrapper_files = ['/etc/hosts.allow', '/etc/hosts.deny']
        tcp_wrapper_configured = False

        for file in tcp_wrapper_files:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    content = f.read().strip()
                    if content and '+' not in content:  # 설정이 있고, 모든 호스트 허용(+) 설정이 아닌 경우
                        tcp_wrapper_configured = True

        # iptables 규칙 확인 (리눅스 커널 방화벽)
        iptables_check = subprocess.run(['iptables', '-L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        iptables_configured = iptables_check.returncode == 0 and 'ACCEPT' in iptables_check.stdout

        # IPFilter 설정 확인 (솔라리스, AIX 등 리눅스가 아닌 경우에만 확인)
        ipfilter_configured = False
        if not os.path.exists('/etc/debian_version'):  # Linux(Debian 계열이 아닌 경우만 확인)
            try:
                ipfilter_check = subprocess.run(['ipfstat', '-io'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                ipfilter_configured = ipfilter_check.returncode == 0 and ipfilter_check.stdout.strip() != ''
            except FileNotFoundError:
                return "점검불가"

        # 각 조건을 만족하는지 여부 확인
        if tcp_wrapper_configured or iptables_configured or ipfilter_configured:
            return {"status": "양호", "message": "접속 IP 및 포트 제한이 적절히 설정되었습니다."}

        return {"status": "취약", "message": "접속 IP 및 포트 제한이 설정되지 않았습니다."}
    except Exception as e:
        return {"status": "점검불가", "message": "접속 IP 및 포트 제한 점검 중 오류가 발생했습니다."}

# 메인 함수
def main():
    # 조치 담당자 입력 (런처에서 전달받음)
    담당자 = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # 먼저 조치를 수행
    remediation_result = remediate_ip_port_restrictions()

    # 조치 수행 시간 기록
    remediation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 재진단 수행
    diagnosis_result = check_ip_port_restrictions()

    # 최종 출력
    account_result = {
        "카테고리": "파일 및 디렉토리 관리",
        "항목 설명": "접속 IP 및 포트 제한",
        "중요도": "상",
        "진단 결과": "취약",
        "조치 결과": remediation_result,
        "재진단 결과": diagnosis_result["status"],
        "메시지": diagnosis_result["message"],
        "조치 파일명": "18.py",
        "조치 담당자": 담당자,
        "조치 시각": remediation_date,
        "코드": "U-18"
    }

    # 최종 결과 출력
    print(json.dumps(account_result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
