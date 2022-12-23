import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from pathlib import Path

import lime.tools
from tools import de_calibrate_func, obj_database, load_nirspec_fits, sidebar_widgets, hdr_to_df, spectrum_fits_path, \
    get_obj_spec, read_database, read_pdf
from plots import plot_nirspec_2D, plot_spectrum, plot_fits_2d, pdf_display
from streamlit import session_state as s_state

if 'auth_status' not in s_state:
    if 'auth_status_hold' in s_state:
        s_state['auth_status'] = s_state['auth_status_hold']
    else:
        s_state['auth_status'] = False

# Confirm the user has been identified
if s_state['auth_status']:

    # Resetting the sample variable
    if 'sample' not in s_state:
        s_state['sample'] = s_state['sample_hold']

    # Sample database and location
    data_path, sample_df = obj_database(s_state['sample'])

    # Side bar settings
    sidebar_widgets(sample_df, data_path, s_state['sample'])

    # Page structure
    st.markdown(f'# {s_state["sample"]} NIRSpec sample')
    st.markdown(f'On the sidebar, you can filter the sample by observation configuration')

    # Sample different type of screens
    if s_state['sample'] == 'SMACS':

        # Locate the object and its 1d fits file
        obj_ref, obj_file = spectrum_fits_path(s_state['sample'], sample_df, data_path)

        # Fits file online
        if obj_file.is_file():

            st.markdown(f'### {obj_ref} spectrum plot')

            # figure_conversion(fig_spec, static_fig=False)
            st.bokeh_chart(plot_spectrum(s_state['spec']))
            st.markdown(f'The selected file is: {obj_file.name}')

            # Fits information
            wave, e_flux, err, hdr_list = load_nirspec_fits(obj_file.as_posix())

            # Display the header
            st.markdown(f'### {obj_ref} header data')
            tab1, tab2 = st.tabs(['Extension 0', 'Extension 1'])
            s_state['spec'] = get_obj_spec(data_path, obj_file, obj_ref, None)

            with tab1:
                hdr_df = hdr_to_df(hdr_list[0])
                st.dataframe(hdr_df, width=800)

            with tab2:
                hdr_df = hdr_to_df(hdr_list[1])
                st.dataframe(hdr_df, width=800)
            st.markdown(f'The selected file is: {obj_file.name}')

            # 2D interaction
            obj_2d_file = Path(obj_file.as_posix().replace('_x1d_masked_bpx.fits', '_s2d.fits'))
            if obj_2d_file.is_file():
                st.markdown(f'### {obj_ref} 2D spectrum')
                wave, e_flux, err, hdr_list = load_nirspec_fits(obj_2d_file.as_posix())
                fig = plot_fits_2d(e_flux, wave)
                st.bokeh_chart(fig)
                st.markdown(f'The selected file is: {obj_2d_file.name}')

        # Fits file not found
        else:
            st.write(f'The file was not found in the database: {obj_file.as_posix()}')

    #CEERs 2nd data release_
    else:

        # Locate the object and its 1d fits file
        files_df, fits_path = spectrum_fits_path(s_state['sample'], sample_df, data_path)
        idcs_1d = files_df.MPT.isin([s_state["MPT_ID"]]) & (files_df.ext == 'x1d')
        idcs_2d = files_df.MPT.isin([s_state["MPT_ID"]]) & (files_df.ext == 's2d')

        files_1d = files_df.loc[idcs_1d].index.values
        files_2d = files_df.loc[idcs_2d].index.values
        files_1d = np.sort(files_1d)
        files_2d = np.sort(files_2d)

        st.markdown(f'# Object {s_state["MPT_ID"]}: x1d spectrum')

        if len(files_1d) > 0:
            fits_1d = st.selectbox('Observations', files_1d, key='fits_1d')
            fits1_path = data_path/'spectra'/f'{fits_1d}.fits'
            s_state['spec'], hdr_list = get_obj_spec(None, fits1_path, None, None, header=True)

            tab0, tab1, tab2 = st.tabs(['Spectrum', 'Header 0', 'Header 1'])

            with tab0:
                st.bokeh_chart(plot_spectrum(s_state['spec']))
                st.markdown(f'You can click the +/- loop symbols to magnify on the X axis')

            with tab1:
                hdr_df = hdr_to_df(hdr_list[0])
                st.dataframe(hdr_df, width=800)
            with tab2:
                hdr_df = hdr_to_df(hdr_list[1])
                st.dataframe(hdr_df, width=800)

        else:
            st.markdown(f'The .fits file is not available')

        st.markdown(f'# Object {s_state["MPT_ID"]}: s2d spectrum')
        if len(files_2d) > 0:
            fits_2d = st.selectbox('Observations', files_2d, key='fits_2d')
            fits2d_path = data_path/'spectra'/f'{fits_2d}.fits'
            wave1, e_flux1, err1, hdr_list2 = load_nirspec_fits(fits2d_path.as_posix())
            flux1 = de_calibrate_func(e_flux1)
            wave_A = lime.tools.unit_convertor('um', 'A', wave_array=wave1)
            # st.markdown(f'{wave_A[0], wave_A[-1], len(wave_A)}')
            # st.markdown(f'{s_state["spec"].wave.data[0], s_state["spec"].wave.data[-1], len(s_state["spec"].wave.data)}')

            # Tab structure
            tab0, tab1, tab2 = st.tabs(['Spectrum', 'Header 0', 'Header 1'])

            with tab0:
                fig = plot_fits_2d(flux1, wave_A)
                st.bokeh_chart(fig)
                st.markdown(f'You can click the +/- loop symbols to magnify on the X axis')

            with tab1:
                hdr_df = hdr_to_df(hdr_list2[0])
                st.dataframe(hdr_df, width=800)

            with tab2:
                hdr_df = hdr_to_df(hdr_list2[1])
                st.dataframe(hdr_df, width=800)

        else:
            st.markdown(f'The .fits file is not available')

        st.markdown(f'# Object {s_state["MPT_ID"]}: Bio plot')
        st.markdown(f' These plots were done by Steve Finkestein. Please select file below.')

        bio_df = read_database(data_path/f'bio_pdf_df.pkl')
        idcs_pdf = bio_df.MPT.isin([s_state["MPT_ID"]])
        pdf_list = bio_df.loc[idcs_pdf].index.values
        bio_pdf_file = st.selectbox('Bio plot', pdf_list, key='bio_plot')
        pdf = read_pdf(data_path/'bio_plots'/bio_pdf_file)
        st.markdown(pdf_display(pdf), unsafe_allow_html=True)

# No user
else:
    st.markdown(f'# Please introduce your login details')



