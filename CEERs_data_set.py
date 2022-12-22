import streamlit as st
import streamlit_authenticator as stauth

from streamlit import session_state as s_state
from pathlib import Path
from tools import logo_load, sample_selection, obj_database, decrypt_file, sidebar_widgets


def run():

    # Side bar
    st.set_page_config(page_title="CEERs data")

    user_file = Path(__file__).parent / 'users_hashed.pkl'
    CREDENTIALS = decrypt_file(user_file, st.secrets.calibration.key)
    authenticator = stauth.Authenticate(CREDENTIALS, 'CEERs_LIME', 'aBcDeF', cookie_expiry_days=60)

    name, auth_status, username = authenticator.login(f'CEERs measurements', 'main')
    s_state['auth_status'] = auth_status

    if auth_status is False:
        st.error(f'Username/password is incorrect')

    elif auth_status is None:
        st.warning(f'Please enter you username and password')

    else:

        # Page structure
        st.sidebar.success("Switch between sections for different results")

        # Object selection widgets
        col_logo, col_welcome = st.columns(2)

        with col_logo:
            image = logo_load()
            st.image(image, width=210)

        with col_welcome:
            st.markdown(f'# Welcome\n# {name}')

        # Printed text
        st.markdown(f'You can expand the side bar on the left hand side to access the data tools and products')

        # Data selection
        st.markdown(f'### Select the data set to visualize')
        sample_selection()

        # Sample database and location
        data_path, sample_df = obj_database(s_state['sample'])

        # Side bar settings
        sidebar_widgets(sample_df, data_path, s_state['sample'])

        # Tables of the New sample
        if s_state['sample'] == 'CEERs_2022-12':

            st.markdown(f'The data Below was tabulated by Mark Dickinson. Please send your questions to '
                        f'[Mark Dickinson](mailto:admin@cloudhadoop.com), [Pablo Arrabal](pablo.arrabalharo@noirlab.edu)'
                        f' and [Jeyhan Kartaltepe](mailto:jsksps@rit.edu)')

            # Table with all the objects
            st.markdown(f'## Complete MPT IDs list')
            st.dataframe(sample_df)

            st.markdown('This file provides basic information for the 1022 unique targets selected for NIRSpec observing '
                        'with MR, P, or both, in all six CEERS NIRSpec pointings:')
            st.markdown(' - **MPT_ID**: ID number for MPT (MSA Planning Tool) catalog.')
            st.markdown(' - **ra, dec**: Coordinates (degrees) in CANDELS v1.9 / CEERS WCS reference frame')
            st.markdown(' - **F606W F814W F125W F160W F115W F150W F200W F277W F356W F444W**: Photometry (AB mag, -99 if no value)')
            st.markdown(' - **zphot, zuse, zbest**: Redshift information (generally photometric redshifts with various provenance)')
            st.markdown(' - **Filest**: The remaining columns show the file from corresponding dispenser and pointing')

            # Table with the MPT per field
            st.markdown(f'## MPT IDs by field')
            field_sample_file = data_path/'msa'/'CEERS_MSA_selected_by_field_hashed.pkl'
            sample_field_df = decrypt_file(field_sample_file, st.secrets.calibration.key)
            st.dataframe(sample_field_df)

            st.markdown('For each target by MPT_ID, this file indicates which CEERS pointings include MR and/or prism observations.')
            st.markdown(' - **MPT_ID**: ID number for MPT (MSA Planning Tool) catalog.')
            st.markdown(' - **ra, dec**: Coordinates (degrees) in CANDELS v1.9 / CEERS WCS reference frame')
            st.markdown(' - **nM_all nP_all**: Number of CEERS NIRSpec pointings for which object is selected for MR (M) or Prism (P)')
            st.markdown(' - **nM_p4 nM_p5 nM_p7 nM_p8 nM_p9 nM_p10**: flag indicating that object is observed with MR in field pN')
            st.markdown(' - **nP_p4 nP_p5 nP_p7 nP_p8 nP_p9 nP_p10**: flag indicating that object is observed with Prism in field pN)')

            if s_state['subsample'] == 'All':
                st.warning('You may select a sub-sample to display its MSA', icon='👈')

            else:

                # Table with the MSA MPT ids
                st.markdown(f'## MSA MPT IDs')
                field_sample_file = data_path / 'msa' / f'msa_selected_{s_state["subsample"]}_hashed.pkl'
                msa_sample_df = decrypt_file(field_sample_file, st.secrets.calibration.key)
                st.dataframe(msa_sample_df)

                st.markdown('Targets selected for MSA observation for each contributed target category.')
                st.markdown(' - **MPT_ID**: ID number for MPT (MSA Planning Tool) catalog.')
                st.markdown(' - **ra, dec**: Coordinates (degrees) in CANDELS v1.9 / CEERS WCS reference frame')
                st.markdown(' - **_nM _nP**: number of fields in which object is selected for observation with MR (M) and Prism (P)')
                st.markdown(' - **_ID**: Original target ID from contributed category information')
                st.markdown(' - **_F160W _F277W**: Photometry in HST F160W or NIRCam F277W (AB mag, -99 if no value)')
                st.markdown(' - **_priority_M, _priority_P**: Priorities assigned to the object in the MPT input '
                            'catalogs for MR (M) and Prism (P).')


if __name__ == "__main__":
    run()



