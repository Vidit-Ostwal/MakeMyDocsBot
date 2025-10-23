from typing import Type, Dict, Any, List, Optional

def index_markdown_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

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
                "start_line": i,
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
                next_start = index[k]["start_line"] - 1
                break

        # If found, end is just before next heading
        first_children_start_line = first_children_start_line if first_children_start_line else (total_lines - 1)
        end_line = next_start if next_start else (total_lines - 1)

        index[j]["first_children_start_line"] = first_children_start_line
        index[j]["end_line"] = end_line

        # Extract content between start_line and end_line (exclusive of heading)
        content_lines = lines[current_start:end_line+1]
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
            stack[-1]["children_index"].append(item['start_line'])
            stack[-1]["children"].append(item)
        else:
            # This is a top-level item
            root.append(item)

        # Push current item to stack
        stack.append(item)

    return root[0]


def find_my_sections(index, level, full_context_flag):
    if index['level'] == level:
        return [{   
            "level": index['level'],
            "title": index['title'],
            "start_line": index['start_line'],
            "end_line": index['end_line'] if full_context_flag else index['first_children_start_line'] - 1,
        }]
    
    final_answer = []

    for child in index['children']:
        final_answer.extend(find_my_sections(child, level, full_context_flag))
    
    return final_answer


def remove_children_if_not_there(index : Dict):
    if len(index['children']) == 0:
        index.pop('children',None)
        index.pop('children_index',None)
        return index
    

    for child_index in range(len(index["children"])):
        index["children"][child_index] = remove_children_if_not_there(index["children"][child_index])

    return index


def render_tree(node, indent=0):
    """Recursively renders the tree structure as a formatted string."""
    lines = []
    prefix = " " * indent + f"- {node['title']} (Level:{node['level']}, lines {node['start_line']}-{node['end_line']})"
    lines.append(prefix)

    for child in node.get('children', []):
        lines.append(render_tree(child, indent + 4))  # 4-space indentation per level

    return "\n".join(lines)


# START_LINE AND END_LINE ARE INCLUDED, TO GET THE CONTENT DO END_LINE + 1
def index_markdown_lines_without_context(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    index = [{
        "level": 1,
        "title": "Start of the page",
        "start_line": 0,
        "end_line": None,
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
                "start_line": i,
                "end_line": None,
                "children_index" : [],
                "children": [],
            })

    # Step 2: determine end_line for each heading
    for j in range(len(index)):
        current_level = index[j]["level"]
        current_start = index[j]["start_line"]

        # Find the next heading with same or higher level
        next_start = None

        for k in range(j + 1, len(index)):
            if index[k]["level"] <= current_level:
                next_start = index[k]["start_line"]
                break

        # If found, end is just before next heading
        end_line = (next_start - 1) if next_start else (total_lines - 1)

        index[j]["end_line"] = end_line


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
