from datetime import date, datetime
from fastapi import Depends
from sqlalchemy import func, select, and_, exists, or_, text
from sqlalchemy.orm import Session, aliased
import base64
from datetime import datetime, timezone
import re
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import urllib
from backend.database import db_session
from backend.entities.academic_advising.drop_in_entity import DropInEntity
from backend.models.academic_advising.drop_in import DropIn
from backend.services.academic_advising.drop_in_api import get_events, upcoming_events
from backend.models.pagination import (
    Paginated,
    PaginationParams,
    DropInPaginationParams,
)
from backend.models.user import User
from backend.services.exceptions import (
    ResourceNotFoundException,
    DropInResponseException,
    UserPermissionException,
)


__authors__ = ["Emmalyn Foster"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"

# credentials to call API, will eventually be stored in db
SERVICE_ACCOUNT_FILE = "csxl-academic-advising-feature.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# Global academic advising calendar ID
calendar_id_global = "cs.unc.edu_340oonr4ec26n1fo9l854r3ip8@group.calendar.google.com"


class DropInService:
    def __init__(
        self,
        session: Session = Depends(db_session),
    ):
        """Initializes the `DropInService` session"""
        self._session = session

    def get_paginated_drop_ins(
        self,
        pagination_params: DropInPaginationParams,
        subject: User | None = None,
    ) -> Paginated[DropIn]:
        """List Events.

        Parameters:
            pagination_params: The pagination parameters.

        Returns:
            Paginated[DropIn]: The paginated list of drop-ins.
        """

        if subject == None:
            raise UserPermissionException(
                "view", "drop-in sessions if not authenticated."
            )

        statement = select(DropInEntity)
        length_statement = select(func.count()).select_from(DropInEntity)
        if pagination_params.range_start != "":
            range_start = pagination_params.range_start
            range_end = pagination_params.range_end
            criteria = and_(
                DropInEntity.start >= datetime.fromisoformat(range_start),
                DropInEntity.start <= datetime.fromisoformat(range_end),
            )
            statement = statement.where(criteria)
            length_statement = length_statement.where(criteria)

        if pagination_params.filter != "":
            query = pagination_params.filter

            criteria = or_(
                DropInEntity.title.ilike(f"%{query}%"),
            )

            statement = statement.where(criteria)
            length_statement = length_statement.where(criteria)

        offset = pagination_params.page * pagination_params.page_size
        limit = pagination_params.page_size

        if pagination_params.order_by != "":
            statement = (
                statement.order_by(getattr(DropInEntity, pagination_params.order_by))
                if pagination_params.ascending
                else statement.order_by(
                    getattr(DropInEntity, pagination_params.order_by).desc()
                )
            )

        statement = statement.offset(offset).limit(limit)

        length = self._session.execute(length_statement).scalar()
        entities = self._session.execute(statement).scalars()

        return Paginated(
            items=[entity.to_model() for entity in entities],
            length=length,
            params=pagination_params,
        )

    def all(self) -> list[DropIn]:
        """
        Retrieves all DropIns from the table

        Returns:
            list[DropIn]: List of all `DropIn`
        """
        # Select all entries in `DropIn` table
        query = select(DropInEntity).order_by(DropInEntity.id)
        entities = self._session.scalars(query).all()

        # Convert entries to a model and return
        return [entity.to_model() for entity in entities]

    def get_by_id(self, id: int) -> DropIn:
        """Retrieves DropIn by id

        Args: id of a given drop-in

        Returns: Pydantic model representation of the given drop-in
        """
        entity = self._session.get(DropInEntity, id)

        # Check if result is null
        if entity is None:
            raise ResourceNotFoundException(f"No drop-in found with matching ID: {id}")

        # Convert entry to a model and return
        return entity.to_model()

    def reset_drop_ins(self) -> list[DropIn]:
        """Drops the DropIn table, recreates it, and repopulates it with events from the Google Calendar API
        on a reoccurring basis for consistency. Also used in webhook responses.

        Returns: a list of the inserted events as pydantic models

        """

        self._session.execute(text("DROP TABLE IF EXISTS drop_in CASCADE"))
        self._session.commit()  # Commit the DROP TABLE to finalize it

        # Recreate the table using SQLAlchemy
        DropInEntity.__table__.create(self._session.get_bind(), checkfirst=True)
        self._session.commit()

        events_response = self.get_events_api()
        if events_response is None:
            raise DropInResponseException(
                f"Error retrieving events from Google Calendar"
            )

        print(f"Resetting drop-ins")

        events_dict = self.parse_events(events_response)
        inserted_events = self.insert_all_events(events_dict)

        return inserted_events

    def get_events_api(self) -> dict:
        """Makes the call to the API to retrieve events

        Returns:
            events from Google Calendar API response
        """
        events_response = get_events(calendar_id_global, creds)
        return events_response

    def parse_events(self, events_response: dict) -> dict:
        """Parse the results from API call into a dictionary to make entity objects

        Returns:
            events_dict: dictionary with necessary information for each retrieved event to store in database

        """
        events_dict = upcoming_events(events_response)
        return events_dict

    def create(self, event_data) -> DropIn:  # type: ignore
        """Create an entity from API event data, inserts it into the session, and returns the model

        Args:

            event_data: data from an individual event returned from the API after parsing

        Returns:
            returns the model type of a DropIn object

        """
        print(f"{event_data}")
        drop_in_entity = DropInEntity(
            title=event_data["summary"],
            start=event_data["start"],
            end=event_data["end"],
            link=event_data["link"],
        )

        self._session.add(drop_in_entity)
        return drop_in_entity.to_model()

    def insert_all_events(self, events_dict: dict) -> list[DropIn]:
        """Creates and inserts all events from events_dict into the database, returned from Google Calendar API

        Args:
            events_dict (dict): A dictionary of events where each key is the event_id and
                                the value is a dictionary containing event data like title, date,
                                start_time, end_time, and link.

        Returns:
            list: A list of the inserted DropInEntity objects.
        """

        inserted_events = []  # To store the inserted DropInEntity objects

        for event_id, event_data in events_dict.items():
            drop_in = self.create(event_data)
            print(f"{drop_in}")
            print(f"Inserted DropIn with ID: {drop_in.id}")  # Log ID
            inserted_events.append(drop_in)

        # Commit the transaction
        self._session.commit()
        return inserted_events
