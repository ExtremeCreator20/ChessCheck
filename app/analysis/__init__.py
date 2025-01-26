import chess
import chess.pgn
import chess.engine
from io import StringIO

def parse_pgn(pgn_string) -> tuple:
    """Parses a PGN string and extracts moves, FEN positions, and player information."""
    pgn = chess.pgn.read_game(StringIO(pgn_string))
    if not pgn:
        raise ValueError("Invalid PGN string")

    moves = []
    board = pgn.board()
    for move in pgn.mainline_moves():
        mv = board.san(move)
        board.push(move)
        moves.append((mv, board.fen()))

    white_player = pgn.headers.get("White", "Unknown")
    black_player = pgn.headers.get("Black", "Unknown")
    white_title = pgn.headers.get("WhiteTitle", "")
    black_title = pgn.headers.get("BlackTitle", "")

    return moves, white_player, black_player, white_title, black_title

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
        if info["score"].is_mate():
            evaluation = f"Mate in {info['score'].white()}"
        else:
            evaluation = info["score"].white().score()
    return board.fen(), evaluation