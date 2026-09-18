from dataclasses import dataclass
import random


@dataclass
class GridTelemetry:
    timestamp: int
    load_kw: float
    capacity_kw: float

    @property
    def utilization(self) -> float:
        return (self.load_kw / self.capacity_kw) * 100


class GridSimulator:
    """
    Simulates localized grid telemetry.

    In a production system, this data would come from
    smart meters / grid sensors rather than random generation.
    """

    def __init__(self, capacity_kw: float = 100.0):
        self.capacity_kw = capacity_kw
        self.base_load_kw = 55.0

    def generate(self, timestamp: int) -> GridTelemetry:
        variation = random.uniform(-5, 5)

        # Simulate occasional demand spikes
        if random.random() < 0.25:
            variation += random.uniform(15, 30)

        load = max(
            0,
            min(self.capacity_kw * 1.10,
                self.base_load_kw + variation)
        )

        return GridTelemetry(
            timestamp=timestamp,
            load_kw=round(load, 2),
            capacity_kw=self.capacity_kw
        )
