import numpy as np
import streamlit as st
import lime
import matplotlib.pyplot as plt

from pathlib import Path
from tools import import_osiris_fits, figure_conversion


def plots(lime_spec, static_check=True):

    # Spectrum plot
    st.write(f'{obj_name} spectrum')
    fig_spec = plt.figure()
    lime_spec.plot.spectrum(in_fig=fig_spec, include_fits=True)
    figure_conversion(fig_spec, static_fig=static_check)

    # Fit grid plot
    if lime_spec.log.index.size > 0:
        st.write(f'{obj_name} line fittings grid')
        fig_grid = plt.figure()
        lime_spec.plot.grid(in_fig=fig_grid)
        figure_conversion(fig_grid, static_fig=static_check)
    else:
        st.write(f'{obj_name} does not have line measurements')

    return


data_folder = Path('D:\Pycharm Projects\lime\examples\sample_data')
fits_file = data_folder/'gp121903_BR.fits'
log_address = data_folder/'example3_linelog.txt'
obj_name = 'GP121903'
st.session_state['obj'] = obj_name


# Load the data
wave, flux, hdr = import_osiris_fits(fits_file)
z_obj = 0.19531
normFlux = 1e-18

# Spectrum object
spec = lime.Spectrum(wave, flux, redshift=z_obj, norm_flux=normFlux)
spec.load_log(log_address)
st.session_state['spec'] = spec

# Page structure
st.sidebar.success("Select an object from the pull down menu")
st.header('Object selection')

# Global plots
plots(spec, static_check=True)






# spec_html = mpld3.fig_to_html(fig_spec)
# grid_html = mpld3.fig_to_html(fig_grid)
#
# components.html(spec_html, height=850)
# components.html(grid_html, height=850)


# fig_spec = plt.figure()
# st.pyplot(gp_spec.plot.spectrum(in_fig=fig_spec, include_fits=True))
#
# fig_grid = plt.figure()
# st.pyplot(gp_spec.plot.grid(in_fig=fig_grid))


# mask = lime.spectral_mask_generator(wave_interval=(3500, 7000))
# st.dataframe(mask)

