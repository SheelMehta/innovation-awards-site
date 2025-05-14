import pandas as pd
import json
import os

def format_paragraphs(text):
    return "".join(f"<p>{p.strip()}</p>" for p in str(text).strip().split("\n\n") if p.strip())

# Load data
df = pd.read_excel("ideas.xlsx")

with open("map_data.json", "r") as f:
    coord_dict = json.load(f)

# Coordinate lookup
coord_lookup = {}
for entry in coord_dict:
    city = entry.get("city", "").strip().lower()
    state = entry["state"].strip().lower()
    key_city = f"{city},{state}" if city else None
    key_state = state
    if key_city:
        coord_lookup[key_city] = entry
    coord_lookup[key_state] = entry

# Setup
os.makedirs("idea_pages", exist_ok=True)
cards_html = ""
map_pins = []
used_locations = {}
all_tags = set()

# Process ideas
for index, row in df.iterrows():
    id_str = f"{index + 1:02}"
    filename = f"idea_{id_str}.html"

    title = row["title"]
    summary = row["summary"]
    problem = row["problem"]
    solution = row["solution"]
    description = row["description"]
    tags = [t.strip() for t in str(row["tags"]).split(",") if t.strip()]
    name = row["name"]
    grade = row["grade"]
    school = row["school"]
    city = str(row["city"]).strip()
    state = str(row["state"]).strip()

    all_tags.update(tags)
    tag_data = " ".join(tags)
    tag_html = "".join(f"<span class='tag'>{t}</span>" for t in tags)

    cards_html += f"""
    <div class="card" data-tags="{tag_data}">
      <h2>{title}</h2>
      <p>{summary}</p>
      <div class="tags">{tag_html}</div>
      <a href="idea_pages/{filename}" target="_blank">Explore Idea →</a>
    </div>
    """

    # Page HTML
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
    .tagline {{
      writing-mode: vertical-rl;
      position: fixed;
      top: 80px;
      left: 10px;
      font-size: 14px;
      color: rgba(255, 255, 255, 0.4);
    }}
    h1 {{
      font-family: 'Orbitron', sans-serif;
      font-size: 52px;
      margin-bottom: 40px;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}
    .tabs {{
      display: flex;
      gap: 10px;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 40px;
    }}
    .tab-button {{
      background: rgba(255,255,255,0.2);
      border: none;
      padding: 10px 20px;
      color: white;
      font-size: 16px;
      border-radius: 8px;
      cursor: pointer;
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
    }}
  </style>
</head>
<body>

  <a class="back" href="../index.html">← Back</a>
  <div class="tagline">BUILT TO BE REPAIRED</div>
  <h1>{title}</h1>
  <div class="tabs">
    <button class="tab-button active" onclick="showTab('idea')">💡 Idea</button>
    <button class="tab-button" onclick="showTab('innovator')">👤 Innovator</button>
    <button class="tab-button" onclick="showTab('learn')">📘 Learn More</button>
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
  <div id="tab-innovator" class="tab-content">
    <div class="card">
      <h2>👤 {name}</h2>
      <p><strong>🎓 Class:</strong> {grade}</p>
      <p><strong>🏫 School:</strong> {school}</p>
      <p><strong>📍 City:</strong> {city}</p>
      <p><strong>🗺️ State:</strong> {state}</p>
    </div>
  </div>
  <div id="tab-learn" class="tab-content">
    <div class="card">
      <h2>📘 Learn More</h2>
      {format_paragraphs(description)}
    </div>
  </div>
  <script>
    function showTab(id) {{
      document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
      document.querySelector(`[onclick="showTab('${{id}}')"]`).classList.add('active');
      document.getElementById('tab-' + id).style.display = 'block';
    }}
  </script>
</body>
</html>""")

    # Coordinate & jitter
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
        "name": name,
        "state": state,
        "city": city,
        "lat": base["lat"] + jitter,
        "lon": base["lon"] + jitter,
        "link": f"idea_pages/{filename}"
    })

# Write pin_points.json
with open("pin_points.json", "w", encoding="utf-8") as f:
    json.dump(map_pins, f, indent=2)

# Write index.html
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