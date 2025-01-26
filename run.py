from app.analysis import *
from flask import *
import json
from urllib.parse import unquote

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")

cfile = open("config.json", "r+")

conf : dict = json.load(cfile)

ENGINE = conf["engine-path"]
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