import time

from grid_simulator import GridSimulator
from rules_engine import GridRulesEngine
from evse_simulator import EVSESimulator


def print_header():
    print("=" * 78)
    print("GRIDPULSE EV — SMART CHARGING SIMULATION")
    print("=" * 78)


def run():
    grid = GridSimulator(capacity_kw=100)
    rules = GridRulesEngine()
    evse_system = EVSESimulator()

    print_header()

    for timestamp in range(1, 31):

        telemetry = grid.generate(timestamp)

        decision = rules.evaluate(
            telemetry.utilization
        )

        if decision.power_limit < 1.0:
            evse_system.apply_power_limit(
                decision.power_limit
            )
        else:
            evse_system.restore_normal_charging()

        charging_load = evse_system.total_load_kw()

        print(
            f"\nTimestep: {timestamp:02d}"
        )

        print(
            f"Grid Load:       {telemetry.load_kw:6.2f} kW"
        )

        print(
            f"Grid Capacity:   {telemetry.capacity_kw:6.2f} kW"
        )

        print(
            f"Utilization:     {telemetry.utilization:6.2f}%"
        )

        print(
            f"EV Charging:     {charging_load:6.2f} kW"
        )

        print(
            f"Decision:        {decision.action}"
        )

        print(
            f"Power Limit:     {decision.power_limit * 100:6.0f}%"
        )

        print(
            f"Reason:          {decision.reason}"
        )

        print("-" * 78)

        time.sleep(0.5)


if __name__ == "__main__":
    run()
