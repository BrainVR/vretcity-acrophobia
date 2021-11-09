import os
from requests.sessions import session
import streamlit as st
from nudz_vretcity_acrophobia import loader
from vretcity import visualisations, getters
from nudz_vretcity_acrophobia import api


@st.cache
def fetch_online_data():
    print("this is running")
    token = os.environ['TOKEN']
    try:
        df_sessions = api.get_sessions(token)
        return df_sessions
    except:
        return None


def get_session_participant(df_sessions, id):
    participant = df_sessions.loc[df_sessions['id'] == id,]
    return participant


def get_session_info(sel, df_sessions):
    participant = get_session_participant(df_sessions, sel)
    txt = f'''
    Participant {participant['id'].values[0]}(code {participant['user'].values[0]})\n
    {participant['app'].values[0]}, version {participant['version'].values[0]}\n
    {participant['created_at'].values[0]}\n
    Number of events {participant['events_count'].values[0]}
    '''
    return txt


def fetch_session_data():
    token = os.environ['TOKEN']
    id = st.session_state['selected_session']
    try:
        df_session = api.get_session_data(token, id)
        set_data(df_session, f'Online data from participant {id}')
        return df_session
    except:
        return None


def donwnload_filename(participant):
    txt = f'{participant["id"].values[0]}-{participant["user"].values[0]}.csv'
    return txt


def download_session_data():
    return


def load_data(file):
    if file is None:
        if 'data_df_session' in st.session_state:
            return st.session_state["data_df_session"]
        else:
            df_session = loader.load_and_process_log("example-data/example-pc.csv")
    else:
        df_session = loader.load_and_process_log(file)
    set_data(df_session, "Uploaded file")
    return(df_session)


def has_valid_session_data():
    return "data_df_session" in st.session_state and st.session_state["data_df_session"] is not None


def set_data(df, source):
    st.session_state["loaded_data"] = source
    st.session_state["data_df_session"] = df


def get_data():
    if 'data_df_session' not in st.session_state:
        return None
    return st.session_state['data_df_session']


def option_text(option):
    # this should be buffered anyway
    df_sessions = fetch_online_data()
    participant = df_sessions.loc[df_sessions['id'] == option,]
    txt = f'{participant["id"].values[0]} ({participant["user"].values[0]})'
    return txt


def main():
# SETTING UP PAGE -----------
    st.set_page_config(layout="wide")
    st.title("VRETCity log visualiser")
    if get_data() is not None:
        st.subheader(st.session_state["loaded_data"])
    st.sidebar.write("Please upload your log file below and wait a few moments. ")
    file = st.sidebar.file_uploader("Upload file")

# ONLINE SELECTIOn --------
    df_sessions = fetch_online_data()
    if df_sessions is not None:
        sel = st.sidebar.selectbox("Select data from online repository", df_sessions['id'][::-1],
            format_func=option_text, index=0, key="selected_session")
        st.sidebar.text(get_session_info(sel, df_sessions))
        if st.session_state['selected_session'] > 0:
            st.sidebar.button("Load online data", on_click=fetch_session_data)
        if has_valid_session_data():
            participant = get_session_participant(df_sessions, sel)
            save_data = st.session_state['data_df_session'].to_csv().encode("utf-8")
            st.sidebar.download_button("Donwload the data", data=save_data,
                file_name=donwnload_filename(participant))
    else:
        st.sidebar.text("There has been some trouble fetching data from the online repository. Please refresh the webpage or contact the administrator")



# HANDELING FILE UPLOADS -------
    if file is not None:
        load_data(file)
    df_session = get_data()
    if df_session is None:
        return
    st.write("First few lines of the file")
    st.dataframe(df_session.head())

# EVENT overview ----------------
    st.title("Overview of the events")
    df_events = getters.get_events(df_session)
    s_event_summary = df_events.groupby(['typ', 'objekt']).count()["timesincestart"]
    s_event_summary = s_event_summary.rename("N")

    action, interaction, trigger, control = st.columns(4)
    if "Action" in s_event_summary.index.unique(level="typ"): 
        action.write(s_event_summary["Action"])
    else:
        action.write("No action events")
    if "Interactable" in s_event_summary.index.unique(level="typ"):
        interaction.write(s_event_summary["Interactable"])
    else:
        interaction.write("No interaction events")
    if "TriggerBegin" in s_event_summary.index.unique(level="typ"):
        trigger.write(s_event_summary["TriggerBegin"])
    else:
        trigger.write("No Trigger events in the log")

    if "ExperimentalControl" in s_event_summary.index.unique(level="typ"):
        control.write(s_event_summary["ExperimentalControl"])
    else:
        control.write("No experimental control events")

## Path visualisatoin ------------
    st.title("3d visualisation of participant's path")
    fig = visualisations.plot_path(df_session)
    st.plotly_chart(fig)

# Heart Rate ---------------------
    st.title("Heart rate visualisation")
    df_heartrate = getters.get_heartrate(df_session)
    if df_heartrate.shape[0] > 1:
        fig = visualisations.plot_event_value(df_heartrate, timesincestart=True)
        st.plotly_chart(fig)
    else:
        st.text("There are no heartrate data in the file")


