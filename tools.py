import numpy as np
import pandas as pd
import lime
import pickle
import mpld3

from astropy.io import fits
from pathlib import Path
import streamlit.components.v1 as components
import streamlit as st
from streamlit import session_state as s_state
from PIL import Image
from cryptography.fernet import Fernet


PATH_DATA = './data'
IMAGE_PATH = './CEERS_white.png'
USERS = ['Vital Fernandez', 'Ricardo Amorin', 'Raymond Simons', 'Pablo Arrabal', 'Mark Dickinson']
USERNAMES = ['Vital', 'Amorin', 'Simons', 'Arrabal', 'Dickinson']
CREDENTIALS = {'usernames': {}}
DEFAULTS = {'visit': 'Visit_2', 'disp': 'G235M', 'flux_check': True, 'subsample': 'All', 'MPT_ID': 0}

for i, username in enumerate(USERNAMES):
    CREDENTIALS['usernames'][username] = {'name': USERS[i], 'password': None}


# Calibrate flux files
def calibrate_func(data_array, factor=st.secrets.calibration.factor, k1=st.secrets.calibration.k1, k2=st.secrets.calibration.k2,
                   k3=st.secrets.calibration.k3, k4=st.secrets.calibration.k4, norm=st.secrets.calibration.norm):

    # 2D data
    if len(data_array.shape) > 1:
        data_array = data_array/norm
        calib_data = (data_array/np.exp(factor)) + (k1 + k2 * factor + k3 * factor*factor) * np.arange(data_array.shape[1])/factor**k4

    # 1d Data
    else:
        calib_data = (data_array/(np.exp(factor))) + (k1 + k2 * factor + k3 * factor*factor) * np.arange(data_array.size)/factor**k4

    return calib_data


# De-calibrate flux files
def de_calibrate_func(data_array, factor=st.secrets.calibration.factor, k1=st.secrets.calibration.k1, k2=st.secrets.calibration.k2,
                      k3=st.secrets.calibration.k3, k4=st.secrets.calibration.k4, norm=st.secrets.calibration.norm):

    # 2D data
    if len(data_array.shape) > 1:
        calib_data = ((data_array) - (k1 + k2 * factor + k3 * factor*factor) * np.arange(data_array.shape[1])/factor**k4) * np.exp(factor)
        calib_data = calib_data * norm

    # 1d Data
    else:
        calib_data = (data_array - (k1 + k2 * factor + k3 * factor*factor) * np.arange(data_array.size)/factor**k4) * np.exp(factor)

    return calib_data


def create_pickle(pickle_file, dataframe):
    with open(pickle_file, "wb") as outfile:
        pickle.dump(dataframe, outfile)


def encrypt_file(filepath, key, variable):

    #Save variable to pickle file
    with open(filepath, "wb") as outfile:
        pickle.dump(variable, outfile)

    f = Fernet(key)
    with open(filepath, "rb") as file:
        file_data = file.read()

    encrypted_data = f.encrypt(file_data)
    with open(filepath, "wb") as file:
        file.write(encrypted_data)


def decrypt_file(pickle_file, key):
    f = Fernet(key)
    with open(pickle_file, "rb") as file:
        encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        data = pickle.loads(decrypted_data)

    return data


# Sample DF slicer for object selection
def obj_indexing(db_df, visit_var, disp_var, flux_measurements=False):

    idcs_objects = (db_df.visit == visit_var) & (db_df.disp == disp_var)

    if flux_measurements:
        idcs_objects = idcs_objects & (~np.isnan(db_df.redshift))

    return db_df.loc[idcs_objects].SOURCEID.values


# Object selection widgets
def select_obj(sample_DF):

    # Object selection widgets
    col1, col2, col3 = st.columns(3)

    with col1:
        visit = st.radio("Visit", key="visit", options=["Visit_1", "Visit_2"])

    with col2:
        disp = st.radio("Grism", key="disp", options=["G235M", "G395M"])

    with col3:
        warn_text = 'Checking this box constrains the selection to those objects whose emission lines could be identified'
        st.checkbox(label="Line measurements", key="objs_flux_check", help=warn_text)
        sample_list = obj_indexing(sample_DF, visit, disp, s_state.objs_flux_check)
        sourceID = st.selectbox('SMACS object', sample_list, key='sourceID')

    return visit, disp, sourceID


