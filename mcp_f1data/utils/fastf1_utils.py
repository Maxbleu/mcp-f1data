import fastf1
import fastf1.events
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from fastapi import HTTPException

def get_latest_session():

    path_parts = []
    next_event = fastf1.get_events_remaining().iloc[0]

    if next_event["EventFormat"] == "testing":
        type_event = "pretest"
        n_event = 1
        practices = ["1","2","3"]
        session = [int(p)-1 for p in practices if p in next_event["Session"]]
    else:
        type_event = "official"
        n_event = int(next_event["RoundNumber"]) - 1
        session = "R"

    event_date = next_event["EventDate"]
    year = event_date.year 
    path_parts.extend([type_event, year, n_event, session])

    return path_parts

def get_session(type_event:str=None, year:int=None, event:int=None, session:str=None, latest_session:bool=False):
    if latest_session:
        type_event, year, event, session = get_latest_session()
    if type_event == "official":
        session = fastf1.get_session(year, event, session)
    elif type_event == "pretest":
        session = fastf1.get_testing_session(year, event, session)
    session.load()
    return session

def get_laps(type_event:str, year:int, event:int, session:str, driver:str=None):
    session = get_session(type_event, year, event, session)

    if len(session.drivers) == 0:
        raise HTTPException(status_code=404, detail="No laps found for this session.")

    laps = session.laps
    laps["LapTime"] = pd.to_timedelta(laps["LapTime"])
    if driver: laps = laps.pick_drivers(driver)
    return laps

def get_specific_lap(laps:DataFrame, lap_number:int = -1, get_personal_fastest_lap: bool = False, get_general_fastest_lap:bool = False):
    if (get_general_fastest_lap or get_personal_fastest_lap) and (lap_number == -1):
        lap = laps.pick_fastest()
    else:
        lap = laps.pick_laps(lap_number)
    return lap