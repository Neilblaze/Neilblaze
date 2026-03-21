#!/usr/bin/env python3

import json
import math
import sys
import os
import random

import networkx as nx

CATEGORY_COLORS = {
    "AI & ML": "#2ecc71",
    "Web & Apps": "#9b59b6",
    "Infrastructure & DevOps": "#3498db",
    "Hardware & Maker": "#e67e22",
    "Languages & Compilers": "#e74c3c",
    "Other": "#7f8c8d",
}

# (topics, languages, weight) — higher weight wins ties
CATEGORY_RULES = [
    ("AI & ML", {
        "topics": {
            "machine-learning", "deep-learning", "nlp", "natural-language-processing",
            "computer-vision", "neural-network", "pytorch", "tensorflow", "transformers",
            "llm", "large-language-model", "ai", "artificial-intelligence", "generative-ai",
            "diffusion", "chatbot", "reinforcement-learning", "object-detection",
            "image-classification", "bert", "gpt", "huggingface", "onnx", "inference",
            "fine-tuning", "prompt-engineering", "rag", "speech-recognition",
            "text-generation", "multimodal", "stable-diffusion", "language-model",
        },
        "languages": {"python", "jupyter notebook"},
        "weight": 10,
    }),
    ("Infrastructure & DevOps", {
        "topics": {
            "docker", "kubernetes", "ci-cd", "devops", "automation", "infrastructure",
            "cloud", "aws", "gcp", "azure", "terraform", "ansible", "github-actions",
            "monitoring", "deployment", "serverless",
        },
        "languages": {"shell", "go", "dockerfile", "makefile"},
        "weight": 10,
    }),
    ("Hardware & Maker", {
        "topics": {
            "arduino", "raspberry-pi", "iot", "embedded", "electronics", "maker",
            "hardware", "microcontroller", "esp32", "esp8266", "fpga", "robotics",
        },
        "languages": {"c", "c++", "assembly"},
        "weight": 10,
    }),
    ("Web & Apps", {
        "topics": {
            "web", "frontend", "react", "vue", "nextjs", "api", "rest", "graphql",
            "fullstack", "website", "webapp", "chrome-extension", "pwa", "svelte",
            "angular", "flask", "fastapi", "django", "nodejs", "express",
        },
        "languages": {"javascript", "typescript", "html", "css", "php", "ruby"},
        "weight": 5,
    }),
    ("Languages & Compilers", {
        "topics": {
            "compiler", "programming-language", "parser", "interpreter",
            "language-server", "transpiler", "linter", "syntax", "ast",
        },
        "languages": {"rust", "haskell", "ocaml", "erlang", "elixir"},
        "weight": 8,
    }),
]

SVG_WIDTH = 960
SVG_HEIGHT = 600
MARGIN = 50
FOOTER_HEIGHT = 50
NODE_MIN_R = 5
NODE_MAX_R = 16
SIMILARITY_THRESHOLD = 0.15
FONT_SIZE = 12
LABEL_CHAR_WIDTH = 7.2  # approx width per char at font-size 12
LEGEND_WIDTH = 155
LEGEND_HEIGHT = 120