def save_objSample(param):

    s_state[f'{param}_hold'] = s_state[f'{param}']

    return


def sample_selection():

    if 'sample_hold' not in s_state:
        s_state['sample_hold'] = 'CEERs_2022-12'
    s_state['sample'] = s_state[f'sample_hold']

    sample = st.radio('Sample selection', key='sample', options=['CEERs_2022-12', 'SMACS'], on_change=save_objSample,
                      args=('sample',))

    return sample

def read_database(file_path):
    return decrypt_file(file_path, st.secrets.calibration.key)

@st.experimental_singleton
def read_pdf(file_path):
    return decrypt_file(file_path, st.secrets.calibration.key)

@st.experimental_singleton
def spectrum_fits_path(sample, sample_df, data_path, **kwargs):

    if sample == 'SMACS':
        obj_ref = f'{s_state.sourceID}_{s_state.visit}_{s_state.disp}'
        obj_folder = data_path / f'spectra/S3_out_clean_custom_pl_v2.0/{s_state.disp}/{s_state.visit}/{s_state.sourceID}'
        fits_path = obj_folder / Path(sample_df.loc[obj_ref].path).name

    elif sample == 'CEERs_2022-12':
        obj_ref = decrypt_file(data_path/'file_df.pkl', st.secrets.calibration.key)
        fits_path = data_path/'spectra'

    else:
        st.markdown(f'Sample {sample} not recognized')

    return obj_ref, fits_path

# Object selection widgets
def sidebar_widgets(sample_DF, data_path, sample):

    # Sample criteria selection
    for item, value in DEFAULTS.items():
        if f'{item}_hold' not in s_state:
            s_state[f'{item}_hold'] = value
        s_state[item] = s_state[f'{item}_hold']

    # Adjust the sidebar to the sample
    with st.sidebar:

        if sample == 'SMACS':

            st.markdown(f'# Object selection')

            visit = st.radio("Visit", key="visit", options=["Visit_1", "Visit_2"], on_change=save_objSample, args=("visit",))

            disp = st.radio("Grism", key="disp", options=["G235M", "G395M"], on_change=save_objSample, args=("disp",))

            st.markdown('Sub-sample criteria')
            warn_text = 'This selection constrains the selection to those objects whose emission lines could be identified'
            flux_check2 = st.checkbox(label="Redshift measurements", key="flux_check", help=warn_text, on_change=save_objSample,
                                      args=("flux_check",))

            # Object selection criteria
            sample_list = obj_indexing(sample_DF, visit, disp, flux_check2)

            if 'sourceID_hold' not in s_state:
                s_state[f'sourceID_hold'] = sample_list[0]
            s_state['sourceID'] = s_state[f'sourceID_hold']

            if s_state['sourceID'] not in list(sample_list):
                s_state['sourceID'] = sample_list[0]
                st.sidebar.warning('Object not found in the sample selection, switching to the first object in the selected list')

            st.selectbox('SMACS object', sample_list, key='sourceID', on_change=save_objSample, args=("sourceID",))

            obj_ref = f'{s_state.sourceID}_{s_state.visit}_{s_state.disp}'
            obj_folder = data_path / f'spectra/S3_out_clean_custom_pl_v2.0/{s_state.disp}/{s_state.visit}/{s_state.sourceID}'
            obj_file = obj_folder / Path(sample_DF.loc[obj_ref].path).name
            s_state['spec'] = get_obj_spec(data_path, obj_file, obj_ref, sample_DF)

        elif sample == 'CEERs_2022-12':
            st.markdown(f'# Object selection')

            sub_sample_dict = decrypt_file(data_path/'msa'/'subsamples_dict_hashed.pkl', st.secrets.calibration.key)

            sub_sample_list = ['All'] + list(sub_sample_dict.keys())
            subSample = st.selectbox('Sub-sample', sub_sample_list, key='subsample', on_change=save_objSample, args=("subsample",))

            if subSample == 'All':
                sample_list = sample_DF.index.values
            else:
                sample_list = sub_sample_dict[subSample]
                sample_list = np.sort(sample_list)


            if len(sample_list) > 0:

                # Change the current object is on the list if repeating
                if s_state['MPT_ID'] not in list(sample_list):
                    st.sidebar.warning(f'MPT_ID {s_state["MPT_ID"]} not found in the sample selection, '
                                       f'switching to the first object on the selection')
                    s_state['MPT_ID'] = sample_list[0]

                st.selectbox('Object selection', sample_list, key='MPT_ID', on_change=save_objSample, args=("MPT_ID",))

            else:
                st.sidebar.warning(f'Sub-sample {subSample} MSA does not have objects')


        else:
            st.markdown(f'Sample {sample} is not recognized')

    return

