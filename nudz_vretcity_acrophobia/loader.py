from vretcity import loader, preprocessor


def load_and_process_log(file):
    df_session = loader.load_log(file)
    _ = preprocessor.process_log(df_session)
    if loader.is_valid(df_session): return df_session
    return None
