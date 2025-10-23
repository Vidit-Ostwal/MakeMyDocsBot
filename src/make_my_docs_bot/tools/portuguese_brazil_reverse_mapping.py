from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List, Optional
import requests
import json
import re
import os
from datetime import datetime
import subprocess
import re
from make_my_docs_bot.tools.index_markdown import index_markdown_lines as index_markdown_lines_global
from make_my_docs_bot.tools.index_markdown import find_my_sections as find_my_sections_global

class PortugureseBrazilFileMappingToolInput(BaseModel):
    """Input schema for Branch Change Analyzer Tool."""
    list_of_files: List[str] = Field(
        ..., 
        description="Files which have been changed in the feature branch"
    )
    level: int = Field(
        ...,
        description="The level of change this is, for eg. 1 / 2 / 3 / 4"
    )
    full_context_flag: bool = Field(
        ...,
        description="Flag to know whether the entire object got changed, or partial"
    )

class PortugureseBrazilFileMappingTool(BaseTool):
    """Tool for fetching comprehensive GitHub issue data using GitHub's REST API."""

    name: str = "Portugurese Brazil File Mapping Tool"
    description: str = (
        "Find the files in Portuguese (Brazil) directory which are related to the file which are changed"
        "Indexes the Portuguese (Brazil) files and gives that back"
        "Input: list_of_files Output: A structure formatted response of what files and indexing of those files"
    )
    args_schema: Type[BaseModel] = PortugureseBrazilFileMappingToolInput


    def render_tree(self, nodes):
        """Recursively renders the tree structure as a formatted string."""
        lines = []

        for node in nodes:
            prefix = " " * int(node['level']) + f"- {node['title']} (Level:{node['level']}, lines {node['start_line']}-{node['end_line']})"
            lines.append(prefix)

        return "\n".join(lines)
    

    def find_my_sections(self, index, level, full_context_flag):
        return find_my_sections_global(index, level, full_context_flag)



    # START_LINE AND END_LINE ARE INCLUDED, TO GET THE CONTENT DO END_LINE + 1
    def index_markdown_lines(self,file_path, level, full_context_flag):
        index = index_markdown_lines_global(file_path=file_path)
        filtered_sections = self.find_my_sections(index, level, full_context_flag)
        return self.render_tree(filtered_sections)


    def _run(self, list_of_files: List[str], level: int, full_context_flag: bool) -> dict:
        """Indentifies the Portuguese (Brazil) files and returs the indexing of those files"""
        # Main execution
        reverse_section_mapping = {}
        for file in list_of_files:
            portugurese_brazil_file_path = file.replace("docs/en","docs/pt-BR")
    
            parent_dir = os.path.dirname(os.getcwd())
            file_path = os.path.join(parent_dir, portugurese_brazil_file_path)

            sections = self.index_markdown_lines(file_path, level, full_context_flag)
            reverse_section_mapping[portugurese_brazil_file_path] = sections
        
        return reverse_section_mapping