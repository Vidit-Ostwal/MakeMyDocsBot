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
from make_my_docs_bot.tools.index_markdown import index_markdown_lines_without_context as index_markdown_lines_without_context_global
from make_my_docs_bot.tools.index_markdown import render_tree as render_tree_global
from make_my_docs_bot.tools.index_markdown import remove_children_if_not_there as remove_children_if_not_there_global

class FileIndexingToolInput(BaseModel):
    """Input schema for Branch Change Analyzer Tool."""
    file_path: str = Field(
        ..., 
        description="Engligh documentation File which has been changed"
    )

class FileIndexingTool(BaseTool):
    """Tool for fetching comprehensive GitHub issue data using GitHub's REST API."""

    name: str = "File Indexing Tool"
    description: str = (
        "Find the files in korean directory and Portuguese (Brazil) which are related to the file which are changed"
        "Index back the documentation of english files, korean and Portuguese (Brazil) files"
        "Input: file_path Output: A structure formatted response of what files and indexing of those files"
    )
    args_schema: Type[BaseModel] = FileIndexingToolInput

    def remove_children_if_not_there(self, index : Dict):
        return remove_children_if_not_there_global(index)


    def render_tree(self, node, indent=0):
        return render_tree_global(node, indent)

    # START_LINE AND END_LINE ARE INCLUDED, TO GET THE CONTENT DO END_LINE + 1
    def index_markdown_lines(self,file_path):
        index = index_markdown_lines_without_context_global(file_path=file_path)
        return self.render_tree(self.remove_children_if_not_there(index))


    def _run(self, file_path: str) -> dict:
        """Indentifies the korean, Portuguese (Brazil) files and returs the indexing of those files"""
        # Main execution
        reverse_section_mapping = {}
        
        english_file_path = file_path
        korean_file_path = file_path.replace("docs/en","docs/ko")
        portugurese_brazil_file_path = file_path.replace("docs/en","docs/pt-BR")

        parent_dir = os.path.dirname(os.getcwd())
        english_file_path = os.path.join(parent_dir, english_file_path)
        korean_file_path = os.path.join(parent_dir, korean_file_path)
        portugurese_brazil_file_path = os.path.join(parent_dir, portugurese_brazil_file_path)


        reverse_section_mapping[english_file_path] = self.index_markdown_lines(english_file_path)
        reverse_section_mapping[korean_file_path] = self.index_markdown_lines(korean_file_path)
        reverse_section_mapping[portugurese_brazil_file_path] = self.index_markdown_lines(portugurese_brazil_file_path)

        return reverse_section_mapping