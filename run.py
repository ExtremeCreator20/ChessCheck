import os

os.system("python -m pip install -r requirements.txt")

from app.analysis import *
from flask import *
import json, requests, zipfile, tarfile
from urllib.parse import unquote
import platform as pf

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")

cfile = open("config.json", "r+")

conf : dict = json.load(cfile)


def download_engine(ost="win"):
    if ost == "win":
        link = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-windows-x86-64-avx2.zip"
    elif ost == "linux":
        link = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar"
    elif ost == "mac":
        link = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-macos-m1-apple-silicon.tar"
    else:
        raise Exception("Unsupported platform: " + ost)
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish." + ("zip" if ost == "win" else "tar"))

    response = requests.get(link, stream=True)

    response.raise_for_status()

    with open(dest, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):  
            file.write(chunk)
    
    return dest


def get_engine():
    pltf = pf.platform(terse=True)
    if pltf.startswith("Linux"):
        tarfile.TarFile(download_engine("linux"), 'r').extractall(os.path.join(os.path.dirname(os.path.abspath(__file__))))
        os.replace(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish", "stockfish-ubuntu-x86-64-avx2"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish-ubuntu-x86-64-avx2"))
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish-ubuntu-x86-64-avx2")
    
    elif pltf.startswith("Windows"):
        zipfile.ZipFile(download_engine("win"), 'r').extractall(os.path.join(os.path.dirname(os.path.abspath(__file__))))
        os.replace(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish", "stockfish-windows-x86-64-avx2.exe"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish-windows-x86-64-avx2.exe"))
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish-windows-x86-64-avx2.exe")
    
    elif pltf.startswith("Darwin"):
        tarfile.TarFile(download_engine("mac"), 'r').extractall(os.path.join(os.path.dirname(os.path.abspath(__file__))))
        os.replace(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish", "stockfish-macos-m1-apple-silicon"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish-macos-m1-apple-silicon"))
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish-macos-m1-apple-silicon")

    else:
        raise Exception("Unsupported platform: " + pltf)

ENGINE = get_engine()
HOST = conf["host"]
PORT = conf["port"]

stored_pgn = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global stored_pgn
    if request.method == 'POST':
        stored_pgn = request.form['pgn']
    return render_template('index.html', pgn=stored_pgn)

@app.route("/analyze", methods=['GET', 'POST'])
def analyze_route():
    global stored_pgn
    analysis_result = None
    moves = []
    current_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    evaluation = None
    white_player = black_player = "Unknown"
    white_title = black_title = "Casual Player (Unknown)"
    if request.method == 'POST':
        pgn_data = request.form['pgn']
        if pgn_data != stored_pgn:
            stored_pgn = pgn_data
        moves, white_player, black_player, white_title, black_title = parse_pgn(stored_pgn)
        analysis_result = analyze(stored_pgn, ENGINE)
        if moves:
            current_position, evaluation = get_position_evaluation(moves[1][1], ENGINE)
    return render_template("analyze.html", analysis_result=analysis_result, moves=moves, position=current_position, evaluation=evaluation, white_player=white_player, black_player=black_player, white_title=white_title, black_title=black_title)

@app.route("/position/<path:fen>", methods=['GET'])
def position(fen):
    dfen = unquote(fen)
    current_position, evaluation = get_position_evaluation(dfen, ENGINE)
    return jsonify({"position": current_position, "evaluation": evaluation})

@app.route("/settings", methods=['GET'])
def settings():
    return render_template("settings.html", settings=conf)

@app.route("/settings/change/<setting>", methods=["POST"])
def changesetting(setting):
    value = request.form['value']
    conf[setting] = value
    with open("config.json", "w") as cfile:
        json.dump(conf, cfile, indent=4)
    return redirect(url_for('settings'))

app.run(host=HOST, port=PORT, debug=True)