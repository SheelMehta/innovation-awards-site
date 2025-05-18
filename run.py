import pandas as pd
import json
import os
import re

def format_paragraphs(text):
    """Converts double-newline-separated paragraphs to <p> tags."""
    return "".join(f"<p>{p.strip()}</p>" for p in str(text).strip().split("\n\n") if p.strip())

def get_status_badge(status):
    """Returns a colored badge for the status field."""
    if not status or status.lower() == "idea":
        return ""
    color = "#FFD600" if "poc" in status.lower() else "#5eead4"
    txt = "PoC developed" if "poc" in status.lower() else status
    return f"<div class='status-badge' style='background:{color};color:#1e1b4b;padding:7px 20px;border-radius:22px;font-weight:700;display:inline-block;margin-left:16px;'>{txt}</div>"

def get_teacher_line(teacher):
    """Returns a teacher-assist line if applicable."""
    if teacher.strip().lower() == "yes":
        return '<div class="teacher-note" style="color:#22c55e;margin-top:10px;font-size:15px;"><span style="font-size:18px;margin-right:7px;">👩‍🏫</span><span>Teacher assisted the student in submitting this entry.</span></div>'
    return ""

def get_poc_embed(poc):
    """Returns embed html for PoC if YouTube or other."""
    poc = poc.strip()
    # YouTube embed
    yt_match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})", poc)
    if yt_match:
        yt_id = yt_match.group(1)
        return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{yt_id}" frameborder="0" allowfullscreen></iframe>'
    # Image
    if poc.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return f'<img src="{poc}" alt="Proof of Concept Image" style="max-width:100%;border-radius:14px;">'
    # Video
    if poc.lower().endswith(('.mp4', '.webm', '.ogg')):
        return f'<video controls style="max-width:100%;border-radius:14px;"><source src="{poc}">Your browser does not support the video tag.</video>'
    # Fallback: clickable link
    if poc:
        return f'<a class="org-link" href="{poc}" target="_blank" style="padding:14px 38px;display:inline-block;background:#00FFD0;color:#1e1b4b;border-radius:12px;font-weight:bold;text-decoration:none;margin:18px 0;">🔗 Open Demo / Prototype</a>'
    return ""

# === Load Data ===
df = pd.read_excel("ideas.xlsx")
with open("map_data.json", "r") as f:
    coord_dict = json.load(f)

coord_lookup = {}
for entry in coord_dict:
    city = entry.get("city", "").strip().lower()
    state = entry["state"].strip().lower()
    key_city = f"{city},{state}" if city else None
    key_state = state
    if key_city:
        coord_lookup[key_city] = entry
    coord_lookup[key_state] = entry

os.makedirs("idea_pages", exist_ok=True)
cards_html = ""
map_pins = []
used_locations = {}
all_tags = set()

