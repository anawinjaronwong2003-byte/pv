import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==============================
# PAGE SETTING
# ==============================
st.set_page_config(page_title="AASHTO 1993 SN Calculator", layout="wide")
st.title("AASHTO 1993 Flexible Pavement Design")
st.subheader("Structural Number (SN) Calculator")

st.markdown("Design equation based on AASHTO 1993 Guide")

st.latex(r"""
\log_{10}(W_{18}) =
Z_r S_o +
9.36 \log_{10}(SN+1) - 0.20 +
\frac{\log_{10}\left(\frac{\Delta PSI}{4.2-1.5}\right)}
{0.40 + \frac{1094}{(SN+1)^{5.19}}}
+ 2.32 \log_{10}(M_r) - 8.07
""")

# ==============================
# INPUT
# ==============================
st.sidebar.header("Input Parameters")

W18 = st.sidebar.number_input("Traffic (W18) - ESALs", value=1000000.0)
ZR = st.sidebar.number_input("Reliability Factor (Zr)", value=-1.645)
So = st.sidebar.number_input("Overall Std. Deviation (So)", value=0.45)
deltaPSI = st.sidebar.number_input("Delta PSI", value=1.7)
Mr = st.sidebar.number_input("Resilient Modulus Mr (psi)", value=8000.0)

# ==============================
# EQUATION FUNCTION
# ==============================
def equation(SN):
    if SN <= 0:
        return 1e6
    left = np.log10(W18)
    right = (
        ZR * So
        + 9.36 * np.log10(SN + 1)
        - 0.20
        + (np.log10(deltaPSI / (4.2 - 1.5)))
        / (0.40 + (1094 / ((SN + 1) ** 5.19)))
        + 2.32 * np.log10(Mr)
        - 8.07
    )
    return left - right

# ==============================
# CALCULATION
# ==============================
if st.button("Calculate SN"):

    # ค้นหาค่า SN ที่ทำให้สมการเข้าใกล้ 0 มากที่สุด
    SN_values = np.linspace(0.1, 10, 20000)
    residuals = [abs(equation(sn)) for sn in SN_values]
    SN = SN_values[np.argmin(residuals)]

    st.success(f"Structural Number (SN) = {SN:.3f}")

    # แสดงค่าประกอบ
    st.markdown("### Calculation Breakdown")
    st.write("log10(W18) =", round(np.log10(W18), 4))
    st.write("Zr × So =", round(ZR * So, 4))
    st.write("2.32 log10(Mr) =", round(2.32 * np.log10(Mr), 4))

    # ==============================
    # GRAPH
    # ==============================
    st.markdown("### Solution Graph")

    fig, ax = plt.subplots()
    ax.axhline(0)
    ax.plot(SN_values, [equation(sn) for sn in SN_values])
    ax.set_xlabel("Structural Number (SN)")
    ax.set_ylabel("Equation Balance")
    ax.set_title("AASHTO 1993 SN Solution Curve")

    st.pyplot(fig)

st.markdown("---")
st.markdown("Developed for Flexible Pavement Design based on AASHTO 1993")
