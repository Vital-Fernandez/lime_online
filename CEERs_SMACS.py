import pickle
import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path
from tools import CREDENTIALS, logo_load


def run():

    # Session state
    st_state = st.session_state

    # Side bar
    st.set_page_config(page_title="CEERs data")

    # User authentification
    pass_pickle_path = Path(__file__).parent / 'hashed_contr.pkl'
    with pass_pickle_path.open('rb') as file:
        hashed_passwords = pickle.load(file)

    # Assign the same passord to every user
    for i, user in enumerate(CREDENTIALS['usernames']):
        CREDENTIALS['usernames'][user]['password'] = hashed_passwords[i]

    authenticator = stauth.Authenticate(CREDENTIALS, 'CEERs_LIME', 'aBcDeF', cookie_expiry_days=60)

    name, auth_status, username = authenticator.login(f'CEERs SMACS flux measurements', 'main')
    st_state['auth_status'] = auth_status

    if auth_status is False:
        st.error(f'Username/password is incorrect')

    elif auth_status is None:
        st.warning(f'Please enter you username and password')

    else:

        # Page structure
        st.sidebar.success("Switch between sections for different results")

        # Object selection widgets
        col1, col2 = st.columns(2)

        with col1:
            image = logo_load()
            st.image(image, width=210)

        with col2:
            st.markdown(f'# Welcome\n# {name}')

        # Printed text
        st.markdown(f'You can expand the side bar on the left hand side to access the data tools and products')
        st.markdown(f'These results correspond to the v2.0 calibration (2022-Nov-16)')


if __name__ == "__main__":

    # 8506
    run()



