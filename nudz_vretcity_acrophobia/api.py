import requests
import pandas as pd
from vretcity import loader, preprocessor

import io

API_PATH = "https://expozice.jan-husak.cz/api/download"


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def get_sessions(token):
    r = requests.get(API_PATH, auth=BearerAuth(token), timeout=2)
    if(r.status_code == 200):
        df_sessions = pd.DataFrame(r.json()['runs'])
        return(df_sessions)
    else:
        raise Exception('failed')


def get_session_data(token, run_id):
    pth = f'{API_PATH}/{run_id}'
    r = requests.get(pth, auth=BearerAuth(token), timeout=10)
    if(r.status_code == 200):
        df_session = loader.load_log(io.StringIO(r.content.decode(r.encoding)))
        _ = preprocessor.process_log(df_session)
        if loader.is_valid(df_session):
            return df_session
        else:
            raise Exception('final log is not valid')
    else:
        raise Exception('failed')
