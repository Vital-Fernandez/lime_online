import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from pathlib import Path
from tools import figure_conversion, data_location, obj_database, load_nirspec_fits, sidebar_widgets


def hdr_to_df(header):

    key_list = list(header.keys())
    comments_list = header.comments

    df = pd.DataFrame(index=key_list, columns=['Value', 'Comment']).fillna('')
    for idx in df.index:
        df.loc[idx, 'Value'] = header.get(idx, '')
        df.loc[idx, 'Comment'] = comments_list[idx]

    return df

def obj_listing(db_df):
    return db_df.index.values


def plots(obj_label, lime_spec, static_check=True):

    # Spectrum plot
    st.write(f'{obj_label} spectrum')
    fig_spec = plt.figure()
    lime_spec.plot.spectrum(in_fig=fig_spec, include_fits=True)
    figure_conversion(fig_spec, static_fig=static_check)

    # Fit grid plot
    if lime_spec.log.index.size > 0:
        st.write(f'{obj_label} line fittings grid')
        fig_grid = plt.figure()
        lime_spec.plot.grid(in_fig=fig_grid)
        figure_conversion(fig_grid, static_fig=static_check)
    else:
        st.write(f'{obj_label} does not have line measurements')

    return


# Confirm the user has been identified
st_state = st.session_state
if st_state['auth_status']:

    # Sample data
    data_path = data_location()
    sample_df = obj_database(data_path)

    # Page structure
    st.markdown(f'# NIRSpec observation')
    st.markdown(f'On the sidebar, you can filter the sample by the JWST visit, NIRSpec dispenser and '
                f'measurements availability')

    # # Object selection widgets
    # select_obj(sample_df)

    # Side bar settings
    sidebar_widgets(sample_df)

    obj_ref = f'{st_state.sourceID}_{st_state.visit}_{st_state.disp}'
    obj_folder = data_path/f'spectra/S3_out_clean_custom_pl_v2.0/{st_state.disp}/{st_state.visit}/{st_state.sourceID}'
    obj_file = obj_folder/Path(sample_df.loc[obj_ref].path).name
    st.markdown(f'*The selected file is {obj_file.name}*')

    # Fits file online
    if obj_file.is_file():

        st.markdown(f'### {obj_ref} spectrum plot')

        # Spectrum plot
        fig_spec = plt.figure()
        st_state['spec'].plot.spectrum(in_fig=fig_spec, fig_cfg={'axes.labelsize': 12, 'xtick.labelsize': 12,
                                                                 'ytick.labelsize': 12})
        figure_conversion(fig_spec, static_fig=False)

        # Fits information
        obj_ref = f'{st_state.sourceID}_{st_state.visit}_{st_state.disp}'
        obj_folder = data_path / f'spectra/S3_out_clean_custom_pl_v2.0/{st_state.disp}/{st_state.visit}/{st_state.sourceID}'
        obj_file = obj_folder / Path(sample_df.loc[obj_ref].path).name
        wave, e_flux, err, hdr_list = load_nirspec_fits(obj_file.as_posix())

        # Display the header
        st.markdown(f'### {obj_ref} header data')
        tab1, tab2 = st.tabs(['Extension 0', 'Extension 1'])

        with tab1:
            hdr_df = hdr_to_df(hdr_list[0])
            st.dataframe(hdr_df, width=800)
        with tab2:
            hdr_df = hdr_to_df(hdr_list[1])
            st.dataframe(hdr_df, width=800)

    # Fits file not found
    else:
        st.write(f'The file was not found in the database: {obj_file.as_posix()}')

# No user
else:
    st.markdown(f'# Please introduce your login details')



