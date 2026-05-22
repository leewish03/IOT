# Open WebUI MCP 설정

서버 배포 후 Open WebUI 쪽 설정을 이 폴더에 둡니다.

## 백엔드 엔드포인트

- API 상태 확인: `http://orchestrator:8080/health`
- Tool 카탈로그: `http://orchestrator:8080/tools`
- Resource 카탈로그: `http://orchestrator:8080/resources`
- Prompt 카탈로그: `http://orchestrator:8080/prompts`

## MCP 연동 메모

`backend.app.mcp_server.McpCatalogServer`에는 안정적인 Resources, Tools, Prompts 계약이
들어 있습니다. 배포 환경에서 MCP SDK transport를 사용한다면 Tool 로직을 중복 구현하지
말고 이 클래스를 감싸서 사용합니다.

현재 구현은 REST API와 MCP 스타일 카탈로그를 제공하는 단계이며, Open WebUI가 직접 붙는
실제 MCP transport(stdio/SSE/streamable HTTP)는 아직 포함되어 있지 않습니다. Open WebUI가
같은 Docker Compose 네트워크 안에서 실행될 때는 `http://orchestrator:8080`을 사용할 수
있고, 별도 호스트에서 실행될 때는 `http://<ubuntu-host>:8080` 형태의 실제 서버 주소를
사용해야 합니다.

Open WebUI에서 검증할 대표 프롬프트:

- `내일 7시에 깨워`
- `오늘 밤 11시에 ch2 꺼`
- `왜 오늘 알람이 울렸지`
