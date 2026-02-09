import streamlit as st
import math

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AASHTO 1993 Pavement Design", page_icon="🛣️", layout="wide")

st.title("🛣️ AASHTO 1993 Pavement Structure Number Calculator")
st.markdown("### คำนวณ Structure Number (SN) สำหรับผิวทางลาดยาง")

# คำอธิบาย
with st.expander("ℹ️ คำอธิบายและสูตร AASHTO 1993"):
    st.markdown("""
    **AASHTO 1993 Design Equation:**
    
    log₁₀(W₁₈) = Z_R × S₀ + 9.36 × log₁₀(SN + 1) - 0.20 + [log₁₀(ΔPSI/(4.2 - 1.5))] / [0.40 + 1094/(SN + 1)^5.19] + 2.32 × log₁₀(M_R) - 8.07
    
    **Structure Number (SN):**
    
    SN = a₁ × D₁ + a₂ × D₂ × m₂ + a₃ × D₃ × m₃
    
    โดยที่:
    - a₁, a₂, a₃ = Layer coefficients (ค่าสัมประสิทธิ์ชั้น)
    - D₁, D₂, D₃ = Layer thickness in inches (ความหนาชั้น)
    - m₂, m₃ = Drainage coefficients (ค่าสัมประสิทธิ์การระบายน้ำ)
    
    **ชั้นทาง:**
    1. Surface/Asphalt Concrete (ผิวทางแอสฟัลต์)
    2. Base Course (ชั้นหินคลุก)
    3. Subbase Course (ชั้นดินถม)
    """)

