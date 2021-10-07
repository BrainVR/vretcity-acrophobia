import streamlit as st
from nudz_vretcity_acrophobia import loader
from vretcity import visualisations, getters

def load_data(file):
    if file is None:
        if 'data_df_session' in st.session_state:
            return st.session_state["data_df_session"]
        else:
            return loader.load_and_process_log("example-data/example-pc.csv")
    df_session = loader.load_and_process_log(file)
    st.session_state["data_df_session"] = df_session
    return(df_session)


def main():
    st.set_page_config(layout="wide")
    st.title("VRETCity log visualiser")
    st.sidebar.write("Please upload your log file below and wait a few moments. ")
    file = st.sidebar.file_uploader("Upload file")
    df_session = load_data(file)
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