# Front image
@st.experimental_singleton
def logo_load(file_address=IMAGE_PATH):
   return Image.open(Path(file_address))


@st.experimental_singleton
def obj_database(sample='SMACS', file_address=PATH_DATA):

    file_address = Path(file_address)
    data_path = file_address / sample

    if sample == 'SMACS':
        file_address = data_path/'obj_table_v8.txt'
        df_database = lime.load_log(file_address)
    else:
        file_address = data_path/'sample_df.pkl'
        df_database = decrypt_file(file_address, st.secrets.calibration.key)

    return data_path, df_database


@st.experimental_singleton
def get_obj_spec(data_path, fits_address, obj_ref, sampleDF, norm_flux=1e-20, header=False):

    if sampleDF is not None:
        z_obj = sampleDF.loc[obj_ref].redshift
    else:
        z_obj = 0

    wave, e_flux, err, hdr = load_nirspec_fits(fits_address.as_posix())
    mask = np.isnan(err)

    flux = de_calibrate_func(e_flux)

    spec = lime.Spectrum(wave, flux, err, redshift=z_obj, units_wave='um', units_flux='Jy', pixel_mask=mask)
    spec.convert_units(units_wave='A', units_flux='Flam', norm_flux=norm_flux)

    if obj_ref is not None:
        log_path = data_path/f'logs/{obj_ref}_v8_log.txt'

        if log_path.is_file():
            spec.load_log(log_path)

    output = spec if header is False else (spec, hdr)

    return output


# Function to open nirspec fits files
def load_nirspec_fits(file_address, ext=None):

    # Stablish the file type
    if 'x1d' in file_address:
        ext = 1
        spec_type = 'x1d'

    elif 's2d' in file_address:
        ext = 1
        spec_type = 's2d'

    elif 'uncal' in file_address:
        ext = 1
        spec_type = 's2d'

    elif 'cal' in file_address:
        ext = 1
        spec_type = 'cal'
    else:
        print('Spectrum type could not be guessed')

    # Open the fits file
    with fits.open(file_address) as hdu_list:

        if spec_type == 'x1d':
            data_table, header = hdu_list[ext].data, (hdu_list[0].header, hdu_list[ext].header)
            wave_array, flux_array, err_array = data_table['WAVELENGTH'], data_table['FLUX'], data_table['FLUX_ERROR']

        elif spec_type == 'cal':
            wave_array, flux_array, err_array = None, None, None

        elif spec_type == 's2d':
            header = (hdu_list[0].header, hdu_list[1].header)
            wave_array = np.linspace(header[1]['WAVSTART'], header[1]['WAVEND'], header[1]['NAXIS1'], endpoint=True) * 1000000
            err_array = hdu_list[2].data
            flux_array = hdu_list[1].data

    return wave_array, flux_array, err_array, header


def figure_conversion(in_fig, static_fig=True, height=850):

    # Static figures
    if static_fig:
        st.pyplot(in_fig)

    # Dynamic figures
    else:
        fig_html = mpld3.fig_to_html(in_fig)
        components.html(fig_html, height=height)

    return


def hdr_to_df(header):

    key_list = list(header.keys())
    comments_list = header.comments

    df = pd.DataFrame(index=key_list, columns=['Value', 'Comment']).fillna('')
    for idx in df.index:
        df.loc[idx, 'Value'] = header.get(idx, '')
        df.loc[idx, 'Comment'] = comments_list[idx]

    return df


