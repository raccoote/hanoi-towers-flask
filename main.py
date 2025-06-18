from flask import Flask, request, render_template_string
import copy
import os

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>Towers of Hanoi</title>

<center>
<h1>Towers of Hanoi</h1>
  <p style="max-width: 600px; margin: auto; text-align: left;">
    The Towers of Hanoi is a classic puzzle invented by French mathematician Édouard Lucas in 1883. It consists of three rods and n disks of different sizes. The goal is to move all the disks from the first rod to the third, always making sure that smaller disks stay on top of the bigger ones.
    The minimum number of moves required to solve the puzzle with <strong>n</strong> disks is 2<sup>n</sup> − 1.
  </p>
<br>

  <form method="get" 
        style="display: flex; align-items: center; justify-content: center; gap: 10px; flex-wrap: wrap;">
  <label>Number of disks (1–15):</label>
  <input type="number" name="disks" min="1" max="15" value="{{ disks }}">
  <input type="submit" value="Solve">
</form>

{% if total_moves %}
  {{ current_frame|safe }}

  <form method="get" style="display: flex; flex-direction: column; align-items: center; gap: 10px;">

  <input type="hidden" name="disks" value="{{ disks }}">

  <!-- group buttons and heading -->
  <div style="display: inline-flex; align-items: center; justify-content: center; gap: 10px;">
    <button type="submit" name="prev" value="{{ move_index - 1 }}" {% if move_index == 0 %}disabled{% endif %}>
      &lt;
    </button>

    <h2 style="margin: 0;">Step {{ move_index }} / {{ total_moves }}</h2>

    <button type="submit" name="next" value="{{ move_index + 1 }}" {% if move_index >= total_moves %}disabled{% endif %}>
      &gt;
    </button>
  </div>

  <!-- slider -->
  <div style="width: 100%; display: flex; justify-content: center;">
    <input type="range" name="index" min="0" max="{{ total_moves }}" value="{{ move_index }}"
       oninput="this.nextElementSibling.value = parseInt(this.value) + 1" onchange="this.form.submit()">
  </div>

</form>

{% endif %}
  <p style="max-width: 600px; margin: auto; text-align: left;">

<br>This puzzle is often used to teach recursion. The recursive solution breaks the problem down into smaller sub-problems, solving them step by step with elegant logic.<br><br>
</p>
<div style="max-width: 600px; margin: auto;">
  <pre style="background-color: #f4f4f4; padding: 1rem; border-radius: 5px; overflow-x: auto; text-align: left;">
<code style="font-family: monospace;">
###  Python Recursive Solution  ###
def hanoi(n, source, target, auxiliary):
    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
    else:
        hanoi(n - 1, source, auxiliary, target)
        print(f"Move disk {n} from {source} to {target}")
        hanoi(n - 1, auxiliary, target, source)

# Example usage
hanoi(3, "A", "C", "B")
  </code></pre>
  <p style="font-size: 0.9em; margin-top: 20px;">
  &copy; 2025 Dimitra Pazouli · <a href="https://github.com/raccoote/hanoi-towers-flask/tree/main" target="_blank">Source Code on GitHub</a>
</p>
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
    height = 250
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
    disks = 5

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
            disks = 5

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

# uncomment for local testing
#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
