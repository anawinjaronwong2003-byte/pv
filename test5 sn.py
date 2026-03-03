import streamlit as st
import math

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="AASHTO 1993 Pavement Design",
    page_icon="🛣️",
    layout="wide"
)

st.title("🛣️ AASHTO 1993 Flexible Pavement Design")
st.markdown("### Structural Number (SN) Calculator with Design Guidance")

# ===============================
# HELPER FUNCTIONS
# ===============================

def get_zr(reliability):
    table = {
        50: 0.000, 75: -0.674, 80: -0.841,
        85: -1.037, 90: -1.282, 95: -1.645,
        98: -2.054, 99: -2.327
    }
    keys = sorted(table.keys())
    if reliability in table:
        return table[reliability]
    for i in range(len(keys) - 1):
        if keys[i] <= reliability <= keys[i + 1]:
            r1, r2 = keys[i], keys[i + 1]
            z1, z2 = table[r1], table[r2]
            return z1 + (z2 - z1) * (reliability - r1) / (r2 - r1)
    return -1.282


def aashto_equation(sn, zr, so, delta_psi, mr, w18):
    if sn <= 0:
        return 1e6
    try:
        left = math.log10(w18)
        right = (
            zr * so
            + 9.36 * math.log10(sn + 1)
            - 0.20
            + (math.log10(delta_psi / (4.2 - 1.5)))
            / (0.40 + 1094 / ((sn + 1) ** 5.19))
            + 2.32 * math.log10(mr)
            - 8.07
        )
        return left - right
    except:
        return 1e6


def solve_required_sn(zr, so, delta_psi, mr, w18):
    low, high = 0.1, 10
    for _ in range(100):
        mid = (low + high) / 2
        if aashto_equation(mid, zr, so, delta_psi, mr, w18) > 0:
            low = mid
        else:
            high = mid
    return round((low + high) / 2, 3)


# ===============================
# INPUT SECTION
# ===============================
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📊 Traffic & Design Parameters")

    w18_million = st.number_input(
        "Design ESAL (W₁₈) [Million ESAL]",
        min_value=0.01,
        max_value=200.0,
        value=1.0,
        help="Typical range: 0.1 – 50 million for most highways"
    )
    w18 = w18_million * 1_000_000

    reliability = st.slider(
        "Reliability (%)",
        50.0, 99.0, 90.0,
        help="Recommended: 85–95% for highways"
    )

    zr = get_zr(reliability)
    st.info(f"Computed Zr = {zr:.3f}")

    so = st.number_input(
        "Overall Standard Deviation (So)",
        0.30, 0.60, 0.45,
        help="Typical flexible pavement: 0.40–0.50"
    )

    psi_initial = st.number_input(
        "Initial Serviceability (p0)",
        4.0, 4.5, 4.2,
        help="Usually 4.2 for new asphalt pavement"
    )

    psi_terminal = st.number_input(
        "Terminal Serviceability (pt)",
        2.0, 3.0, 2.5,
        help="Commonly 2.0–2.5"
    )

    delta_psi = psi_initial - psi_terminal
    st.write(f"ΔPSI = {delta_psi:.2f}")

    mr = st.number_input(
        "Subgrade Resilient Modulus (Mr) [psi]",
        3000, 30000, 7500,
        help="Soft soil: 3000–8000 psi | Good soil: 10000+ psi"
    )

with col2:
    st.subheader("🏗️ Pavement Layer Configuration")

    st.markdown("**Surface Layer (Asphalt Concrete)**")
    a1 = st.number_input("a1 (0.40–0.44 typical)", 0.30, 0.50, 0.44)
    d1 = st.number_input("D1 Thickness (inch)", 1.0, 10.0, 4.0)

    st.markdown("**Base Layer**")
    a2 = st.number_input("a2 (0.10–0.20 typical)", 0.05, 0.30, 0.14)
    d2 = st.number_input("D2 Thickness (inch)", 2.0, 15.0, 6.0)
    m2 = st.number_input("m2 Drainage (0.8–1.4 typical)", 0.5, 1.5, 1.0)

    st.markdown("**Subbase Layer**")
    a3 = st.number_input("a3 (0.08–0.15 typical)", 0.05, 0.20, 0.11)
    d3 = st.number_input("D3 Thickness (inch)", 2.0, 20.0, 8.0)
    m3 = st.number_input("m3 Drainage (0.8–1.4 typical)", 0.5, 1.5, 1.0)


# ===============================
# RESULTS
# ===============================
st.markdown("---")
st.subheader("📈 Design Results")

provided_sn = a1 * d1 + a2 * d2 * m2 + a3 * d3 * m3
required_sn = solve_required_sn(zr, so, delta_psi, mr, w18)

colA, colB, colC = st.columns(3)

colA.metric("Required SN", required_sn)
colB.metric("Provided SN", round(provided_sn, 3))

difference = round(provided_sn - required_sn, 3)
colC.metric("Safety Margin", difference,
            delta=difference,
            delta_color="normal" if difference >= 0 else "inverse")

# ===============================
# DESIGN CHECK
# ===============================
if provided_sn >= required_sn:
    st.success("✅ DESIGN ADEQUATE")
else:
    st.error("❌ DESIGN INADEQUATE")
    st.warning(f"Increase SN by approx. {abs(difference):.3f}")

# ===============================
# THICKNESS SUMMARY
# ===============================
st.markdown("---")
st.subheader("📏 Thickness Summary")

st.write(f"Surface: {d1*2.54:.1f} cm")
st.write(f"Base: {d2*2.54:.1f} cm")
st.write(f"Subbase: {d3*2.54:.1f} cm")
st.write(f"Total Thickness: {(d1+d2+d3)*2.54:.1f} cm")

st.markdown("---")
st.caption("AASHTO 1993 Flexible Pavement Design Tool | Enhanced UX Version")
