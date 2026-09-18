```python
import streamlit as st
import random
import time
from dataclasses import dataclass
from collections import deque

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="GridPulse EV",
    page_icon="⚡",
    layout="wide"
)

# ---------------------------------------------------------
# DATA MODELS
# ---------------------------------------------------------

@dataclass
class EVSE:
    evse_id: str
    max_power_kw: float
    current_power_kw: float
    connected: bool = True


# ---------------------------------------------------------
# INITIAL STATE
# ---------------------------------------------------------

if "grid_load" not in st.session_state:
    st.session_state.grid_load = 62.0

if "evses" not in st.session_state:
    st.session_state.evses = [
        EVSE("EVSE-01", 11.0, 11.0),
        EVSE("EVSE-02", 7.0, 7.0),
        EVSE("EVSE-03", 11.0, 11.0),
        EVSE("EVSE-04", 22.0, 22.0),
    ]

if "history" not in st.session_state:
    st.session_state.history = deque(maxlen=30)

if "running" not in st.session_state:
    st.session_state.running = False


# ---------------------------------------------------------
# GRID LOGIC
# ---------------------------------------------------------

GRID_CAPACITY = 100.0

WARNING_THRESHOLD = 80.0
CRITICAL_THRESHOLD = 90.0
EMERGENCY_THRESHOLD = 100.0


def calculate_decision(utilization):

    if utilization >= EMERGENCY_THRESHOLD:
        return (
            "EMERGENCY THROTTLE",
            0.40,
            "Grid capacity exceeded"
        )

    elif utilization >= CRITICAL_THRESHOLD:
        return (
            "CRITICAL THROTTLE",
            0.60,
            "Grid utilization above critical threshold"
        )

    elif utilization >= WARNING_THRESHOLD:
        return (
            "SOFT THROTTLE",
            0.80,
            "Grid utilization approaching capacity"
        )

    return (
        "NORMAL CHARGING",
        1.00,
        "Grid operating within safe range"
    )


def apply_charging_limit(power_limit):

    for evse in st.session_state.evses:

        if evse.connected:
            evse.current_power_kw = round(
                evse.max_power_kw * power_limit,
                2
            )


def generate_grid_load():

    current = st.session_state.grid_load

    change = random.uniform(-5, 5)

    # Occasionally create a grid spike
    if random.random() < 0.25:
        change += random.uniform(12, 25)

    new_load = current + change

    return max(
        40,
        min(105, new_load)
    )


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("⚡ GridPulse EV")
st.subheader("IoT-Driven Smart Charging Platform")

st.markdown(
    """
    **Sense → Decide → Act**

    A simulated intelligent automation loop that monitors
    localized grid conditions and dynamically adjusts EV
    charging power.
    """
)

st.divider()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("Simulation Control")

    st.session_state.running = st.toggle(
        "Run simulation",
        value=st.session_state.running
    )

    st.markdown("---")

    st.subheader("Grid Configuration")

    grid_capacity = st.number_input(
        "Grid Capacity (kW)",
        min_value=50.0,
        max_value=500.0,
        value=100.0,
        step=10.0
    )

    st.markdown("---")

    st.caption(
        "This is a simulation prototype. "
        "A production system would receive telemetry "
        "from real grid sensors and communicate with "
        "EVSE hardware through OCPP."
    )


# ---------------------------------------------------------
# TELEMETRY UPDATE
# ---------------------------------------------------------

GRID_CAPACITY = grid_capacity

st.session_state.grid_load = generate_grid_load()

utilization = (
    st.session_state.grid_load /
    GRID_CAPACITY
) * 100

decision, power_limit, reason = calculate_decision(
    utilization
)

apply_charging_limit(power_limit)

charging_load = sum(
    evse.current_power_kw
    for evse in st.session_state.evses
    if evse.connected
)

peak_reduction = max(
    0,
    (51.0 - charging_load) / 51.0 * 100
)

st.session_state.history.append({
    "grid": st.session_state.grid_load,
    "charging": charging_load,
    "utilization": utilization
})


# ---------------------------------------------------------
# TOP METRICS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Grid Load",
        f"{st.session_state.grid_load:.1f} kW"
    )

with col2:
    st.metric(
        "Grid Utilization",
        f"{utilization:.1f}%"
    )

with col3:
    st.metric(
        "EV Charging Load",
        f"{charging_load:.1f} kW"
    )

with col4:
    st.metric(
        "Peak Load Reduction",
        f"{peak_reduction:.1f}%"
    )


st.divider()


# ---------------------------------------------------------
# AUTOMATION STATUS
# ---------------------------------------------------------

st.subheader("🤖 Automation Engine")

status_col, decision_col = st.columns([1, 2])

with status_col:

    if decision == "NORMAL CHARGING":
        st.success("● NORMAL")

    elif decision == "SOFT THROTTLE":
        st.warning("● SOFT THROTTLE")

    elif decision == "CRITICAL THROTTLE":
        st.error("● CRITICAL THROTTLE")

    else:
        st.error("● EMERGENCY THROTTLE")


with decision_col:

    st.markdown(
        f"""
        **Decision:** `{decision}`

        **Charging Power Limit:** `{power_limit * 100:.0f}%`

        **Reason:** {reason}
        """
    )


st.divider()


# ---------------------------------------------------------
# EVSE STATUS
# ---------------------------------------------------------

st.subheader("🔌 EVSE Charging Stations")

cols = st.columns(len(st.session_state.evses))

for col, evse in zip(
    cols,
    st.session_state.evses
):

    with col:

        st.markdown(
            f"### {evse.evse_id}"
        )

        st.metric(
            "Current Power",
            f"{evse.current_power_kw:.1f} kW"
        )

        st.caption(
            f"Maximum: {evse.max_power_kw:.1f} kW"
        )

        if evse.current_power_kw < evse.max_power_kw:
            st.warning("Power throttled")
        else:
            st.success("Full power")


st.divider()


# ---------------------------------------------------------
# LOAD GRAPH
# ---------------------------------------------------------

st.subheader("📈 Real-Time System Load")

if len(st.session_state.history) > 0:

    chart_data = {
        "Grid Load (kW)": [
            item["grid"]
            for item in st.session_state.history
        ],
        "EV Charging Load (kW)": [
            item["charging"]
            for item in st.session_state.history
        ]
    }

    st.line_chart(chart_data)


# ---------------------------------------------------------
# ARCHITECTURE FLOW
# ---------------------------------------------------------

st.divider()

st.subheader("🔄 GridPulse Feedback Loop")

st.markdown(
    """
    **Grid Telemetry**
    ↓
    **Utilization Calculation**
    ↓
    **Automation / Rules Engine**
    ↓
    **Charging Power Decision**
    ↓
    **EVSE Power Adjustment**
    ↓
    **Reduced Grid Stress**
    ↓
    **New Telemetry**
    ↺
    """
)


# ---------------------------------------------------------
# AUTO REFRESH
# ---------------------------------------------------------

if st.session_state.running:

    time.sleep(1)

    st.rerun()
```
