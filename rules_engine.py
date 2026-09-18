from dataclasses import dataclass


@dataclass
class AutomationDecision:
    action: str
    power_limit: float
    reason: str


class GridRulesEngine:
    """
    Converts grid telemetry into charging-control decisions.

    The rules are intentionally deterministic so that the
    prototype is explainable and predictable.
    """

    def __init__(
        self,
        warning_threshold: float = 80.0,
        critical_threshold: float = 90.0,
        emergency_threshold: float = 100.0
    ):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.emergency_threshold = emergency_threshold

    def evaluate(self, utilization: float) -> AutomationDecision:

        if utilization >= self.emergency_threshold:
            return AutomationDecision(
                action="EMERGENCY_THROTTLE",
                power_limit=0.40,
                reason="Grid capacity exceeded"
            )

        if utilization >= self.critical_threshold:
            return AutomationDecision(
                action="CRITICAL_THROTTLE",
                power_limit=0.60,
                reason="Grid utilization above critical threshold"
            )

        if utilization >= self.warning_threshold:
            return AutomationDecision(
                action="SOFT_THROTTLE",
                power_limit=0.80,
                reason="Grid utilization approaching capacity"
            )

        return AutomationDecision(
            action="NORMAL_CHARGING",
            power_limit=1.00,
            reason="Grid operating within safe range"
        )
