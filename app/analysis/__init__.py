import chess
import chess.pgn
import chess.engine
from io import StringIO

def parse_pgn(pgn_string) -> list:
    """Parses a PGN string and extracts moves and FEN positions."""
    pgn = chess.pgn.read_game(StringIO(pgn_string))
    if not pgn:
        raise ValueError("Invalid PGN string")

    moves = []
    board = pgn.board()
    for move in pgn.mainline_moves():
        moves.append((board.san(move), board.fen()))
        board.push(move)

    return moves

def analyze_game(moves, engine) -> dict:
    """Analyzes moves using an engine and returns a dictionary with scores."""
    analysis_results = {}

    with chess.engine.SimpleEngine.popen_uci(engine) as engine:
        board = chess.Board()

        for move in moves:
            board.push_san(move)
            info = engine.analyse(board, chess.engine.Limit(depth=20))

            if info["score"].is_mate():
                score = f"Mate in {info['score']}"
            else:
                score = info["score"].white().score()

            analysis_results[move] = score

    return analysis_results

def analyze(pgn_string, engine) -> dict | dict[str, str]:
    """Full analysis pipeline from PGN string to results."""
    try:
        moves = parse_pgn(pgn_string)
        results = analyze_game(moves, engine)
        return results
    except Exception as e:
        return {"error": str(e)}

def get_position_evaluation(fen, engine):
    """Get the position and evaluation for a specific FEN string."""
    board = chess.Board(fen)
    with chess.engine.SimpleEngine.popen_uci(engine) as engine:
        info = engine.analyse(board, chess.engine.Limit(depth=20))
        evaluation = info["score"].white().score() if not info["score"].is_mate() else f"Mate in {info['score']}"
    return board.fen(), evaluation