# === Process each idea ===
for index, row in df.iterrows():
    id_str = f"{index + 1:02}"
    filename = f"idea_{id_str}.html"

    # Fields
    title = row.get("title", "").strip()
    summary = row.get("summary", "").strip()
    problem = row.get("problem", "").strip()
    solution = row.get("solution", "").strip()
    description = row.get("description", "").strip()
    tags = [t.strip() for t in str(row.get("tags", "")).split(",") if t.strip()]
    name = row.get("name", "").strip()
    grade = str(row.get("grade", "")).strip()
    school = str(row.get("school", "")).strip()
    city = str(row.get("city", "")).strip()
    state = str(row.get("state", "")).strip()
    year = str(row.get("year", "")).strip()
    age = str(row.get("age", "")).strip()
    status = str(row.get("status", "")).strip()
    poc = str(row.get("poc", "")).strip()
    teacher = str(row.get("teacher", "")).strip()

    all_tags.update(tags)
    tag_data = " ".join(tags)
    tag_html = "".join(f"<span class='tag'>{t}</span>" for t in tags)

    # === Innovator Card (no photos, no cartoon) ===
    school_line = f'<div class="innovator-row"><span class="innovator-icon">🏫</span><span class="innovator-detail"><strong>School:</strong> {school}</span></div>' if school else ''
    year_line = f'<div class="innovator-row"><span class="innovator-icon">🕰️</span><span class="innovator-detail"><strong>Year awarded:</strong> {year}</span></div>' if year else ''
    age_line = f'<div class="innovator-row"><span class="innovator-icon">🎂</span><span class="innovator-detail"><strong>Age:</strong> {age}</span></div>' if age else ''
    teacher_line = get_teacher_line(teacher)
    status_badge = get_status_badge(status)

    innovator_card = f"""
    <div class="innovator-card">
      <div style="display:flex; justify-content: space-between; align-items: flex-start;">
        <div>
          <div class="innovator-row" style="margin-bottom: 12px;">
            <span class="innovator-icon" style="font-size: 34px;">👤</span>
            <span class="innovator-detail" style="font-size: 1.45em; font-weight: bold; margin-left: 10px;">{name}</span>
          </div>
          <div class="innovator-row"><span class="innovator-icon">🎓</span><span class="innovator-detail"><strong>Class:</strong> {grade}</span></div>
          {school_line}
          <div class="innovator-row"><span class="innovator-icon">📍</span><span class="innovator-detail"><strong>City:</strong> {city}</span></div>
          <div class="innovator-row"><span class="innovator-icon">🗺️</span><span class="innovator-detail"><strong>State:</strong> {state}</span></div>
          {year_line}
          {age_line}
          {teacher_line}
        </div>
        {status_badge}
      </div>
    </div>
    """

    # === PoC Tab Logic ===
    poc_tab_button = ""
    poc_tab_content = ""
    if isinstance(poc, str) and poc.strip().lower() not in ["", "nan"]:
        poc_tab_button = '<button class="tab-button" onclick="showTab(\'poc\')">🔬 Proof of Concept</button>'
        embed_html = get_poc_embed(poc)
        poc_tab_content = f"""
        <div id="tab-poc" class="tab-content">
          <h2 style="color:#00FFD0; font-family:'Orbitron',sans-serif; font-size:22px;">🔬 Proof of Concept Demo</h2>
          <div style="display:flex;justify-content:center;">{embed_html}</div>
        </div>
        """

    # === Cards for Gallery ===
    cards_html += f"""
    <div class="card" data-tags="{tag_data}">
      <h2>{title}</h2>
      <p>{summary}</p>
      <div class="tags">{tag_html}</div>
      <a href="idea_pages/{filename}" target="_blank">Explore Idea →</a>
    </div>
    """

    # === Write Idea Page ===
    with open(f"idea_pages/{filename}", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600&family=Inter&display=swap" rel="stylesheet"/>
  <style>
    body {{
      margin: 0;
      background: linear-gradient(135deg, #2e1065, #9333EA);
      color: white;
      font-family: 'Inter', sans-serif;
      padding: 80px 20px;
      text-align: center;
      overflow-x: hidden;
    }}
    h1 {{
      font-family: 'Orbitron', sans-serif;
      font-size: 52px;
      margin-bottom: 18px;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}
    .innovator-card {{
      background: rgba(0,0,0,0.28);
      border-radius: 22px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.18);
      max-width: 540px;
      margin: 32px auto 20px auto;
      padding: 30px 32px 24px 32px;
      text-align: left;
      position: relative;
    }}
    .innovator-row {{
      display: flex;
      align-items: center;
      margin-bottom: 8px;
    }}
    .innovator-row:last-child {{ margin-bottom: 0; }}
    .innovator-icon {{
      font-size: 21px;
      margin-right: 8px;
      min-width: 24px;
      text-align: center;
    }}
    .innovator-detail {{
      font-size: 1em;
      color: #fff;
    }}
    .teacher-note {{
      margin-top: 12px;
      font-size: 16px;
      color: #22c55e;
      display: flex;
      align-items: center;
    }}
    .status-badge {{
      background: #FFD600;
      color: #232946;
      padding: 7px 16px;
      border-radius: 18px;
      font-weight: 700;
      font-size: 15px;
      box-shadow: 0 1px 7px rgba(0,0,0,0.11);
      margin-left: 14px;
      margin-top: 6px;
      display: inline-block;
      white-space: nowrap;
    }}
    .tabs {{
      display: flex;
      gap: 10px;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 40px;
      margin-top: 22px;
    }}
    .tab-button {{
      background: rgba(255,255,255,0.2);
      border: none;
      padding: 13px 38px;
      color: white;
      font-size: 20px;
      border-radius: 14px;
      cursor: pointer;
      font-family: 'Inter', sans-serif;
      font-weight: bold;
      transition: background 0.16s, color 0.16s;
    }}
    .tab-button.active {{
      background: #facc15;
      color: #1e1b4b;
    }}
    .tab-content {{
      display: none;
      max-width: 900px;
      margin: auto;
    }}
    .card {{
      position: relative;
      padding: 40px 30px;
      border-radius: 16px;
      margin-bottom: 40px;
      box-shadow: 0 12px 40px rgba(0,0,0,0.4);
      font-size: 20px;
      text-align: left;
    }}
    .card.problem {{
      background: rgba(0,0,0,0.4);
      border-left: 8px solid #ef4444;
    }}
    .card.problem::before {{
      content: "✖";
      position: absolute;
      font-size: 120px;
      color: rgba(255, 255, 255, 0.05);
      top: 10px;
      left: 20px;
    }}
    .card.solution {{
      background: rgba(255,255,255,0.07);
      border-left: 8px solid #facc15;
    }}
    .card.solution::before {{
      content: "✔";
      position: absolute;
      font-size: 120px;
      color: rgba(255, 255, 255, 0.05);
      top: 10px;
      right: 20px;
    }}
    .card h2 {{
      font-family: 'Orbitron', sans-serif;
      font-size: 28px;
      margin-bottom: 20px;
    }}
    .card p {{
      line-height: 1.7;
    }}
    .back {{
      position: fixed;
      top: 20px;
      left: 20px;
      background: #5eead4;
      color: #1e1b4b;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: bold;
      text-decoration: none;
      z-index: 2;
      font-size: 18px;
    }}
    a.org-link {{
      color: #00FFD0;
      text-decoration: underline;
      font-weight: bold;
      transition: color 0.2s;
      word-break: break-all;
    }}
    a.org-link:visited {{
      color: #B388FF;
    }}
    a.org-link:hover,
    a.org-link:active {{
      color: #38bdf8;
    }}
    .share-button {{
      margin: 24px auto 42px auto;
      display: block;
      background: #5eead4;
      color: #1e1b4b;
      font-weight: bold;
      border: none;
      padding: 13px 32px;
      font-size: 21px;
      border-radius: 15px;
      cursor: pointer;
      box-shadow: 0 2px 16px rgba(0,255,208,0.13);
      transition: background 0.15s;
    }}
    .share-button:hover {{
      background: #00FFD0;
      color: #232946;
    }}
  </style>
</head>
<body>

  <a class="back" href="../ideas.html">← Back</a>
  <h1>{title}</h1>
  {innovator_card}
  <button class="share-button" onclick="navigator.clipboard.writeText(window.location.href);alert('🔗 Copied the page URL!')">📤 Share This Innovation</button>
  <div class="tabs">
    <button class="tab-button active" onclick="showTab('idea')">💡 Idea</button>
    <button class="tab-button" onclick="showTab('learn')">📘 Learn More</button>
    {poc_tab_button}
  </div>
  <div id="tab-idea" class="tab-content" style="display:block;">
    <div class="card problem">
      <h2>The Problem</h2>
      {format_paragraphs(problem)}
    </div>
    <div class="card solution">
      <h2>The Solution</h2>
      {format_paragraphs(solution)}
    </div>
  </div>
  <div id="tab-learn" class="tab-content">
    <div class="card">
      <h2>📘 Learn More</h2>
      {format_paragraphs(description)}
    </div>
  </div>
  {poc_tab_content}
  <script>
    function showTab(id) {{
      document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
      document.querySelector(`[onclick="showTab('${{id}}')"]`).classList.add('active');
      document.getElementById('tab-' + id).style.display = 'block';
    }}
  </script>
</body>
</html>
""")

    # === Map Pin Logic ===
    city_key = f"{city.lower()},{state.lower()}"
    state_key = state.lower()
    base = coord_lookup.get(city_key) or coord_lookup.get(state_key)
    if not base:
        continue
    coord_key = f"{base['lat']},{base['lon']}"
    used = used_locations.get(coord_key, 0)
    used_locations[coord_key] = used + 1
    jitter = 0.15 * used
    map_pins.append({
        "title": title,
        "name": name,
        "state": state,
        "city": city,
        "lat": base["lat"] + jitter,
        "lon": base["lon"] + jitter,
        "link": f"idea_pages/{filename}"
    })

# === Write pin_points.json ===
with open("pin_points.json", "w", encoding="utf-8") as f:
    json.dump(map_pins, f, indent=2)

# === Write ideas.html (gallery) ===
with open("ideas.html", "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Innovation Gallery</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600&family=Inter&display=swap" rel="stylesheet">
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      min-height: 100vh;
      background: linear-gradient(135deg, #2e1065, #9333EA);
      font-family: 'Inter', sans-serif;
      color: white;
      text-align: center;
    }}
    h1 {{
      font-family: 'Orbitron', sans-serif;
      font-size: 36px;
      margin: 40px 0 20px;
    }}
    .toolbar {{
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 10px;
    }}
    .tag-filter {{
      padding: 8px 14px;
      background: rgba(255, 255, 255, 0.1);
      border: none;
      color: white;
      border-radius: 20px;
      font-size: 14px;
      cursor: pointer;
    }}
    .tag-filter.active {{
      background: #14b8a6;
      color: black;
    }}
    .surprise {{
      background: #5eead4;
      color: #1e1b4b;
      border: none;
      padding: 8px 16px;
      font-weight: bold;
      border-radius: 8px;
      cursor: pointer;
    }}
    .grid {{
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 30px;
      padding-bottom: 60px;
    }}
    .card {{
      background: rgba(255,255,255,0.08);
      padding: 20px;
      width: 280px;
      border-radius: 16px;
      box-shadow: 0 6px 30px rgba(0,0,0,0.3);
      text-align: left;
      transition: transform 0.3s ease;
    }}
    .card:hover {{
      transform: scale(1.03);
      background: rgba(255,255,255,0.12);
    }}
    .card h2 {{
      font-family: 'Orbitron', sans-serif;
      font-size: 22px;
      margin: 0 0 10px 0;
      color: #5eead4;
    }}
    .card p {{
      font-size: 15px;
      margin: 0;
      line-height: 1.4;
    }}
    .card a {{
      display: inline-block;
      margin-top: 12px;
      text-decoration: none;
      font-weight: bold;
      background: #5eead4;
      color: #1e1b4b;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 14px;
    }}
    .tags {{
      margin-top: 12px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .tag {{
      background: rgba(20, 184, 166, 0.15);
      border: 1px solid #14b8a6;
      color: #99f6e4;
      border-radius: 20px;
      padding: 4px 12px;
      font-size: 12px;
      font-weight: 500;
    }}
    .back {{
      position: fixed;
      top: 20px;
      left: 20px;
      background: #5eead4;
      color: #1e1b4b;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: bold;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <a class="back" href="index.html">← Back</a>
  <h1>🧠 Innovation Gallery</h1>
  <div class="toolbar">
    {"".join(f"<button class='tag-filter' onclick=\"toggleTag('{tag}')\">{tag}</button>" for tag in sorted(all_tags))}
    <button class="surprise" onclick="surpriseMe()">🎲 Surprise Me</button>
  </div>
  <div class="grid" id="cardGrid">
    {cards_html}
  </div>
  <script>
    let activeTags = new Set();
    function toggleTag(tag) {{
      const button = document.querySelector(`.tag-filter[onclick*="${{tag}}"]`);
      if (activeTags.has(tag)) {{
        activeTags.delete(tag);
        button.classList.remove('active');
      }} else {{
        activeTags.add(tag);
        button.classList.add('active');
      }}
      applyFilter();
    }}
    function applyFilter() {{
      const cards = document.querySelectorAll('.card');
      cards.forEach(card => {{
        const tags = card.getAttribute('data-tags');
        const matches = Array.from(activeTags).some(tag => tags.includes(tag));
        if (activeTags.size === 0 || matches) {{
          card.style.display = "block";
        }} else {{
          card.style.display = "none";
        }}
      }});
    }}
    function surpriseMe() {{
      const visibleCards = Array.from(document.querySelectorAll('.card')).filter(card => card.style.display !== "none");
      if (visibleCards.length === 0) return;
      const randomCard = visibleCards[Math.floor(Math.random() * visibleCards.length)];
      const link = randomCard.querySelector("a").href;
      window.open(link, "_blank");
    }}
  </script>
</body>
</html>""")
