from datetime import datetime
import pytest
import datetime
from sqlalchemy.orm import Session
from ....models.academic_advising.drop_in import DropIn
from ....entities.academic_advising import DropInEntity
from .test_responses_api import (
    sample_response_small,
    sample_parsed_response_small,
    sample_response_large,
    sample_parsed_response_large,
)
from ..reset_table_id_seq import reset_table_id_seq


# sample API responses
sample_response_small = sample_response_small
sample_parsed_response_small = sample_parsed_response_small
sample_response_large = sample_response_large
sample_parsed_response_large = sample_parsed_response_large

sample_responses = [
    sample_response_small,
    sample_parsed_response_small,
    sample_response_large,
    sample_parsed_response_large,
]


def date_maker(days_in_future: int, hour: int, minutes: int) -> datetime.datetime:
    """
    Creates a new `datetime` object relative to the current day when the
    data is reset using a reset script.

    Parameters:
        days_in_future (int): Number of days in the future from the current day to set the date
        hour (int): Which hour of the day to set the `datetime`, using the 24 hour clock
        minutes (int): Which minute to set the `datetime`

    Returns:
        datetime: `datetime` object to use in events test data.
    """
    # Find the date and time at the moment the script is run
    now = datetime.datetime.now()
    # Set the date and time to 12:00AM of that day
    current_day = datetime.datetime(now.year, now.month, now.day)
    # Create a delta containing the offset for which to move the current date
    timedelta = datetime.timedelta(days=days_in_future, hours=hour, minutes=minutes)
    # Create the new date object offset by `timedelta`
    new_date = current_day + timedelta
    # Returns the new date
    return new_date


# drop in objects after API parsing + committing to table
drop_in_one = DropIn(
    id=1,
    title="KMP Advising",
    start=date_maker(0, 5, 30),
    end=date_maker(0, 6, 30),
    link="https://calendar.google.com/",
)

drop_in_two = DropIn(
    id=2,
    title="Brent Advising",
    start=date_maker(1, 4, 30),
    end=date_maker(1, 5, 30),
    link="https://calendar.google.com/",
)

drop_in_three = DropIn(
    id=3,
    title="Cynthia Advising",
    start=date_maker(2, 0, 30),
    end=date_maker(2, 1, 30),
    link="https://calendar.google.com/",
)

drop_ins = [drop_in_one, drop_in_two, drop_in_three]

# event_data from events_dict to use for create() testing
create_event_data_1 = {
    "summary": "Brent Advising",
    "start": date_maker(1, 0, 30),
    "end": date_maker(1, 1, 30),
    "link": "https://calendar.google.com/",
}

create_event_data_2 = {
    "summary": "KMP Advising",
    "start": date_maker(2, 0, 30),
    "end": date_maker(2, 1, 30),
    "link": "https://calendar.google.com/",
}

insert_all_event_data = {
    "4": {
        "summary": "Brent Advising",
        "start": date_maker(1, 0, 30),
        "end": date_maker(1, 1, 30),
        "link": "https://www.google.com/calendar/event?eid=N242MWl2bm83MjQxdHF0cnJwYWM1NXY3YWFfMjAyNDExMjVUMTgwMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
    "5": {
        "summary": "KMP Advising",
        "start": date_maker(2, 0, 30),
        "end": date_maker(2, 1, 30),
        "link": "https://www.google.com/calendar/event?eid=cms1amNvNmx1bDdlNTFiMG90YnQycDllY21fMjAyNDExMjZUMTUzMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
    "6": {
        "summary": "Cynthia Advising",
        "start": date_maker(2, 3, 30),
        "end": date_maker(2, 4, 30),
        "link": "https://www.google.com/calendar/event?eid=cms1amNvNmx1bDdlNTFiMG90YnQycDllY21fMjAyNDExMjZUMTUzMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
}

insert_all_event_data_2 = {
    "4": {
        "summary": "Brent Advising",
        "start": date_maker(3, 0, 30),
        "end": date_maker(3, 1, 30),
        "link": "https://www.google.com/calendar/event?eid=N242MWl2bm83MjQxdHF0cnJwYWM1NXY3YWFfMjAyNDExMjVUMTgwMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
    "5": {
        "summary": "KMP Advising",
        "start": date_maker(4, 0, 30),
        "end": date_maker(4, 1, 30),
        "link": "https://www.google.com/calendar/event?eid=cms1amNvNmx1bDdlNTFiMG90YnQycDllY21fMjAyNDExMjZUMTUzMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
    "6": {
        "summary": "Cynthia Advising",
        "start": date_maker(5, 0, 30),
        "end": date_maker(5, 1, 30),
        "link": "https://www.google.com/calendar/event?eid=cms1amNvNmx1bDdlNTFiMG90YnQycDllY21fMjAyNDExMjZUMTUzMDAwWiBjcy51bmMuZWR1XzM0MG9vbnI0ZWMyNm4xZm85bDg1NHIzaXA4QGc",
    },
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