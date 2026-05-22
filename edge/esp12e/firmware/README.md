# ESP12-E 릴레이 펌웨어 계약

MVP 펌웨어는 독립적인 릴레이 2채널을 노출하고 운영 상태를 발행해야 합니다.

## MQTT 토픽

- 명령: `home/relay/{device_id}/{channel}/set`
- 상태: `home/relay/{device_id}/state`
- 가용성: `home/relay/{device_id}/availability`

## 상태 payload

```json
{
  "device_id": "relay_esp12e_room_a",
  "channels": {"ch1": false, "ch2": true},
  "online": true,
  "firmware": "0.1.0",
  "rssi": -61,
  "last_command_result": "ch2:on"
}
```

중앙 예약은 백엔드/Home Assistant 계층에 남겨둡니다. ESP12-E가 예약 작업의 진실 원천이
되어서는 안 됩니다.
