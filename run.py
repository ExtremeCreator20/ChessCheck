from app.analysis import *
from flask import *
import json

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")

cfile = open("config.json", "r+")

conf : dict = json.load(cfile)

ENGINE = conf["engine-path"]
PORT = conf["port"]

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/analyze", methods=['GET', 'POST'])
def analyze_route():
    analysis_result = None
    moves = []
    current_position = None
    evaluation = None
    if request.method == 'POST':
        pgn_data = request.form['pgn']
        moves = parse_pgn(pgn_data)
        analysis_result = analyze(pgn_data, ENGINE)
        if moves:
            current_position, evaluation = get_position_evaluation(moves[0][1], ENGINE)
    return render_template("analyze.html", analysis_result=analysis_result, moves=moves, current_position=current_position, evaluation=evaluation)

@app.route("/position/<fen>", methods=['GET'])
def position(fen):
    current_position, evaluation = get_position_evaluation(fen, ENGINE)
    return jsonify({"position": current_position, "evaluation": evaluation})

app.run(host='0.0.0.0', port=5000, debug=True)