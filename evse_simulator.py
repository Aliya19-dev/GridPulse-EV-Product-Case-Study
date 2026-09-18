from dataclasses import dataclass


@dataclass
class EVSE:
    evse_id: str
    max_power_kw: float
    current_power_kw: float
    target_power_kw: float
    connected: bool = True

    def set_power(self, power_kw: float):
        if not self.connected:
            self.current_power_kw = 0
            return

        self.target_power_kw = max(
            0,
            min(power_kw, self.max_power_kw)
        )

        self.current_power_kw = self.target_power_kw


class EVSESimulator:
    """
    Simulates a group of EV chargers.

    A real implementation would communicate with charging
    stations through OCPP 2.0.1 over WebSockets.
    """

    def __init__(self):
        self.chargers = [
            EVSE("EVSE-01", 11.0, 11.0, 11.0),
            EVSE("EVSE-02", 7.0, 7.0, 7.0),
            EVSE("EVSE-03", 11.0, 11.0, 11.0),
            EVSE("EVSE-04", 22.0, 22.0, 22.0),
        ]

    def total_load_kw(self) -> float:
        return round(
            sum(
                charger.current_power_kw
                for charger in self.chargers
                if charger.connected
            ),
            2
        )

    def apply_power_limit(self, percentage: float):
        """
        Apply proportional throttling to connected EVSEs.
        """

        for charger in self.chargers:
            if charger.connected:
                new_power = (
                    charger.max_power_kw * percentage
                )

                charger.set_power(new_power)

    def restore_normal_charging(self):
        for charger in self.chargers:
            if charger.connected:
                charger.set_power(charger.max_power_kw)
