"""Tests for the DropIn Service"""

import subprocess
import pytest

from backend.services.exceptions import UserPermissionException
from ..fixtures import drop_in_svc
from unittest.mock import create_autospec

from ....services.academic_advising.drop_in import DropInService
from ....models.academic_advising.drop_in import DropIn
from backend.models.pagination import DropInPaginationParams, PaginationParams

# Import the setup_teardown fixture explicitly to load entities in database
from .drop_in_demo_data import date_maker, fake_data_fixture as insert_fake_data_two

# Import the fake model data in a namespace for test assertions
# reset demo: python3 -m backend.script.reset_demo
from . import drop_in_demo_data
from .. import user_data


def test_get_all(drop_in_svc: DropInService):
    """Test getting all drop-ins from the database"""
    events = drop_in_svc.all()
    assert events is not None
    assert len(events) == len(drop_in_demo_data.drop_ins)


def test_get_by_id(drop_in_svc: DropInService):
    """Test getting a drop-in by id"""
    event = drop_in_svc.get_by_id(drop_in_demo_data.drop_in_one.id)
    assert event is not None
    assert event.id == drop_in_demo_data.drop_in_one.id


def test_list(drop_in_svc: DropInService):
    """Test that a paginated list of events can be produced."""
    pagination_params = DropInPaginationParams(
        order_by="id",
        range_start=date_maker(days_in_future=0).isoformat(),
        range_end=date_maker(days_in_future=1).isoformat(),
    )
    fetched_events = drop_in_svc.get_paginated_drop_ins(pagination_params, user_data.student)
    assert len(fetched_events.items) == 1


def test_list_filter(drop_in_svc: DropInService):
    """Test that a paginated list of events can be produced."""
    pagination_params = DropInPaginationParams(filter="Cynthia")
    fetched_events = drop_in_svc.get_paginated_drop_ins(pagination_params, user_data.student)
    assert len(fetched_events.items) == 1
    

def test_list_unauthenticated(drop_in_svc: DropInService):
    """Test that a user cannot view events unless authenticated."""
    with pytest.raises(UserPermissionException):
        pagination_params = DropInPaginationParams(order_by="id")
        fetched_events = drop_in_svc.get_paginated_drop_ins(pagination_params)
        pytest.fail()  # Fail test if no error was thrown above


def test_reset_drop_ins(drop_in_svc: DropInService):
    """Test the script to drop the drop_ins table and repopulated, to be done with the webhook/job
    This test also resets the demo, as the table is now populated with API data and test data has been removed.
    """

    inserted_events = drop_in_svc.reset_drop_ins()
    assert inserted_events is not None
    assert len(drop_in_svc.all()) > 0

    subprocess.run(
        [
            "python3",
            "-m",
            "backend.script.reset_demo",
        ],  # Command to reset the database to test data
        capture_output=True,  # Capture output to check for errors
        text=True,  # Capture output as text
    )


def test_parse_events(drop_in_svc: DropInService):
    """Test parsing through API response to insert in database"""
    events_dict = drop_in_svc.parse_events(drop_in_demo_data.sample_response_small)
    assert isinstance(events_dict, dict)
    assert events_dict == drop_in_demo_data.sample_parsed_response_small


def test_parse_events_large(drop_in_svc: DropInService):
    """Test parsing through API response to insert in database"""
    events_dict = drop_in_svc.parse_events(drop_in_demo_data.sample_response_large)
    assert isinstance(events_dict, dict)
    assert events_dict == drop_in_demo_data.sample_parsed_response_large


def test_get_events_api(drop_in_svc: DropInService):
    """Test the API call to Google Calendar"""
    events = drop_in_svc.get_events_api()
    assert events is not None
    assert isinstance(events, dict)


def test_create_1(drop_in_svc: DropInService):
    """Test creating an event from the event_data passed from the parse_events() to the insert_all_events() service"""
    event_1 = drop_in_demo_data.create_event_data_1
    event = drop_in_svc.create(event_1)
    assert event is not None
    assert isinstance(event, DropIn)
    assert event.title == event_1["summary"]
    assert event.start == event_1["start"]
    assert event.end == event_1["end"]
    assert event.date == event_1["date"]
    assert event.link == event_1["link"]


def test_create_2(drop_in_svc: DropInService):
    """Test creating an event from the event_data passed from the parse_events() to the insert_all_events() service"""
    event_2 = drop_in_demo_data.create_event_data_2
    event = drop_in_svc.create(event_2)
    assert event is not None
    assert isinstance(event, DropIn)
    assert event.title == event_2["summary"]
    assert event.start == event_2["start"]
    assert event.end == event_2["end"]
    assert event.date == event_2["date"]
    assert event.link == event_2["link"]


def test_insert_all_events(drop_in_svc: DropInService):
    """Test inserting events from parsed_events() service in the database"""
    inserted_events = drop_in_svc.insert_all_events(
        drop_in_demo_data.insert_all_event_data
    )
    for event_id, event_data in drop_in_demo_data.insert_all_event_data.items():
        event_in_db = drop_in_svc.get_by_id(event_id)
        assert event_in_db is not None
        assert event_in_db.id == int(event_id)
        assert event_in_db.title == event_data["summary"]
        assert event_in_db.date == event_data["date"]
        assert event_in_db.start == event_data["start"]
        assert event_in_db.end == event_data["end"]
        assert event_in_db.link == event_data["link"]


def test_insert_all_events_2(drop_in_svc: DropInService):
    """Test inserting events from parsed_events() service in the database"""
    inserted_events = drop_in_svc.insert_all_events(
        drop_in_demo_data.insert_all_event_data_2
    )
    # change to 3,4,5 bc other events have not been inserted
    for event_id, event_data in drop_in_demo_data.insert_all_event_data_2.items():
        event_in_db = drop_in_svc.get_by_id(event_id)
        assert event_in_db is not None
        assert event_in_db.id == int(event_id)
        assert event_in_db.title == event_data["summary"]
        assert event_in_db.date == event_data["date"]
        assert event_in_db.start == event_data["start"]
        assert event_in_db.end == event_data["end"]
        assert event_in_db.link == event_data["link"]
