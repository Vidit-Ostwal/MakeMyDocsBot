
from pydantic import BaseModel, Field
from typing import List, Optional

class SectionChange(BaseModel):
    FILE_PATH: str = Field(..., description="Path to the file that needs to be changed.")
    PREVIOUS_SECTION: Optional[str] = Field(None, description="Title of the previous section.")
    PREVIOUS_SECTION_START_LINE: Optional[int] = Field(None, description="Line number where the previous section started.")
    PREVIOUS_SECTION_END_LINE: Optional[int] = Field(None, description="Line number where the previous section ended.")
    NEXT_SECTION: Optional[str] = Field(None, description="Title of the next section.")
    NEXT_SECTION_START_LINE: Optional[int] = Field(None, description="Line number where the next section will start.")
    NEXT_SECTION_END_LINE: Optional[int] = Field(None, description="Line number where the next section will end.")
    NEW_HEADING_TRANSLATED: str = Field(..., description="New heading which needs to be inserted in the language (Korean or Portuguese(Brazil)), don't include English component here. Korean or Portuguese (Brazil) depending on the whether Previous sections are Korean or in Portuguese (Brazil)")
    LEVEL: int = Field(..., ge=1, le=4, description="The level of the heading (1 to 4).")
    REASON: str = Field(..., description="Explanation for how the heading position was determined, referencing nearby sections.")

class SectionChanges(BaseModel):
    """Structured list of changes required to make documentation indexing consistent."""
    changes: List[SectionChange]




class FileChange(BaseModel):
    """Represents a single section that was changed in a file."""
    
    level: int = Field(..., description="The level of the heading (1 = title, 2 = subtitle, etc.)")
    title: str = Field(..., description="The title or heading of the section that changed")
    context: str = Field(..., description="The modified context or content of the section")
    full_context_flag: bool = Field(..., description="True if the entire section was changed, False if only part of it")

class FileChanges(BaseModel):
    """Structured analysis of a file showing all changed sections."""
    changes: List[FileChange]





class FileContentUpdate(BaseModel):
    FILE_PATH: str = Field(..., description="Path to the file that needs to be updated.")
    CONTENT_TO_BE_DELETED_START_LINE: int = Field(..., ge=-1, description="Line number where content deletion starts (-1 if not applicable).")
    CONTENT_TO_BE_DELETED_END_LINE: int = Field(..., ge=-1, description="Line number where content deletion ends (-1 if not applicable).")
    NEW_CONTENT: str = Field(..., description="New translated or replacement content to be added to the file.")

class FileContentUpdates(BaseModel):
    """Structured list of file content updates to apply for translations or replacements."""
    updates: List[FileContentUpdate]