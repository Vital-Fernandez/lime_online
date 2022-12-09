import streamlit as st
import matplotlib.pyplot as plt
from tools import figure_conversion

st_state = st.session_state


# Page structure
st.sidebar.success("Select a line from the pull down")
st.header('Line selection')

spec = st.session_state['spec']

if spec.log.size > 0:
    st.selectbox('Line label', spec.log.index.values, key='line')

    # Spectrum plot
    st.write(f'{st_state["line"]} fitting')
    fig_line = plt.figure()
    spec.plot.band(st_state["line"], in_fig=fig_line, include_fits=True)
    figure_conversion(fig_line, static_fig=True)


else:
    st.write(f'This object does not have line measurements')


