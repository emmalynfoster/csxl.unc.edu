"""Tests for the DropIn Service"""

import pytest
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


def test_get_all(drop_in_svc: DropInService):
    """Tests getting all drop-ins from the database"""
    events = drop_in_svc.all()
    assert events is not None
    assert len(events) == len(drop_in_demo_data.drop_ins)


def test_parse_events(drop_in_svc: DropInService):
    """Tests parsing through API response to insert in database"""
    events_dict = drop_in_svc.parse_events(drop_in_demo_data.sample_response)
    assert isinstance(events_dict, dict)
    assert events_dict == drop_in_demo_data.sample_parsed_response


def test_list(drop_in_svc: DropInService):
    """Test that a paginated list of events can be produced."""
    pagination_params = DropInPaginationParams(
        order_by="id",
        range_start=date_maker(days_in_future=0).isoformat(),
        range_end=date_maker(days_in_future=1).isoformat(),
    )
    fetched_events = drop_in_svc.get_paginated_drop_ins(pagination_params)
    assert len(fetched_events.items) == 1


def test_list_filter(drop_in_svc: DropInService):
    """Test that a paginated list of events can be produced."""
    pagination_params = DropInPaginationParams(filter="Cynthia")
    fetched_events = drop_in_svc.get_paginated_drop_ins(pagination_params)
    assert len(fetched_events.items) == 1
