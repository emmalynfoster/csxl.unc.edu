from pydantic import BaseModel

"""Pydantic models for the `Document Section` entity."""


__author__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


class DocumentSection(BaseModel):
    """Data for a document section."""

    id: int
    title: str
    content: str
    document_id: int
