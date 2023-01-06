import streamlit as st
import matplotlib.pyplot as plt

from tools import figure_conversion, obj_database, sidebar_widgets, read_file_database, get_obj_spec, read_ceers_database
from lime.tools import UNITS_LATEX_DICT
from streamlit import session_state as s_state
from numpy import isnan

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
    st.markdown(f'# {s_state["sample"]} Line fitting')
    st.markdown(f'On the sidebar, you can select the object')

    if s_state['sample'] == 'SMACS':

        # Sample database and location
        data_path, sample_df = obj_database(s_state.sample)

        # Sidebar object selection
        sidebar_widgets(sample_df, data_path, s_state['sample'])

        # Page structure
        obj_ref = f'{s_state.sourceID}_{s_state.visit}_{s_state.disp}'
        st.markdown(f'# Line fitting for {obj_ref}')

        spec = st.session_state['spec']

        if spec.log.size > 0:

            tab1, tab2, tab3 = st.tabs(['Grid', 'Profile', 'Table'])

            # Grid plot
            with tab1:
                st.markdown(f'## Line grid')
                fig_grid = plt.figure(tight_layout=True)
                st.pyplot(s_state['spec'].plot.grid(in_fig=fig_grid, n_cols=2, fig_cfg={'axes.titlesize': 10}),
                          col_row_scale=(1, 3))

            # Spectrum plot
            with tab2:
                st.markdown(f'## Line profile')
                st.selectbox('Select a line for the profile visualization', spec.log.index.values, key='line')
                fig_line = plt.figure()
                spec.plot.band(s_state["line"], in_fig=fig_line, include_fits=True, fig_cfg={'axes.labelsize': 12,
                                                                                              'xtick.labelsize': 12,
                                                                                              'ytick.labelsize': 12})
                figure_conversion(fig_line, static_fig=True)

            # Dataframe
            with tab3:

                # Explanations
                st.markdown(f'## Measurements table')
                st.markdown(f'- Please check [LiMe](https://lime-stable.readthedocs.io/en/latest/) online documentation for '
                            f'the parameters physical description.')
                label_dis, label_flux = UNITS_LATEX_DICT[spec.units_wave], UNITS_LATEX_DICT[spec.units_flux]
                st.markdown(f'- The lines are measured in the observed frame.')
                st.markdown(f'- The dispersion axis is in $${label_dis}$$.')
                st.markdown(f'- The flux axis is in $${label_flux}$$.')

                # Output file formatting
                st.selectbox('Log file format:', ['.txt', '.pdf', '.fits', '.xlsx', '.asdf'], key='file_format')
                st.dataframe(spec.log)
                string_DF = spec.log.to_string()
                st.download_button('Download', data=string_DF.encode('UTF-8'), file_name=f'{obj_ref}{s_state.file_format}')

        else:
            st.markdown(f'This object does not have line measurements')

    # CEERs 2022
    else:

        # Locate the object and its 1d fits file
        fits_path = data_path/'spectra'
        file_df_path = data_path/'file_df.pkl'
        files_df = read_file_database(file_df_path)
        ceers_df = read_ceers_database(data_path.parent/'ceers_sample.pkl')

        # Index the files
        idcs_1d = files_df.MPT.isin([s_state["MPT_ID"]]) & (files_df.ext == 'x1d')
        files_1d = files_df.loc[idcs_1d].index.values

        # Object
        st.markdown(f'# Object {s_state["MPT_ID"]}: x1d spectra')

        # Select among the files
        if len(files_1d) > 0:
            fits_1d = st.selectbox('File selection', files_1d, key='fits_1d')
            fits1_path = data_path/'spectra'/f'{fits_1d}.fits'

            ceers_database = data_path.parent/'ceers_sample.pkl'
            ceers_df = read_ceers_database(ceers_database)

            z_obj = ceers_df.loc[s_state["MPT_ID"], 'z_obj']
            z_obj = 0 if isnan(z_obj) else z_obj
            obj_ref = fits1_path.stem
            s_state['spec'], hdr_list = get_obj_spec(data_path, fits1_path, obj_ref, z_obj=z_obj, header=True, sample=s_state['sample'])

            if len(s_state['spec'].log.index) > 0:
                tab1, tab2, tab3 = st.tabs(['Grid', 'Profile', 'Table'])

                # Grid plot
                with tab1:
                    st.markdown(f'## Line grid')
                    fig_grid = plt.figure(tight_layout=True)
                    st.pyplot(s_state['spec'].plot.grid(in_fig=fig_grid, n_cols=2, fig_cfg={'axes.titlesize': 10}),
                              col_row_scale=(1, 3))

                # Spectrum plot
                with tab2:
                    st.markdown(f'## Line profile')
                    st.selectbox('Select a line for the profile visualization', s_state['spec'].log.index.values, key='line')
                    fig_line = plt.figure()
                    s_state['spec'].plot.band(s_state["line"], in_fig=fig_line, include_fits=True, fig_cfg={'axes.labelsize': 12,
                                                                                                 'xtick.labelsize': 12,
                                                                                                 'ytick.labelsize': 12})
                    figure_conversion(fig_line, static_fig=True)

                # Dataframe
                with tab3:

                    # Explanations
                    st.markdown(f'## Measurements table')
                    st.markdown(
                        f'- Please check [LiMe](https://lime-stable.readthedocs.io/en/latest/) online documentation for '
                        f'the parameters physical description.')
                    label_dis, label_flux = UNITS_LATEX_DICT[s_state['spec'].units_wave], UNITS_LATEX_DICT[s_state['spec'].units_flux]
                    st.markdown(f'- The lines are measured in the observed frame.')
                    st.markdown(f'- The dispersion axis is in $${label_dis}$$.')
                    st.markdown(f'- The flux axis is in $${label_flux}$$.')

                    # Output file formatting
                    st.selectbox('Log file format:', ['.txt', '.pdf', '.fits', '.xlsx', '.asdf'], key='file_format')
                    st.dataframe(s_state['spec'].log)
                    string_DF = s_state['spec'].log.to_string()
                    st.download_button('Download', data=string_DF.encode('UTF-8'),
                                       file_name=f'{obj_ref}{s_state.file_format}')

            else:
                st.markdown(f'There are not line measurements for this object')

        else:
            st.markdown(f'There are not observations for this object')

# No user
else:
    st.markdown(f'# Please use your login details')


