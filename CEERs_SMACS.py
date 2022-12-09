import pickle
import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path
from tools import CREDENTIALS


def run():

    # Side bar
    st.set_page_config(page_title="Intro")

    # User authentification
    pass_pickle_path = Path(__file__).parent / 'hashed_contr.pkl'
    with pass_pickle_path.open('rb') as file:
        hashed_passwords = pickle.load(file)

    # Assign the same passord to every user
    for i, user in enumerate(CREDENTIALS['usernames']):
        CREDENTIALS['usernames'][user]['password'] = hashed_passwords[i]

    authenticator = stauth.Authenticate(CREDENTIALS, 'CEERs_LIME', 'aBcDeF', cookie_expiry_days=60)

    name, auth_status, username = authenticator.login(f'CEERs SMACS flux measurements', 'main')

    if auth_status is False:
        st.error(f'Username/password is incorrect')

    elif auth_status is None:
        st.warning(f'Please enter you username and password')

    else:

        # Page structure
        st.sidebar.success("Switch between sections for different results")

        # Wording
        st.header('SMACs CEERS measurements')


if __name__ == "__main__":
    run()



