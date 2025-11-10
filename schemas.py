"""
Database Schemas for Criminal DBMS

Each Pydantic model corresponds to one MongoDB collection.
Collection name is the lowercase of the class name, e.g. Suspect -> "suspect".
"""
from typing import List, Optional
from pydantic import BaseModel, Field

# Suspects hold core identity data and investigative attributes
class Suspect(BaseModel):
    full_name: str = Field(..., description="Legal full name")
    aliases: List[str] = Field(default_factory=list, description="Known aliases")
    dob: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    last_known_location: Optional[str] = Field(None, description="City/Area last seen")
    risk_level: str = Field("medium", description="low | medium | high")
    status: str = Field("active", description="active | detained | cleared")
    notes: Optional[str] = Field(None, description="Investigator notes")
    tags: List[str] = Field(default_factory=list, description="Keywords for quick filtering")

# Evidence items are simple typed records linked inside cases
class EvidenceItem(BaseModel):
    type: str = Field(..., description="e.g., photo, video, document, dna")
    description: Optional[str] = None
    url: Optional[str] = Field(None, description="Optional reference or storage link")

# Cases link suspects and evidence
class Case(BaseModel):
    title: str = Field(..., description="Case title")
    description: Optional[str] = None
    status: str = Field("open", description="open | in_progress | closed")
    priority: str = Field("medium", description="low | medium | high | critical")
    suspects: List[str] = Field(default_factory=list, description="Array of suspect ObjectId strings")
    evidence: List[EvidenceItem] = Field(default_factory=list)
    lead_detective: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
