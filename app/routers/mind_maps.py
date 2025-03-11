"""Module for generate mind maps"""

import random
from fastapi import APIRouter, HTTPException
from matplotlib.patches import FancyBboxPatch
from app.locales.localization import Localization
from fastapi import Response
from pydantic import BaseModel
import matplotlib.pyplot as plt
import networkx as nx
import io
import json
from app.config import client
import textwrap

router = APIRouter()

Localization.set_language("en")


class MindMapRequest(BaseModel):
    text: str


def generate_mindmap_structure(text: str):
    """Generate structured mind map data using ChatGPT API."""
    prompt = (
        "Ensure the output is a valid JSON object in this format:\n\n"
        '{\n  "title": "Root Node",\n  "branches": [\n    {\n      "name": "Branch 1",\n      "sub_branches": [\n        {"name": "Sub-branch 1.1"}\n      ]\n    }\n  ]\n}\n\n'
        "Do not add extra text, explanations, or formatting outside the JSON and just create up to two subranches so we don't have fusion of items."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an AI that generates structured JSON for mind maps. Ensure the output is a valid JSON object",
            },
            {
                "role": "user",
                "content": f"Please generate a mind map for: {text}. {prompt}",
            },
        ],
    )

    mind_map_content = response.choices[0].message.content.strip()

    # Validate and parse JSON
    try:
        mind_map_data = json.loads(mind_map_content)

        if "title" not in mind_map_data or "branches" not in mind_map_data:
            raise ValueError("Invalid JSON format: Missing 'title' or 'branches'.")

        return mind_map_data

    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=500, detail="Failed to decode mind map structure"
        )


def hierarchical_layout(G, root=None, width=3.0, vert_gap=3.0, x_center=0.5):
    """Generate a hierarchical layout with better spacing between nodes."""
    pos = {}
    levels = {}

    def dfs(node, depth=0, x=0):
        """Recursive function to assign positions with more space between nodes."""
        if node in pos:
            return

        if depth not in levels:
            levels[depth] = []

        levels[depth].append(node)

        siblings = list(G.successors(node))
        total_siblings = len(siblings) if siblings else 1
        x_offset = width / (total_siblings + 1)

        pos[node] = (x, -depth * vert_gap)

        for i, child in enumerate(siblings):
            dfs(child, depth + 1, x + (i - (total_siblings - 1) / 2) * x_offset)

    dfs(root)
    return pos


def wrap_text(text, width=15):
    """Wraps text to fit inside the node without overflowing."""
    return "\n".join(textwrap.wrap(text, width))


def draw_mindmap(mind_map_json):
    """Create a spacious mind map with wrapped text, rounded rectangles, and varied colors."""

    # Create graph
    G = nx.DiGraph()
    root = mind_map_json["title"]
    G.add_node(root)

    def add_branches(node, branches):
        for branch in branches:
            G.add_node(branch["name"])
            G.add_edge(node, branch["name"])
            if "sub_branches" in branch:
                add_branches(branch["name"], branch["sub_branches"])

    add_branches(root, mind_map_json["branches"])

    pos = hierarchical_layout(G, root=root, width=3.5, vert_gap=3.5)

    colors = ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1"]

    # Draw edges first (so they appear below nodes)
    plt.figure(figsize=(18, 12))
    nx.draw_networkx_edges(G, pos, edge_color="gray", width=1.5, alpha=0.7)

    ax = plt.gca()
    for i, (node, (x, y)) in enumerate(pos.items()):
        color = random.choice(colors)

        wrapped_text = wrap_text(node, width=15)
        text_lines = wrapped_text.count("\n") + 1
        box_height = 0.1 + 0.025 * text_lines

        bbox = FancyBboxPatch(
            (x - 0.2, y - box_height / 2),
            0.4,
            box_height,
            boxstyle="round,pad=0.3",
            facecolor=color,
            edgecolor="black",
            linewidth=1.5,
        )
        ax.add_patch(bbox)

        plt.text(
            x,
            y,
            wrapped_text,
            ha="center",
            va="center",
            fontsize=10,
            weight="bold",
            color="white" if color in ["#6B5B95", "#FF6F61"] else "black",
        )

    # Remove axes for clean visualization
    plt.axis("off")

    # Save to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf


@router.post("/generate_mindmap")
async def generate_mindmap(request: MindMapRequest):
    try:
        # Step 1: Get structured mind map JSON from ChatGPT
        mind_map_json = generate_mindmap_structure(request.text)

        # Step 2: Convert the structured response into an image
        image_buffer = draw_mindmap(mind_map_json)

        # Step 3: Return image as response
        return Response(
            image_buffer.read(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=mindmap.png"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
