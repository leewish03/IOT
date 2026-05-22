# 운영

## 정책 변경 흐름

1. `policies/` 아래 YAML을 수정합니다.
2. 백엔드 테스트 또는 서비스 시작 과정에서 정책 검증을 실행합니다.
3. 활성 레지스트리가 새 파일을 읽도록 백엔드를 reload/redeploy합니다.

## 감사 로그

Tool 호출은 `data/audit.jsonl`에 JSON Lines 형식으로 추가됩니다. 각 항목에는 actor,
source, tool name, 검증된 입력, 결과, timestamp, correlation id가 포함됩니다.

## 하드웨어 적용 체크리스트

- ESP12-E 릴레이 보드 전원과 GPIO 매핑을 확인합니다.
- MQTT broker 주소와 자격 증명을 확인합니다.
- Home Assistant entity/script 이름을 확인합니다.
- Ubuntu 서버에서 백엔드가 Home Assistant와 MQTT broker에 접근할 수 있는지 확인합니다.