# แบ่งคอลัมน์
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Input Parameters")
    
    st.markdown("#### Traffic & Design Parameters")
    w18 = st.number_input("W₁₈ - 18-kip ESAL (ล้านครั้ง)", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    w18 = w18 * 1_000_000  # แปลงเป็นครั้ง
    
    reliability = st.slider("Reliability (R) - ความเชื่อถือได้ (%)", 50, 99, 90, 1)
    
    # Z_R values based on reliability
    zr_values = {50: 0.0, 75: -0.674, 85: -1.037, 90: -1.282, 95: -1.645, 99: -2.327, 99.9: -3.090}
    if reliability in zr_values:
        zr = zr_values[reliability]
    else:
        # Linear interpolation
        zr = -1.282 if reliability == 90 else -1.645
    
    st.info(f"Z_R = {zr:.3f}")
    
    so = st.number_input("S₀ - Standard Deviation", min_value=0.1, max_value=1.0, value=0.45, step=0.01)
    
    psi_initial = st.number_input("p₀ - Initial PSI", min_value=1.5, max_value=5.0, value=4.2, step=0.1)
    psi_terminal = st.number_input("p_t - Terminal PSI", min_value=1.5, max_value=5.0, value=2.5, step=0.1)
    delta_psi = psi_initial - psi_terminal
    
    mr = st.number_input("M_R - Resilient Modulus (psi)", min_value=1000, max_value=50000, value=7500, step=500)

with col2:
    st.subheader("🏗️ Layer Properties")
    
    st.markdown("#### Layer 1: Asphalt Concrete (ผิวทางแอสฟัลต์)")
    a1 = st.number_input("a₁ - Layer Coefficient", min_value=0.0, max_value=1.0, value=0.44, step=0.01, key="a1")
    d1 = st.number_input("D₁ - Thickness (inches)", min_value=0.0, max_value=20.0, value=4.0, step=0.5, key="d1")
    
    st.markdown("#### Layer 2: Base Course (ชั้นหินคลุก)")
    a2 = st.number_input("a₂ - Layer Coefficient", min_value=0.0, max_value=1.0, value=0.14, step=0.01, key="a2")
    d2 = st.number_input("D₂ - Thickness (inches)", min_value=0.0, max_value=30.0, value=6.0, step=0.5, key="d2")
    m2 = st.number_input("m₂ - Drainage Coefficient", min_value=0.0, max_value=2.0, value=1.0, step=0.05, key="m2")
    
    st.markdown("#### Layer 3: Subbase Course (ชั้นดินถม)")
    a3 = st.number_input("a₃ - Layer Coefficient", min_value=0.0, max_value=1.0, value=0.11, step=0.01, key="a3")
    d3 = st.number_input("D₃ - Thickness (inches)", min_value=0.0, max_value=40.0, value=8.0, step=0.5, key="d3")
    m3 = st.number_input("m₃ - Drainage Coefficient", min_value=0.0, max_value=2.0, value=1.0, step=0.05, key="m3")

# คำนวณ Structure Number
st.markdown("---")
st.subheader("🎯 Results / ผลการคำนวณ")

# คำนวณ SN
sn_calculated = a1 * d1 + a2 * d2 * m2 + a3 * d3 * m3

col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    st.metric("Layer 1 Contribution", f"{a1 * d1:.2f}")
    
with col_res2:
    st.metric("Layer 2 Contribution", f"{a2 * d2 * m2:.2f}")
    
with col_res3:
    st.metric("Layer 3 Contribution", f"{a3 * d3 * m3:.2f}")

st.markdown("### 📈 Total Structure Number (SN)")
st.success(f"## SN = {sn_calculated:.2f}")

# คำนวณ Required SN จาก AASHTO equation (iterative method)
st.markdown("---")
st.subheader("🔍 Design Verification")

# ฟังก์ชันคำนวณ W18 จาก SN
def calculate_w18_from_sn(sn, zr, so, delta_psi, mr):
    try:
        # AASHTO 1993 equation
        log_w18 = (zr * so + 9.36 * math.log10(sn + 1) - 0.20 + 
                   (math.log10(delta_psi / (4.2 - 1.5))) / 
                   (0.40 + 1094 / ((sn + 1) ** 5.19)) + 
                   2.32 * math.log10(mr) - 8.07)
        return 10 ** log_w18
    except:
        return 0

# หา Required SN โดยการ iterate
required_sn = 1.0
for i in range(100):
    w18_calc = calculate_w18_from_sn(required_sn, zr, so, delta_psi, mr)
    if w18_calc >= w18:
        break
    required_sn += 0.01

col_ver1, col_ver2, col_ver3 = st.columns(3)

with col_ver1:
    st.metric("Required SN", f"{required_sn:.2f}", 
              delta=None, delta_color="normal")

with col_ver2:
    st.metric("Provided SN", f"{sn_calculated:.2f}", 
              delta=None, delta_color="normal")

with col_ver3:
    difference = sn_calculated - required_sn
    st.metric("Difference", f"{difference:.2f}", 
              delta=f"{difference:.2f}", 
              delta_color="normal" if difference >= 0 else "inverse")

# แสดงผลการตรวจสอบ
if sn_calculated >= required_sn:
    st.success(f"✅ **Design is ADEQUATE** - Provided SN ({sn_calculated:.2f}) ≥ Required SN ({required_sn:.2f})")
else:
    st.error(f"❌ **Design is INADEQUATE** - Provided SN ({sn_calculated:.2f}) < Required SN ({required_sn:.2f})")
    st.warning(f"⚠️ Need to increase thickness by approximately {(required_sn - sn_calculated):.2f} SN units")

# ตารางสรุป
st.markdown("---")
st.subheader("📋 Design Summary")

summary_data = {
    "Parameter": [
        "Design ESAL (W₁₈)",
        "Reliability (%)",
        "Standard Deviation (S₀)",
        "ΔPSI",
        "Resilient Modulus (psi)",
        "Required SN",
        "Provided SN",
        "Status"
    ],
    "Value": [
        f"{w18/1_000_000:.2f} million",
        f"{reliability}%",
        f"{so:.2f}",
        f"{delta_psi:.1f}",
        f"{mr:,}",
        f"{required_sn:.2f}",
        f"{sn_calculated:.2f}",
        "✅ ADEQUATE" if sn_calculated >= required_sn else "❌ INADEQUATE"
    ]
}

st.table(summary_data)

# Thickness in cm
st.markdown("---")
st.subheader("📏 Layer Thickness (Metric)")
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.info(f"**Layer 1 (AC):** {d1 * 2.54:.1f} cm")
with col_m2:
    st.info(f"**Layer 2 (Base):** {d2 * 2.54:.1f} cm")
with col_m3:
    st.info(f"**Layer 3 (Subbase):** {d3 * 2.54:.1f} cm")

st.info(f"**Total Pavement Thickness:** {(d1 + d2 + d3) * 2.54:.1f} cm ({d1 + d2 + d3:.1f} inches)")

# Footer
st.markdown("---")
st.caption("AASHTO 1993 Pavement Design Method | Structure Number Calculator")
