import streamlit as st
import matplotlib.pyplot as plt
from tools import figure_conversion

# Page structure
st.sidebar.success("Select an object from the pull down menu")
st.header('Object selection')

spec = st.session_state['spec']
input_line = 'H1_6563A'

# Spectrum plot
st.write(f'{st.session_state["obj"]} spectrum')
fig_spec = plt.figure()
spec.plot.spectrum(in_fig=fig_spec, include_fits=True)
figure_conversion(fig_spec, static_fig=True)

