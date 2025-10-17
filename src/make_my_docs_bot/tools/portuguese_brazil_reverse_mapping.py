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


    def index_markdown_lines(self,lines):
        index = [{
            "level": 1,
            "title": "Start of the page",
            "start_line": 0,
            "end_line": None,
            "first_children_start_line": None,
            "before_first_children_content": None,
            "content": None,
            "children_index" : [],
            "children" : []
        }]

        total_lines = len(lines)
        in_code_block = False  # Track whether we’re inside a fenced code block

        # Step 1: collect all headings with their start lines
        for i, line in enumerate(lines, start=0):
            stripped = line.strip()

            # Detect code block start/end
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue  # Don’t treat the ``` line itself as a heading

            # Skip headings inside code blocks
            if in_code_block:
                continue

            if stripped.startswith("#"):
                # Count heading level (number of leading #)
                level = stripped.count("#", 0, stripped.find(" ")) if " " in stripped else stripped.count("#")
                title = stripped.strip("# ").strip()
                index.append({
                    "level": level,
                    "title": title,
                    "start_line": i+1,
                    "end_line": None,
                    "first_children_start_line": None,
                    "before_first_children_content": None,
                    "content": None,
                    "children_index" : [],
                    "children": [],
                })

        # Step 2: determine end_line for each heading
        for j in range(len(index)):
            current_level = index[j]["level"]
            current_start = index[j]["start_line"]
            first_children_start_line = index[j]["first_children_start_line"]

            # Find the next heading with same or higher level
            next_start = None

            for k in range(j + 1, len(index)):
                if first_children_start_line is None:
                    first_children_start_line = index[k]['start_line']
                if index[k]["level"] <= current_level:
                    next_start = index[k]["start_line"]
                    break

            # If found, end is just before next heading
            first_children_start_line = (first_children_start_line - 1) if first_children_start_line else (total_lines - 1)
            end_line = (next_start - 1) if next_start else (total_lines - 1)

            index[j]["first_children_start_line"] = first_children_start_line
            index[j]["end_line"] = end_line

            # Extract content between start_line and end_line (exclusive of heading)
            content_lines = lines[current_start:end_line]
            index[j]["content"] = "".join(content_lines)
            if len(index[j]["content"]) > 300:
                index[j]["content"] = index[j]["content"][:300]


            # Extract content between start_line and first_children_start_line (exclusive of heading)
            content_lines = lines[current_start:first_children_start_line]
            index[j]["before_first_children_content"] = "".join(content_lines)
            if len(index[j]["before_first_children_content"]) > 300:
                index[j]["before_first_children_content"] = index[j]["before_first_children_content"][:300]

        # Step 3: Build hierarchy (nest children)
        root = []
        stack = []

        for item in index:
            # While stack has items and top level >= current level, pop it
            while stack and stack[-1]["level"] >= item["level"]:
                stack.pop()

            if stack:
                # Current item is child of stack top
                stack[-1]["children_index"].append(item['start_line']-1)
                stack[-1]["children"].append(item)
            else:
                # This is a top-level item
                root.append(item)

            # Push current item to stack
            stack.append(item)

        return root[0]


    def find_my_sections(self, index, level, full_context_flag):
        if index['level'] == level:
            return [{   
                "level": index['level'],
                "title": index['title'],
                "start_line": index['start_line'],
                "end_line": index['end_line'] if full_context_flag else index['first_children_start_line'],
                "existing_context": index['content'] if full_context_flag else index['before_first_children_content'],
            }]
        
        final_answer = []

        for child in index['children']:
            final_answer.append(self.find_my_sections(child, level, full_context_flag))
        
        return final_answer


    def _run(self, list_of_files: List[str], level: int, full_context_flag: bool) -> dict:
        """Indentifies the Portuguese (Brazil) files and returs the indexing of those files"""
        # Main execution
        reverse_section_mapping = {}
        for file in list_of_files:
            portugurese_brazil_file_path = file.replace("docs/en","docs/pt-BR")
    
            parent_dir = os.path.dirname(os.getcwd())
            file_path = os.path.join(parent_dir, portugurese_brazil_file_path)
            
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            sections = self.index_markdown_lines(lines)
            filtered_section = self.find_my_sections(sections, level, full_context_flag)
            reverse_section_mapping[portugurese_brazil_file_path] = filtered_section
        
        return reverse_section_mapping