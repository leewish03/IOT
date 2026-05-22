# MCP 계약

## Resources

- `home://devices/relay`
- `home://calendar/tomorrow`
- `home://alarm/next`
- `home://automation/active`
- `home://logs/recent`

## Tools

- `relay.turn_on(device_id?, channel)`
- `relay.turn_off(device_id?, channel)`
- `relay.get_state(device_id?)`
- `relay.schedule(device_id?, channel, action, execute_at)`
- `calendar.get_tomorrow()`
- `alarm.create(time, profile, label, linked_event_id?)`
- `alarm.update_profile(alarm_id, profile)`
- `system.explain_recent_action(time_window?)`
- `system.execute_due_schedules(now?)`
- `automation.prepare_class_day(profile?, offset_min?)`
- `system.status_summary()`

## Prompts

- `create-alarm`
- `prepare-class-day`
- `schedule-relay`
- `why-did-this-run`
- `status-summary`
