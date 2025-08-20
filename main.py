import requests
import chess.pgn
import chess.engine
import io

# SETTINGS
LICHESS_USERNAME = "ilysurf"
STOCKFISH_PATH = "./"  # change to your stockfish executable
DEPTH = 15  # analysis depth

# Fetch last game from Lichess
url = f"https://lichess.org/api/games/user/{LICHESS_USERNAME}?max=1&analysed=false&moves=true&pgnInJson=false"
headers = {"Accept": "application/x-chess-pgn"}
pgn_data = requests.get(url, headers=headers).text

# Parse PGN
game = chess.pgn.read_game(io.StringIO(pgn_data))

def analyze_player(board, engine, color):
    total_loss = 0
    moves = 0
    node = game
    while node.variations:
        move = node.variations[0].move
        info_before = engine.analyse(board, chess.engine.Limit(depth=DEPTH))
        board.push(move)
        info_after = engine.analyse(board, chess.engine.Limit(depth=DEPTH))
        if board.turn != color:  # only evaluate moves made by this player
            node = node.variations[0]
            continue
        eval_before = info_before["score"].pov(color).score(mate_score=10000)
        eval_after = info_after["score"].pov(color).score(mate_score=10000)
        if eval_before is not None and eval_after is not None:
            loss = eval_before - eval_after
            if loss > 0:  # losing centipawns only
                total_loss += loss
            moves += 1
        node = node.variations[0]
    return total_loss / moves if moves > 0 else 0

with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
    board = game.board()
    white_acpl = analyze_player(board.copy(), engine, chess.WHITE)
    black_acpl = analyze_player(board.copy(), engine, chess.BLACK)

def acpl_to_elo(acpl):
    return max(800, round(2800 - 25 * acpl))

print(f"White ACPL: {white_acpl:.1f}, Estimated Elo: {acpl_to_elo(white_acpl)}")
print(f"Black ACPL: {black_acpl:.1f}, Estimated Elo: {acpl_to_elo(black_acpl)}")
