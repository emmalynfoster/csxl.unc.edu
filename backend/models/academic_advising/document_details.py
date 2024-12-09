from pydantic import BaseModel
from .document_section import DocumentSection
from backend.models.academic_advising.document import Document

__author__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


class DocumentDetails(Document):
    """
    Pydantic model to represent an `Document`, including back-populated
    relationship fields.

    This model is based on the `DocumentEntity` model, which defines the shape
    of the `Document` database in the PostgreSQL database.
    """

    sections: list[DocumentSection]
