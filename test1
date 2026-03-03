import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

st.set_page_config(page_title="AASHTO 1993 SN Calculator")

st.title("AASHTO 1993 Flexible Pavement Design")
st.subheader("Structural Number (SN) Calculator")

st.latex(r'''
\log_{10}(W_{18}) =
Z_r S_o +
9.36 \log_{10}(SN+1) - 0.20 +
\frac{\log_{10}\left(\frac{\Delta PSI}{4.2-1.5}\right)}
{0.40 + \frac{1094}{(SN+1)^{5.19}}}
+ 2.32 \log_{10}(M_r) - 8.07
''')

# =========================
# INPUT SECTION
# =========================

st.sidebar.header("Input Parameters")

W18 = st.sidebar.number_input("Traffic (W18, ESALs)", value=1000000.0)
ZR = st.sidebar.number_input("Reliability Factor (Zr)", value=-1.645)
So = st.sidebar.number_input("Overall Std. Deviation (So)", value=0.45)
deltaPSI = st.sidebar.number_input("Delta PSI", value=1.7)
Mr = st.sidebar.number_input("Resilient Modulus Mr (psi)", value=8000.0)

# =========================
# SOLVE SN
# =========================

def equation(SN):
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

SN_initial_guess = 3
SN_solution = fsolve(equation, SN_initial_guess)

st.subheader("Result")
st.success(f"Structural Number (SN) = {SN_solution[0]:.3f}")

# =========================
# GRAPH SECTION
# =========================

SN_range = np.linspace(1, 7, 100)
values = [equation(sn) for sn in SN_range]

plt.figure()
plt.axhline(0)
plt.plot(SN_range, values)
plt.xlabel("Structural Number (SN)")
plt.ylabel("Equation Balance")
plt.title("SN Iteration Curve")

st.pyplot(plt)
