from flask import Flask, render_template_string, jsonify, send_file, request
import random
import io

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Simulated Guessing Game</title>
    <style>
      body { font-family: Arial, sans-serif; text-align:center; padding:2rem; }
      #pokemon-img { width: 320px; height: 320px; border: 1px solid #ccc; }
      #status { margin-top: 1rem; }
    </style>
  </head>
  <body>
    <h1>Simulated Guessing Game</h1>
    <img id="pokemon-img" src="/pokemon/{{initial_id}}" alt="pokemon"/>
    <div>
      <input id="guess" placeholder="Type guess here" />
      <button id="submit">Submit</button>
    </div>
    <div id="status"></div>
    <script>
      async function next() {
        const res = await fetch('/next');
        const j = await res.json();
        document.getElementById('pokemon-img').src = '/pokemon/' + j.id;
        document.getElementById('status').textContent = '';
      }
      document.getElementById('submit').addEventListener('click', async () => {
        const g = document.getElementById('guess').value;
        const res = await fetch('/submit', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({guess: g, url: document.getElementById('pokemon-img').src})
        });
        const j = await res.json();
        document.getElementById('status').textContent = j.message;
      });
      setInterval(next, 3000);
    </script>
  </body>
</html>
"""

POKEDEX_SMALL = {
  1: "Bulbasaur", 4: "Charmander", 7: "Squirtle", 25: "Pikachu",
  133: "Eevee", 150: "Mewtwo", 151: "Mew"
}

def make_svg_bytes(id_):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320">
  <rect width="100%" height="100%" fill="#f7f7f7"/>
  <circle cx="160" cy="120" r="80" fill="#ddd"/>
  <text x="160" y="200" font-size="36" text-anchor="middle" fill="#333">{id_}</text>
</svg>'''
    return io.BytesIO(svg.encode("utf-8"))

@app.route("/")
def index():
    initial = random.choice(list(POKEDEX_SMALL.keys()))
    return render_template_string(TEMPLATE, initial_id=initial)

@app.route("/next")
def nxt():
    return jsonify({"id": random.choice(list(POKEDEX_SMALL.keys()))})

@app.route("/pokemon/<int:id_>")
def pokemon(id_):
    b = make_svg_bytes(id_)
    return send_file(b, mimetype="image/svg+xml")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    url = data.get("url", "")
    g = (data.get("guess") or "").strip().lower()
    import re
    m = re.search(r"/pokemon/(\d+)", url)
    if not m:
        return jsonify({"ok": False, "message": "No pokemon id found in URL."})
    correct_id = int(m.group(1))
    correct = POKEDEX_SMALL.get(correct_id, "Unknown").lower()
    if g == correct:
        msg = f"Correct — {POKEDEX_SMALL.get(correct_id, 'Unknown')}!"
    else:
        msg = f"Wrong (correct: {POKEDEX_SMALL.get(correct_id, 'Unknown')})."
    return jsonify({"ok": True, "message": msg})
    
if __name__ == "__main__":
    app.run(port=5000)
