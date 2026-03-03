import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AASHTO 1993 SN Calculator",
    page_icon="🛣️",
    layout="wide"
)

st.title("AASHTO 1993 Flexible Pavement Design")
st.markdown("### Structural Number (SN) Calculator")

# ==========================================
# FORMULA DISPLAY
# ==========================================
st.latex(r'''
\log_{10}(W_{18}) =
Z_r S_o +
9.36 \log_{10}(SN+1) - 0.20 +
\frac{\log_{10}\left(\frac{\Delta PSI}{4.2-1.5}\right)}
{0.40 + \frac{1094}{(SN+1)^{5.19}}}
+ 2.32 \log_{10}(M_r) - 8.07
''')

# ==========================================
# SIDEBAR INPUT
# ==========================================
st.sidebar.header("Input Parameters")

W18 = st.sidebar.number_input("Traffic (W18) - ESALs", value=1_000_000.0, format="%.2f")
ZR = st.sidebar.number_input("Reliability Factor (Zr)", value=-1.645)
So = st.sidebar.number_input("Overall Standard Deviation (So)", value=0.45)
deltaPSI = st.sidebar.number_input("Delta PSI", value=1.7)
Mr = st.sidebar.number_input("Resilient Modulus Mr (psi)", value=8000.0)

# ==========================================
# EQUATION FUNCTION
# ==========================================
def aashto_equation(SN):
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


# ==========================================
# CALCULATION
# ==========================================
if st.button("Calculate SN"):

    try:
        SN_initial_guess = 3.0
        SN_solution = fsolve(aashto_equation, SN_initial_guess)
        SN = SN_solution[0]

        st.success(f"Structural Number (SN) = {SN:.3f}")

        st.markdown("### Calculation Components")
        st.write("log10(W18) =", round(np.log10(W18), 4))
        st.write("Zr × So =", round(ZR * So, 4))
        st.write("2.32 log10(Mr) =", round(2.32 * np.log10(Mr), 4))

        # ==========================================
        # GRAPH
        # ==========================================
        st.markdown("### SN Solution Graph")

        SN_range = np.linspace(1, 7, 300)
        values = [aashto_equation(sn) for sn in SN_range]

        fig, ax = plt.subplots()
        ax.axhline(0)
        ax.plot(SN_range, values)
        ax.set_xlabel("Structural Number (SN)")
        ax.set_ylabel("Equation Balance")
        ax.set_title("AASHTO 1993 SN Iteration Curve")

        st.pyplot(fig)

    except:
        st.error("Calculation error. Please verify input values.")
