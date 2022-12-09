import numpy as np
import streamlit as st
import lime
import matplotlib.pyplot as plt

from pathlib import Path
from tools import import_osiris_fits, figure_conversion, data_location, obj_database, load_nirspec_fits, get_obj_spec

st_state = st.session_state

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


# Get the list of possible objects
def obj_listing(db_df):
    return db_df.index.values


def obj_indexing(db_df, visit_var, disp_var, flux_measurements=False):

    idcs_objects = (db_df.visit == visit_var) & (db_df.disp == disp_var)

    if flux_measurements:
        idcs_objects = idcs_objects & (~np.isnan(db_df.redshift))

    return db_df.loc[idcs_objects].SOURCEID.values


# Sample data
data_path = data_location()
sample_df = obj_database(data_path)

# Dropdown menu with the possible objects:
# sample_list = obj_listing(sample_df)

data_folder_old = Path('D:\Pycharm Projects\lime\examples\sample_data')
fits_file = data_folder_old/'gp121903_BR.fits'
log_address = data_folder_old/'example3_linelog.txt'
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

# Object selection widgets
col1, col2, col3 = st.columns(3)

with col1:
    visit = st.radio("Visit", key="visit", options=["Visit_1", "Visit_2"])

with col2:
    disp = st.radio("Grism", key="disp", options=["G235M", "G395M"])

with col3:
    warn_text = 'Checking this box constrains the selection to those objects whose emission lines could be identified'
    st.checkbox(label="Line measurements", key="objs_flux_check", help=warn_text)
    sample_list = obj_indexing(sample_df, visit, disp, st_state.objs_flux_check)
    st.selectbox('SMACS object', sample_list, key='sourceID')


obj_ref = f'{st_state.sourceID}_{st_state.visit}_{st_state.disp}'
obj_folder = data_path/f'spectra/S3_out_clean_custom_pl_v2.0/{st_state.disp}/{st_state.visit}/{st_state.sourceID}'
obj_file = obj_folder/Path(sample_df.loc[obj_ref].path).name
# st.write(f'You selected folder: {obj_folder} ({obj_folder.is_dir()})')
st.write(f'The selected file: {obj_file.name}')

# Fits file online
if obj_file.is_file():

    st_state['spec'] = get_obj_spec(obj_file, obj_ref, sample_df)

    # Spectrum plot
    st.write(f'\nSpectrum plot')
    fig_spec = plt.figure()
    st.pyplot(st_state['spec'].plot.spectrum(in_fig=fig_spec))

    # Grid plot
    if st_state['spec'].log.size > 0:
        st.write(f'\nGrid plot')
        fig_grid = plt.figure()
        st.pyplot(st_state['spec'].plot.grid(in_fig=fig_grid, n_cols=2))

# Fits file not found
else:
    st.write(f'The file was not found in the database: {obj_file.as_posix()}')


# # Global plots
# plots(spec, static_check=True)






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

