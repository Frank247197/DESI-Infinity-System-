# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - REAL-TIME TELEMETRY & ALERTS
# System Health Metrics, Threshold Alerts & Monitoring Export
# ============================================================

import os
import time
from typing import Dict, Any, List

class TelemetryMonitor:
    """
    [CALC] Collects real-time operational telemetry, tracks active module states,
    and triggers threshold alerts for thermal/power envelopes (50 MW ceiling).
    """
    def __init__(self, max_power_mw: float = 50.0):
        self.max_power_mw = max_power_mw
        self.start_time = time.time()
        self.alerts: List[Dict[str, str]] = []

    def record_power_draw(self, current_mw: float) -> Dict[str, Any]:
        if current_mw < 0:
            raise ValueError("Power draw cannot be negative.")
        utilization_pct = (current_mw / self.max_power_mw) * 100.0
        status = "NOMINAL"
        if current_mw > self.max_power_mw:
            status = "CRITICAL_ENVELOPE_EXCEEDED"
            self.alerts.append({"level": "CRITICAL", "message": f"Power {current_mw} MW exceeds {self.max_power_mw} MW limit."})
        elif utilization_pct >= 85.0:
            status = "WARNING_HIGH_LOAD"
            self.alerts.append({"level": "WARNING", "message": f"Power utilization at {utilization_pct:.1f}%."})

        return {
            "current_mw": current_mw,
            "envelope_limit_mw": self.max_power_mw,
            "utilization_pct": round(utilization_pct, 2),
            "status": status
        }

    def export_prometheus_text(self, current_mw: float) -> str:
        uptime_sec = round(time.time() - self.start_time, 2)
        return (
            f"# HELP desi_system_uptime_seconds System uptime in seconds\n"
            f"# TYPE desi_system_uptime_seconds gauge\n"
            f"desi_system_uptime_seconds {uptime_sec}\n"
            f"# HELP desi_power_draw_mw Current power envelope draw in megawatts\n"
            f"# TYPE desi_power_draw_mw gauge\n"
            f"desi_power_draw_mw {current_mw}\n"
        )

if __name__ == "__main__":
    monitor = TelemetryMonitor(max_power_mw=50.0)
    print("Telemetry Check:", monitor.record_power_draw(32.5))
    print("\nPrometheus Export:\n" + monitor.export_prometheus_text(32.5))
