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

st.title("🛣️ AASHTO 1993 Pavement Structure Number Calculator")
st.markdown("Advanced Flexible Pavement Design Verification Tool")

# ===============================
# HELPER FUNCTIONS
# ===============================

# Interpolate Zr from reliability
def get_zr(reliability):
    table = {
        50: 0.000,
        75: -0.674,
        80: -0.841,
        85: -1.037,
        90: -1.282,
        95: -1.645,
        98: -2.054,
        99: -2.327,
        99.9: -3.090
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


# AASHTO Equation → difference
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


# Solve SN using binary search
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
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Design Inputs")

    w18_million = st.number_input("Design ESAL (Million)", 0.01, 100.0, 1.0)
    w18 = w18_million * 1_000_000

    reliability = st.slider("Reliability (%)", 50.0, 99.9, 90.0, 0.1)
    zr = get_zr(reliability)
    st.info(f"Zr = {zr:.3f}")

    so = st.number_input("Overall Std. Deviation (So)", 0.1, 1.0, 0.45)
    psi_initial = st.number_input("Initial PSI (p0)", 1.5, 5.0, 4.2)
    psi_terminal = st.number_input("Terminal PSI (pt)", 1.5, 5.0, 2.5)

    delta_psi = psi_initial - psi_terminal
    st.write(f"ΔPSI = {delta_psi:.2f}")

    mr = st.number_input("Subgrade Resilient Modulus (psi)", 1000, 50000, 7500)

with col2:
    st.subheader("🏗️ Layer Configuration")

    a1 = st.number_input("a1 (Surface)", 0.0, 1.0, 0.44)
    d1 = st.number_input("D1 (inch)", 0.0, 20.0, 4.0)

    a2 = st.number_input("a2 (Base)", 0.0, 1.0, 0.14)
    d2 = st.number_input("D2 (inch)", 0.0, 30.0, 6.0)
    m2 = st.number_input("m2 (Drainage)", 0.0, 2.0, 1.0)

    a3 = st.number_input("a3 (Subbase)", 0.0, 1.0, 0.11)
    d3 = st.number_input("D3 (inch)", 0.0, 40.0, 8.0)
    m3 = st.number_input("m3 (Drainage)", 0.0, 2.0, 1.0)

# ===============================
# CALCULATIONS
# ===============================
st.markdown("---")
st.subheader("📈 Results")

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
st.markdown("---")

if provided_sn >= required_sn:
    st.success("✅ DESIGN ADEQUATE")
else:
    st.error("❌ DESIGN INADEQUATE")
    st.warning(f"Increase SN by approx. {abs(difference):.3f}")

# ===============================
# METRIC THICKNESS
# ===============================
st.markdown("---")
st.subheader("📏 Thickness in cm")

st.write(f"Surface: {d1*2.54:.1f} cm")
st.write(f"Base: {d2*2.54:.1f} cm")
st.write(f"Subbase: {d3*2.54:.1f} cm")
st.write(f"Total: {(d1+d2+d3)*2.54:.1f} cm")

st.markdown("---")
st.caption("AASHTO 1993 Flexible Pavement Design | Structural Number Method")
