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

class BranchChangeAnalyzerToolInput(BaseModel):
    """Input schema for Branch Change Analyzer Tool."""
    feature_branch: str = Field(
        ..., 
        description="Branch name against which diff will be calculated"
    )
    file_path: str = Field(
        ..., 
        description="File path in which changes needs to be identified"
    )

class BranchChangeAnalyzerTool(BaseTool):
    """Tool for fetching comprehensive GitHub issue data using GitHub's REST API."""

    name: str = "Branch Change Analyzer Tool"
    description: str = (
        "Fetches the changed files between the feature branch and the main branch of the given file_path file"
        "Indexes the changed files and find outs the changed section in a structed format"
        "Input: feature_branch Output: A structure formatted response of what files and lines changed"
    )
    args_schema: Type[BaseModel] = BranchChangeAnalyzerToolInput

    
    def parse_git_diff(self,file_path, base_branch, compare_branch):
        # Get parent directory of current working directory
        parent_dir = os.path.dirname(os.getcwd())
        cmd = ["git", "diff", "-U0", f"{base_branch}...{compare_branch}", "--", file_path]
        result = subprocess.run(cmd, cwd=parent_dir, capture_output=True, text=True)
        diff_text = result.stdout

        changed_lines = []
        for hunk in re.finditer(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff_text):
            start = int(hunk.group(1))
            length = int(hunk.group(2) or 1)
            changed_lines.append((start - 1, start + length - 2)) # -2 because end_index is included in this search

        changed_lines = changed_lines[::-1]
        return changed_lines
    

    def make_my_object(self, object, full_object_content = True):
        return {
            "level": object['level'],
            "title": object['title'],
            "context": object['content'] if full_object_content else object['before_first_children_content'],
            "full_context_flag": full_object_content
        }


    def find_the_object(self, object, start_index, end_index):
        if object['end_line'] <= start_index or object['start_line'] > end_index:
            return None
        
        for child_index in object['children_index']:
            if child_index in list(range(start_index, end_index+1)):
                return self.make_my_object(object, True)
        
        for child in object['children']:
            child_result = self.find_the_object(child, start_index, end_index)
            if child_result is not None:
                return child_result
        
        if len(object['children']) and start_index >= object['start_line'] and end_index < object['first_children_start_line']:
            return self.make_my_object(object, False)
        
        if start_index >= object['start_line'] and end_index < object['end_line']:
            return self.make_my_object(object, True)
        
        return None


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
            first_children_start_line = (first_children_start_line - 1) if first_children_start_line else total_lines
            end_line = (next_start - 1) if next_start else total_lines

            index[j]["first_children_start_line"] = first_children_start_line
            index[j]["end_line"] = end_line

            # Extract content between start_line and end_line (exclusive of heading)
            content_lines = lines[current_start:end_line]
            index[j]["content"] = "".join(content_lines).strip()


            # Extract content between start_line and first_children_start_line (exclusive of heading)
            content_lines = lines[current_start:first_children_start_line]
            index[j]["before_first_children_content"] = "".join(content_lines).strip()

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


    def _run(self, feature_branch: str, file_path: str) -> str:
        """Fetch and return GitHub issue data."""
        # Main execution
        if not file_path:
            return {"message": "No .mdx files changed in docs/en/ directory"}
        
        changed_lines = self.parse_git_diff(file_path,"main",feature_branch) ## This will typically give me the lines which have changed

        parent_dir = os.path.dirname(os.getcwd())
        file_path = os.path.join(parent_dir, file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        index = self.index_markdown_lines(lines)
        
        with open(file_path.replace(".mdx",".json"), "w") as f:
            json.dump(index, f, indent=4) 


        changed_section_metadata = []
        for changed_line in changed_lines:
            section = self.find_the_object(index, changed_line[0],changed_line[1])
            changed_section_metadata.append(section)
        
        
        return {
            "SECTIONS_CHANGED" : changed_section_metadata,
        }