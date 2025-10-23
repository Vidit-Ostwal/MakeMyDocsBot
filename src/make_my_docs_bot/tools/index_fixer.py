from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import os

class FileIndexFixerToolInput(BaseModel):
    """Input schema for File Index Fixer Tool."""

    file_path: str = Field(..., description="Path of the file to be modified")
    
    previous_section: str = Field(..., description="Name of the previous section")
    previous_section_start_line: int = Field(..., description="Line number where the previous section started")
    previous_section_end_line: int = Field(..., description="Line number where the previous section ended")
    
    next_section: str = Field(..., description="Name of the next section")
    next_section_start_line: int = Field(..., description="Line number where the next section starts")
    next_section_end_line: int = Field(..., description="Line number where the next section ends")
    
    new_heading: str = Field(..., description="Heading which was missing and needs to be inserted")
    level: int = Field(..., description="The level of the heading (1/2/3/4)")
    
    reason: str = Field(..., description="Explanation of how the line number was determined, referencing previous and next sections")


class FileIndexFixerTool(BaseTool):
    """Tool for replacing a specific line range in a file with new content."""

    name: str = "File Index Fixer Tool"
    description: str = (
        "Fixes the index of a particular file by adding the indexes which are not there at this moment"
    )
    args_schema: Type[BaseModel] = FileIndexFixerToolInput

    def _run(
        self,
        file_path: str,
        previous_section: str,
        previous_section_start_line: int,
        previous_section_end_line: int,
        next_section: str,
        next_section_start_line: int,
        next_section_end_line: int,
        new_heading: str,
        level: int,
        reason: str
    ) -> str:
        """Add the section heading at the desired place"""
        # Read file
        parent_dir = os.path.dirname(os.getcwd())
        file_path = os.path.join(parent_dir, file_path)

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Replace the specified range
        updated_lines = lines[: previous_section_end_line + 1] + ["\n"] + ["#"*level + " " +  new_heading] + ["\n"] +  ["\n"] + lines[previous_section_end_line+1:]

        # Write updated file
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        print(f"✅ Successfully updated file: {file_path}")

        return {
            "message": f"Lines {previous_section_end_line}-{previous_section_end_line+1} in '{file_path}' replaced successfully.",
            "new_content_preview": new_heading[:300] + ("..." if len(new_heading) > 300 else "")
        }
