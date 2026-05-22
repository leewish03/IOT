# Jarvis Full Stack — 계획 (2026-05)

## Goal

실사용 가능한 **Pi 24h 오케스트레이터 + OpenCV 장면 + AI 판단 + Supabase Auth + Render 대시보드** 일체.

## 완료 범위

| 영역 | 내용 |
|------|------|
| Phase 0·3·4·5 | 릴레이·HA·센서·채팅·음성·대시보드 |
| OpenCV | 사람·자세·이동·구역 → JSON만 LLM |
| 실시간 | `/api/scene/stream` SSE, Pi `CAMERA_DEVICE` |
| Supabase | Auth(이메일/매직링크), RLS, chat/vision/scene_events |
| Pi 배포 | `scripts/pi-install.sh`, systemd, docker-compose |
| Render | `render.yaml` + env 체크리스트 |

## 비전 파이프라인

```
카메라 → OpenCV (backend) → SceneSnapshot JSON → LLM 판단 → MCP 도구
```

원본 픽셀은 LLM에 전송하지 않음.

## 배포

- **Pi:** [docs/06-guide/pi-deploy.md](../06-guide/pi-deploy.md)
- **Render + Supabase:** [docs/06-guide/deploy-render-supabase.md](../06-guide/deploy-render-supabase.md)
