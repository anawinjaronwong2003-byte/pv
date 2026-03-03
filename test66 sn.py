import streamlit as st
import math
import pandas as pd

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AASHTO 1993 Pavement Design Pro",
    page_icon="🛣️",
    layout="wide"
)

st.title("🛣️ AASHTO 1993 Flexible Pavement Design")
st.markdown("### Complete Structural Analysis Tool")

st.markdown("---")

# ==========================================
# FUNCTIONS
# ==========================================

def get_zr(reliability):
    table = {
        50: 0.000, 75: -0.674, 80: -0.841,
        85: -1.037, 90: -1.282, 95: -1.645,
        98: -2.054, 99: -2.327
    }
    keys = sorted(table.keys())
    if reliability in table:
        return table[reliability]
    for i in range(len(keys)-1):
        if keys[i] <= reliability <= keys[i+1]:
            r1, r2 = keys[i], keys[i+1]
            z1, z2 = table[r1], table[r2]
            return z1 + (z2 - z1)*(reliability-r1)/(r2-r1)
    return -1.282


def solve_required_sn(zr, so, delta_psi, mr, w18):
    low, high = 0.1, 10
    for _ in range(100):
        mid = (low + high)/2
        left = math.log10(w18)
        right = (
            zr * so
            + 9.36 * math.log10(mid + 1)
            - 0.20
            + (math.log10(delta_psi / (4.2 - 1.5)))
            / (0.40 + 1094 / ((mid + 1) ** 5.19))
            + 2.32 * math.log10(mr)
            - 8.07
        )
        if left - right > 0:
            low = mid
        else:
            high = mid
    return round((low + high)/2, 3)


# ==========================================
# INPUT SECTION
# ==========================================

st.header("📊 Step 1: Traffic & Reliability")

col1, col2 = st.columns(2)

with col1:
    w18_million = st.number_input(
        "Design Traffic W18 (Million ESAL)",
        0.01, 200.0, 5.0
    )
    st.caption("Typical Highway: 1 – 30 million ESAL")

    reliability = st.slider("Reliability (%)", 50, 99, 90)
    st.caption("Recommended: 85 – 95 %")

with col2:
    so = st.number_input("Overall Std. Deviation (So)", 0.30, 0.60, 0.45)
    st.caption("Flexible pavement: 0.40 – 0.50")

    mr = st.number_input("Subgrade Resilient Modulus Mr (psi)", 3000, 30000, 8000)
    st.caption("Soft soil: 3000–8000 | Good soil: >10000")

# ------------------------------------------

st.header("📉 Step 2: Serviceability")

col3, col4 = st.columns(2)

with col3:
    psi_initial = st.number_input("Initial Serviceability (p0)", 4.0, 4.5, 4.2)

with col4:
    psi_terminal = st.number_input("Terminal Serviceability (pt)", 2.0, 3.0, 2.5)

delta_psi = psi_initial - psi_terminal

# ------------------------------------------

st.header("🏗️ Step 3: Layer Properties")

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Surface")
    a1 = st.number_input("a1", 0.30, 0.50, 0.44)
    d1 = st.number_input("D1 (inch)", 1.0, 10.0, 4.0)

with c2:
    st.subheader("Base")
    a2 = st.number_input("a2", 0.05, 0.30, 0.14)
    d2 = st.number_input("D2 (inch)", 2.0, 15.0, 6.0)
    m2 = st.number_input("m2", 0.5, 1.5, 1.0)

with c3:
    st.subheader("Subbase")
    a3 = st.number_input("a3", 0.05, 0.20, 0.11)
    d3 = st.number_input("D3 (inch)", 2.0, 20.0, 8.0)
    m3 = st.number_input("m3", 0.5, 1.5, 1.0)

# ==========================================
# CALCULATIONS
# ==========================================

w18 = w18_million * 1_000_000
zr = get_zr(reliability)
required_sn = solve_required_sn(zr, so, delta_psi, mr, w18)

surface_sn = a1*d1
base_sn = a2*d2*m2
subbase_sn = a3*d3*m3
provided_sn = surface_sn + base_sn + subbase_sn

difference = round(provided_sn - required_sn, 3)

# ==========================================
# RESULTS
# ==========================================

st.markdown("---")
st.header("📈 Structural Analysis Results")

r1, r2, r3 = st.columns(3)
r1.metric("Required SN", required_sn)
r2.metric("Provided SN", round(provided_sn,3))
r3.metric("Safety Margin", difference,
          delta=difference,
          delta_color="normal" if difference>=0 else "inverse")

# ------------------------------------------

st.subheader("📊 Layer Contribution")

total = provided_sn if provided_sn != 0 else 1

st.write(f"Surface Contribution: {surface_sn:.3f}  ({surface_sn/total*100:.1f}%)")
st.write(f"Base Contribution: {base_sn:.3f}  ({base_sn/total*100:.1f}%)")
st.write(f"Subbase Contribution: {subbase_sn:.3f}  ({subbase_sn/total*100:.1f}%)")

# ------------------------------------------

st.subheader("📐 Calculated Design Parameters")

st.write(f"Zr (Standard Normal Deviate) = {zr:.3f}")
st.write(f"ΔPSI (Serviceability Loss) = {delta_psi:.2f}")
st.write(f"log10(W18) = {math.log10(w18):.3f}")
st.write(f"log10(Mr) = {math.log10(mr):.3f}")

# ------------------------------------------

st.subheader("🧠 Engineering Interpretation")

if provided_sn >= required_sn:
    st.success("Design satisfies AASHTO 1993 requirement.")
    st.info("Structure has sufficient capacity for projected traffic.")
else:
    st.error("Design does NOT satisfy AASHTO requirement.")
    st.warning("Increase asphalt thickness or improve base quality.")

# ------------------------------------------

st.markdown("---")
st.subheader("📏 Thickness Summary (cm)")

st.write(f"Surface: {d1*2.54:.1f} cm")
st.write(f"Base: {d2*2.54:.1f} cm")
st.write(f"Subbase: {d3*2.54:.1f} cm")
st.write(f"Total Thickness: {(d1+d2+d3)*2.54:.1f} cm")

st.markdown("---")
st.caption("AASHTO 1993 Flexible Pavement Design | Advanced Engineering Version")