def escape_xml(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def get_tags(repo):
    tags = set()
    for edge in repo.get("languages", {}).get("edges", []):
        tags.add(edge["node"]["name"].lower())
    primary = repo.get("primaryLanguage")
    if primary:
        tags.add(primary["name"].lower())
    for node in repo.get("repositoryTopics", {}).get("nodes", []):
        tags.add(node["topic"]["name"].lower())
    return tags


def categorize_repo(repo):
    topics = {
        n["topic"]["name"].lower()
        for n in repo.get("repositoryTopics", {}).get("nodes", [])
    }
    primary = repo.get("primaryLanguage")
    lang = primary["name"].lower() if primary else ""

    best_cat, best_score = "Other", 0.0
    for cat_name, rules in [(r[0], r[1]) for r in CATEGORY_RULES]:
        w = rules["weight"]
        score = sum(w for t in rules["topics"] if t in topics)
        if lang in rules["languages"]:
            score += w * 0.5
        if score > best_score:
            best_score = score
            best_cat = cat_name
    return best_cat


def jaccard_similarity(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def generate_graph(repos):
    repo_tags = {}
    for repo in repos:
        repo_tags[repo["name"]] = get_tags(repo)

    G = nx.Graph()
    for repo in repos:
        name = repo["name"]
        category = repo.get("category") or categorize_repo(repo)
        tag_count = len(repo_tags[name])
        radius = min(NODE_MAX_R, max(NODE_MIN_R, NODE_MIN_R + (tag_count - 1) * 0.9))
        G.add_node(name, category=category, radius=radius, tag_count=tag_count)

    names = [r["name"] for r in repos]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            sim = jaccard_similarity(repo_tags[names[i]], repo_tags[names[j]])
            if sim > SIMILARITY_THRESHOLD:
                G.add_edge(names[i], names[j], weight=sim)

    random.seed(42)
    if len(G.nodes) == 0:
        return G, {}

    # Higher k = more spread, more iterations for convergence
    pos = nx.spring_layout(
        G,
        k=5.0 / math.sqrt(max(len(G.nodes), 1)),
        iterations=300,
        seed=42,
        scale=1.0,
    )

    plot_w = SVG_WIDTH - 2 * MARGIN
    plot_h = SVG_HEIGHT - 2 * MARGIN - FOOTER_HEIGHT

    if pos:
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        range_x = max_x - min_x if max_x != min_x else 1
        range_y = max_y - min_y if max_y != min_y else 1

        scaled_pos = {}
        for name, (x, y) in pos.items():
            sx = MARGIN + ((x - min_x) / range_x) * plot_w
            sy = MARGIN + ((y - min_y) / range_y) * plot_h
            scaled_pos[name] = (sx, sy)
    else:
        scaled_pos = {}

    return G, scaled_pos


def resolve_label_positions(scaled_pos, G):
    labels = {}
    for name, (cx, cy) in scaled_pos.items():
        radius = G.nodes[name]["radius"]
        # Place label to right by default, left if too far right
        if cx > SVG_WIDTH - MARGIN - 120:
            lx = cx - radius - 3
            anchor = "end"
        else:
            lx = cx + radius + 3
            anchor = "start"
        ly = cy + FONT_SIZE * 0.35
        labels[name] = (lx, ly, anchor)

    # Iterative nudging: push overlapping labels apart vertically
    label_list = list(labels.keys())
    for _ in range(50):
        moved = False
        for i in range(len(label_list)):
            for j in range(i + 1, len(label_list)):
                n1, n2 = label_list[i], label_list[j]
                x1, y1, a1 = labels[n1]
                x2, y2, a2 = labels[n2]

                w1 = len(n1) * LABEL_CHAR_WIDTH
                w2 = len(n2) * LABEL_CHAR_WIDTH
                h = FONT_SIZE + 2

                if a1 == "start":
                    left1, right1 = x1, x1 + w1
                else:
                    left1, right1 = x1 - w1, x1
                if a2 == "start":
                    left2, right2 = x2, x2 + w2
                else:
                    left2, right2 = x2 - w2, x2

                x_overlap = left1 < right2 and left2 < right1
                y_overlap = abs(y1 - y2) < h

                if x_overlap and y_overlap:
                    nudge = (h - abs(y1 - y2)) / 2 + 1.5
                    if y1 <= y2:
                        labels[n1] = (x1, y1 - nudge, a1)
                        labels[n2] = (x2, y2 + nudge, a2)
                    else:
                        labels[n1] = (x1, y1 + nudge, a1)
                        labels[n2] = (x2, y2 - nudge, a2)
                    moved = True
        if not moved:
            break

    return labels


def render_svg(G, scaled_pos, dark=False):
    if dark:
        bg_color = "#0d1117"
        text_color = "#e6edf3"
        text_muted = "#8b949e"
        edge_color = "#6e7681"
        legend_bg = "#161b22"
        legend_border = "#30363d"
        footer_color = "#484f58"
    else:
        bg_color = "#ffffff"
        text_color = "#1f2328"
        text_muted = "#656d76"
        edge_color = "#bcc3cd"
        legend_bg = "#f6f8fa"
        legend_border = "#d0d7de"
        footer_color = "#d0d7de"

    label_positions = resolve_label_positions(scaled_pos, G)

    lines = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_WIDTH}" height="{SVG_HEIGHT}" '
        f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">'
    )
    lines.append(
        f'  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="{bg_color}" rx="8" />'
    )

    # lines.append(
    #     f'  <text x="{SVG_WIDTH // 2}" y="24" font-family="system-ui, -apple-system, sans-serif" '
    #     f'font-size="13" fill="{text_muted}" text-anchor="middle" font-weight="500">'
    #     f'Repo Relationship Graph &#x2014; Pairwise Topic &amp; Language Similarity</text>'
    # )

    footer_y = SVG_HEIGHT - FOOTER_HEIGHT
    lines.append(
        f'  <line x1="{MARGIN}" y1="{footer_y}" x2="{SVG_WIDTH - MARGIN}" y2="{footer_y}" '
        f'stroke="{footer_color}" stroke-width="0.5" opacity="0.5" />'
    )

    eq_y1 = footer_y + 20
    lines.append(
        f'  <text x="{MARGIN}" y="{eq_y1}" font-family="system-ui, -apple-system, sans-serif" '
        f'font-size="9" fill="{text_muted}" opacity="0.6">'
        f'Updated daily via GitHub Actions \u00b7 \u00A9 Neilblaze</text>'
    )
    # lines.append(
    #     f'  <text x="{MARGIN}" y="{eq_y2}" font-family="system-ui, -apple-system, sans-serif" '
    #     f'font-size="9" fill="{text_muted}" opacity="0.6">'
    #     f'networkx spring_layout \u00b7 Jaccard similarity &gt; 0.15</text>'
    # )
    lines.append(
        f'  <text x="{SVG_WIDTH - MARGIN}" y="{eq_y1}" font-family="system-ui, -apple-system, sans-serif" '
        f'font-size="9" fill="{text_muted}" text-anchor="end" opacity="0.6">'
        f'\u24D8 {len(G.nodes)} repos \u00b7 {len(G.edges)} edges</text>'
    )

    for u, v, data in G.edges(data=True):
        if u in scaled_pos and v in scaled_pos:
            x1, y1 = scaled_pos[u]
            x2, y2 = scaled_pos[v]
            sim = data.get("weight", 0.2)
            opacity = min(0.8, max(0.15, sim * 1.1))
            stroke_w = 0.6 + sim * 1.8
            lines.append(
                f'  <line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{edge_color}" stroke-width="{stroke_w:.1f}" '
                f'opacity="{opacity:.2f}" />'
            )

    for name in G.nodes:
        if name not in scaled_pos:
            continue
        cx, cy = scaled_pos[name]
        cat = G.nodes[name]["category"]
        r = G.nodes[name]["radius"]
        color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Other"])
        if dark:
            # Glow effect
            lines.append(
                f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 4}" '
                f'fill="{color}" opacity="0.12" />'
            )
        lines.append(
            f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
            f'fill="{color}" opacity="0.88" />'
        )

    for name in G.nodes:
        if name not in label_positions:
            continue
        lx, ly, anchor = label_positions[name]
        escaped = escape_xml(name)
        text_w = len(name) * LABEL_CHAR_WIDTH
        if anchor == "start":
            rx = lx - 1
        else:
            rx = lx - text_w - 1
        ry = ly - FONT_SIZE + 1
        lines.append(
            f'  <rect x="{rx:.1f}" y="{ry:.1f}" width="{text_w + 2:.1f}" '
            f'height="{FONT_SIZE + 3}" fill="{bg_color}" opacity="0.75" rx="2" />'
        )
        lines.append(
            f'  <text x="{lx:.1f}" y="{ly:.1f}" '
            f'font-family="system-ui, -apple-system, sans-serif" '
            f'font-size="{FONT_SIZE}" fill="{text_color}" '
            f'text-anchor="{anchor}">{escaped}</text>'
        )

    legend_x = SVG_WIDTH - LEGEND_WIDTH - 12
    legend_y = 36
    lines.append(
        f'  <rect x="{legend_x}" y="{legend_y}" '
        f'width="{LEGEND_WIDTH}" height="{LEGEND_HEIGHT}" '
        f'rx="6" fill="{legend_bg}" stroke="{legend_border}" '
        f'stroke-width="1" opacity="0.95" />'
    )

    legend_cats = [
        ("AI & ML", "#2ecc71"),
        ("Web & Apps", "#9b59b6"),
        ("Infrastructure & DevOps", "#3498db"),
        ("Hardware & Maker", "#e67e22"),
        ("Languages & Compilers", "#e74c3c"),
        ("Other", "#7f8c8d"),
    ]
    for i, (cat_name, cat_color) in enumerate(legend_cats):
        ey = legend_y + 16 + i * 17
        ex = legend_x + 12
        lines.append(
            f'  <circle cx="{ex + 5}" cy="{ey}" r="5" '
            f'fill="{cat_color}" opacity="0.88" />'
        )
        lines.append(
            f'  <text x="{ex + 15}" y="{ey + 4}" '
            f'font-family="system-ui, -apple-system, sans-serif" '
            f'font-size="10" fill="{text_color}">{escape_xml(cat_name)}</text>'
        )

    # lines.append(
    #     f'  <text x="{legend_x + LEGEND_WIDTH // 2}" y="{legend_y + LEGEND_HEIGHT - 6}" '
    #     f'font-family="system-ui, -apple-system, sans-serif" '
    #     f'font-size="8" fill="{text_muted}" text-anchor="middle">'
    #     f'{len(G.nodes)} repos \u00b7 {len(G.edges)} edges</text>'
    # )

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    root_dir = os.path.dirname(os.path.dirname(__file__))
    exports_dir = os.path.join(root_dir, "assets", "exports")
    os.makedirs(exports_dir, exist_ok=True)

    categorized_path = os.path.join(root_dir, "categorized_repos.json")
    data_path = os.path.join(root_dir, "repos_data.json")
    tmp_path = "/tmp/repos_data.json"

    if os.path.exists(categorized_path):
        with open(categorized_path) as f:
            repos = json.load(f)
    elif os.path.exists(data_path):
        with open(data_path) as f:
            repos = json.load(f)
    elif not sys.stdin.isatty():
        repos = json.load(sys.stdin)
    elif os.path.exists(tmp_path):
        with open(tmp_path) as f:
            repos = json.load(f)
    else:
        print("Error: no repo data found. Provide categorized_repos.json or repos_data.json", file=sys.stderr)
        sys.exit(1)

    print(f"Generating graph for {len(repos)} repos...")

    G, pos = generate_graph(repos)
    print(f"Graph: {len(G.nodes)} nodes, {len(G.edges)} edges")

    light_path = os.path.join(exports_dir, "repo-graph.svg")
    with open(light_path, "w") as f:
        f.write(render_svg(G, pos, dark=False))
    print(f"Wrote {light_path}")

    dark_path = os.path.join(exports_dir, "repo-graph-dark.svg")
    with open(dark_path, "w") as f:
        f.write(render_svg(G, pos, dark=True))
    print(f"Wrote {dark_path}")


if __name__ == "__main__":
    main()
