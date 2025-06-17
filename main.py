from flask import Flask, request, render_template_string
import copy

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>Towers of Hanoi - SVG</title>
<center>
<h1>Towers of Hanoi</h1>
<form method="post" action="/">
  <label>Number of disks (1–15):</label>
  <input type="number" name="disks" min="1" max="15" value="{{ disks }}">
  <input type="submit" value="Solve">
</form>

{% if total_moves %}
  <h2>Step {{ move_index + 1 }} / {{ total_moves }}</h2>
  {{ current_frame|safe }}

  <form method="get" style="display: flex; align-items: center; justify-content: center; gap: 10px;">
    <input type="hidden" name="disks" value="{{ disks }}">

    <button type="submit" name="prev" value="{{ move_index - 1 }}" {% if move_index == 0 %}disabled{% endif %}>
      <
    </button>

    <input type="range" name="index" min="0" max="{{ total_moves - 1 }}" value="{{ move_index }}"
           oninput="this.nextElementSibling.value = parseInt(this.value) + 1" onchange="this.form.submit()">

    <button type="submit" name="next" value="{{ move_index + 1 }}" {% if move_index + 1 >= total_moves %}disabled{% endif %}>
      >
    </button>
  </form>
{% endif %}
</center>
"""

def hanoi_moves(n, source, target, auxiliary, moves):
    if n == 1:
        moves.append((source, target))
    else:
        hanoi_moves(n - 1, source, auxiliary, target, moves)
        moves.append((source, target))
        hanoi_moves(n - 1, auxiliary, target, source, moves)

def render_state(disks, moves, step):
    rods = {'A': list(reversed(range(1, disks + 1))), 'B': [], 'C': []}
    for i in range(step):
        src, dest = moves[i]
        if rods[src]:
            rods[dest].append(rods[src].pop())
    return render_svg(rods, disks)

def render_svg(rods, max_disks):
    width = 600
    height = 400
    peg_x = [150, 300, 450]
    peg_y = 200
    disk_height = 12

    svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
    # Draw pegs
    for x in peg_x:
        svg.append(f'<rect x="{x-2}" y="{peg_y - 130}" width="4" height="130" fill="#444"/>')
    # Draw Base
    svg.append(f'<rect x="10" y="{peg_y}" width="600" height="10" fill="#333"/>')
    # Draw Disks
    for i, peg in enumerate(['A', 'B', 'C']):
        for j, disk in enumerate(rods[peg]):
            w = 10 + disk * 10
            x = peg_x[i] - w // 2
            y = peg_y - (j + 1) * disk_height
            color = f"hsl({int((disk - 1) * (360 / max_disks))}, 90%, 70%)"
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{disk_height}" rx="4" fill="{color}" />')

    svg.append('</svg>')
    return '\n'.join(svg)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    move_index = int(request.args.get('index', 0))
    disks = 3

    if request.method == 'POST':
        try:
            disks = int(request.form['disks'])
            if not (1 <= disks <= 15):
                message = "Too many disks. Choose 15 or fewer."
        except:
            message = "Invalid input."
    else:
        try:
            disks = int(request.args.get('disks', 3))
        except:
            disks = 3

    if 'prev' in request.args:
        move_index = max(0, move_index - 1)
    elif 'next' in request.args:
        move_index = min(move_index + 1, 2 ** disks - 1)
    moves = []
    hanoi_moves(disks, 'A', 'C', 'B', moves)
    total_moves = len(moves)
    move_index = max(0, min(move_index, total_moves))

    current_frame = render_state(disks, moves, move_index)

    return render_template_string(TEMPLATE,
                                  current_frame=current_frame,
                                  move_index=move_index,
                                  total_moves=total_moves,
                                  disks=disks,
                                  message=message)

if __name__ == '__main__':
    app.run(debug=True)
