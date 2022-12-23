import streamlit as st
import matplotlib.pyplot as plt

from tools import figure_conversion, obj_database, sidebar_widgets
from lime.tools import UNITS_LATEX_DICT
from streamlit import session_state as s_state

if s_state['auth_status']:

    # Resetting the sample variable
    if 'sample' not in s_state:
        s_state['sample'] = s_state['sample_hold']
    if 'auth_status' not in s_state:
        s_state['auth_status'] = s_state['auth_status_hold']

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

    else:
        st.markdown(f'# There are not line measurements for this dataset yet')


# No user
else:
    st.markdown(f'# Please use your login details')


