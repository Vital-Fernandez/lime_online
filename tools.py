import numpy as np
from astropy.io import fits
import mpld3
import streamlit.components.v1 as components
import streamlit as st


def import_osiris_fits(file_address, ext=0):

    # Open the fits file
    with fits.open(file_address) as hdul:
        data, header = hdul[ext].data, hdul[ext].header

    # Reconstruct the wavelength array from the header data
    w_min, dw, n_pix = header['CRVAL1'],  header['CD1_1'], header['NAXIS1']
    w_max = w_min + dw * n_pix
    wavelength = np.linspace(w_min, w_max, n_pix, endpoint=False)

    return wavelength, data, header


def define_spec():

    return


def figure_conversion(in_fig, static_fig=True, height=850):

    # Static figures
    if static_fig:
        st.pyplot(in_fig)

    # Dynamic figures
    else:
        fig_html = mpld3.fig_to_html(in_fig)
        components.html(fig_html, height=height)

    return

