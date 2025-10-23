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
            start = int(hunk.group(1)) - 1 
            length = int(hunk.group(2) or 1) - 1
            changed_lines.append((start, start + length)) # -2 because end_index is included in this search

        changed_lines = changed_lines[::-1]
        return changed_lines
    
    def make_my_object(self, object, full_object_content = True):
        return {
            "level": object['level'],
            "title": object['title'],
            "context": object['content'] if full_object_content else object['before_first_children_content'],
            "full_context_flag": full_object_content
        }

    # Both start_index and end_index are to be included in the final list
    def find_the_object(self, object, start_index, end_index):
        if not (start_index >= object['start_line'] and end_index <= object['end_line']):
            return None
        

        # Context ending before the first_children_starts 
        if len(object['children']) and start_index >= object['start_line'] and end_index < object['first_children_start_line']:
            return self.make_my_object(object, False)
        

        # Checking the childrens
        for child in object['children']:
            child_result = self.find_the_object(child, start_index, end_index)
            if child_result is not None:
                return child_result

        return self.make_my_object(object, True)
        

    def index_markdown_lines(self, lines):
        return index_markdown_lines_global(lines)


    def _run(self, feature_branch: str, file_path: str) -> str:
        """Fetch and return GitHub issue data."""
        # Main execution
        if not file_path:
            return {"message": "No .mdx files changed in docs/en/ directory"}
        
        changed_lines = self.parse_git_diff(file_path,"main",feature_branch) ## This will typically give me the lines which have changed

        parent_dir = os.path.dirname(os.getcwd())
        file_path = os.path.join(parent_dir, file_path)

        index = self.index_markdown_lines(file_path)

        changed_section_metadata = []
        for changed_line in changed_lines:
            section = self.find_the_object(index, changed_line[0],changed_line[1])
            changed_section_metadata.append(section)
        
        return changed_section_metadata