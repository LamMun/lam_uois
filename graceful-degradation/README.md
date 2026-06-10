# VSR Graceful Degradation - International Latency Circuit Breaker

This repository contribution implements the VSR task **Graceful Degradation**.

The goal is to keep the application usable for Vietnamese users when international connectivity is degraded by undersea cable incidents.

## Practical deliverable

`health_check.py` pings a global external IP every 10 seconds. If latency is higher than 500 ms, or if the ping fails, it switches the app into `LOCAL_ONLY` mode by editing `app_config.json`.

## Files

- `health_check.py` - health-check and circuit breaker script
- `app_config.json` - configuration flag used by the application
- `frontend_local_only_example.js` - example app logic for using the flag
- `VSR_Graceful_Degradation_Report.md` - report for the task
- `VSR_Graceful_Degradation_Report.docx` - Word version of the report

## Run one check

```bash
python health_check.py --once
```

## Run continuously

```bash
python health_check.py
```

## Simulate a cable cut

```bash
python health_check.py --once --simulate-latency 800
```

Expected result in `app_config.json`:

```json
"LOCAL_ONLY": true
```

## Simulate recovery

```bash
python health_check.py --once --simulate-latency 50
```

Expected result in `app_config.json`:

```json
"LOCAL_ONLY": false
```

## Suggested GitHub location

Copy these files into the root of the group `_uois` repository, similar to the other submitted VSR task files.
