from datetime import date, datetime, time
import pytest
import datetime
from sqlalchemy.orm import Session
from ....models.academic_advising.drop_in import DropIn
from ....entities.academic_advising import DropInEntity
from .test_responses_api import sample_response_small, sample_parsed_response_small, sample_response_large, sample_parsed_response_large
from ..reset_table_id_seq import reset_table_id_seq


# sample API responses
sample_response_small = sample_response_small
sample_parsed_response_small = sample_parsed_response_small
sample_response_large = sample_response_large
sample_parsed_response_large = sample_parsed_response_large

sample_responses = [sample_response_small, sample_parsed_response_small, sample_response_large, sample_parsed_response_large]


def date_maker(days_in_future: int) -> datetime.date:
    """
    Creates a `date` object dynamically relative to the current day.

    Parameters:
        days_in_future (int): Number of days in the future from the current day.

    Returns:
        datetime.date: A `date` object representing the new date.
    """
    today = datetime.date.today()
    return today + datetime.timedelta(days=days_in_future)


# drop in objects after API parsing + committing to table
drop_in_one = DropIn(
    id=1,
    title="KMP Advising",
    start=time(8, 0, 0, 0),
    end=time(9, 0, 0, 0),
    date=date_maker(1),
    link="https://calendar.google.com/",
)

drop_in_two = DropIn(
    id=2,
    title="Brent Advising",
    start=time(9, 0, 0, 0),
    end=time(10, 0, 0, 0),
    date=date_maker(2),
    link="https://calendar.google.com/",
)

drop_in_three = DropIn(
    id=3,
    title="Cynthia Advising",
    start=time(10, 0, 0, 0),
    end=time(11, 0, 0, 0),
    date=date_maker(2),
    link="https://calendar.google.com/",
)

drop_ins = [drop_in_one, drop_in_two, drop_in_three]

# event_data from events_dict to use for create() testing
create_event_data_1 = {
    "summary": "Brent Advising",
    "start": time(13, 0),
    "end": time(14, 0),
    "date": date_maker(0),
    "link": "https://calendar.google.com/",
}

create_event_data_2 = {
    "summary": "KMP Advising",
    "start": time(10, 30),
    "end": time(11, 30),
    "date": date_maker(1),
    "link": "https://calendar.google.com/",
}

insert_all_event_data = {
    "4": {
        "summary": "Brent Advising",
        "start": time(13, 0),
        "end": time(14, 0),
        "date": date_maker(0),
        "link": "https://www.google.com/calendar/event?eid=N242MWl2bm83MjQxdHF0cnJwYWM1NXY3YWFfMjAyNDExMjVUMTgwMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
    "5": {
        "summary": "KMP Advising",
        "start": time(10, 30),
        "end": time(11, 30),
        "date": date_maker(1),
        "link": "https://www.google.com/calendar/event?eid=cms1amNvNmx1bDdlNTFiMG90YnQycDllY21fMjAyNDExMjZUMTUzMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
    "6":{
        "summary": "Cynthia Advising",
        "start": time(12, 30),
        "end": time(1, 30),
        "date": date_maker(2),
        "link": "https://www.google.com/calendar/event?eid=cms1amNvNmx1bDdlNTFiMG90YnQycDllY21fMjAyNDExMjZUMTUzMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    }
}

insert_all_event_data_2 = {
    "4": {
        "summary": "Brent Advising",
        "start": time(13, 0),
        "end": time(14, 0),
        "date": date_maker(3),
        "link": "https://www.google.com/calendar/event?eid=N242MWl2bm83MjQxdHF0cnJwYWM1NXY3YWFfMjAyNDExMjVUMTgwMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
    "5": {
        "summary": "KMP Advising",
        "start": time(10, 30),
        "end": time(11, 30),
        "date": date_maker(4),
        "link": "https://www.google.com/calendar/event?eid=cms1amNvNmx1bDdlNTFiMG90YnQycDllY21fMjAyNDExMjZUMTUzMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
    "6":{
        "summary": "Cynthia Advising",
        "start": time(12, 30),
        "end": time(1, 30),
        "date": date_maker(5),
        "link": "https://www.google.com/calendar/event?eid=cms1amNvNmx1bDdlNTFiMG90YnQycDllY21fMjAyNDExMjZUMTUzMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    }
}




def insert_fake_data(session: Session):
    """Inserts fake event data into the test session."""

    global drop_ins

    # Create entities for test event data
    entities = []
    for drop_in in drop_ins:
        drop_in_entity = DropInEntity.from_model(drop_in)
        session.add(drop_in_entity)
        entities.append(drop_in_entity)

    reset_table_id_seq(session, DropInEntity, DropInEntity.id, len(drop_ins) + 1)

    # Commit all changes
    session.commit()


@pytest.fixture(autouse=True)
def fake_data_fixture(session: Session):
    """Insert fake data the session automatically when test is run.
    Note:
        This function runs automatically due to the fixture property `autouse=True`.
    """
    insert_fake_data(session)
    session.commit()
    yield
