from pydantic import BaseModel

"""Pydantic models for the `Document` entity."""


__author__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


class Document(BaseModel):
    """Data for a document."""

    id: int
    title: str
    link: str
