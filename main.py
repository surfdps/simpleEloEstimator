import requests
import chess.pgn
import chess.engine
import io
from colorama import Fore, Style, init
from tqdm import tqdm

# Init colorama
init(autoreset=True)

# SETTINGS
LICHESS_USERNAME = "ilysurf"
STOCKFISH_PATH = "./stockfish/stockfish-macos-m1-apple-silicon" 
DEPTH = 15

print(f"{Fore.CYAN}Fetching latest game from Lichess...{Style.RESET_ALL}")
# Fetch latest game
url = f"https://lichess.org/api/games/user/{LICHESS_USERNAME}?max=1&moves=true&pgnInJson=false"
headers = {"Accept": "application/x-chess-pgn"}
pgn_data = requests.get(url, headers=headers).text

game = chess.pgn.read_game(io.StringIO(pgn_data))
print(f"{Fore.GREEN}Game loaded successfully!{Style.RESET_ALL}")

# Extract player names from the game
white_player = game.headers.get("White", "Unknown")
black_player = game.headers.get("Black", "Unknown")
print(f"{Fore.CYAN}White: {Fore.WHITE}{white_player}{Style.RESET_ALL}")
print(f"{Fore.CYAN}Black: {Fore.WHITE}{black_player}{Style.RESET_ALL}")

def analyze_player(board, engine, color, color_name, player_name):
    total_loss = 0
    moves = 0
    blunders = mistakes = inaccuracies = best_moves = 0
    node = game
    
    # Count total moves first for progress bar
    total_moves = 0
    temp_node = game
    while temp_node.variations:
        total_moves += 1
        temp_node = temp_node.variations[0]
    
    print(f"\n{Fore.CYAN}Analyzing {color_name} ({player_name}) moves...{Style.RESET_ALL}")
    
    # Create progress bar
    with tqdm(total=total_moves, desc=f"Analyzing {color_name} ({player_name})", unit="move", 
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
        
        while node.variations:
            move = node.variations[0].move
            
            # Update progress bar description with current move
            pbar.set_description(f"Analyzing {color_name} ({player_name}) - {move}")
            
            info_before = engine.analyse(board, chess.engine.Limit(depth=DEPTH))
            best_move = info_before["pv"][0] if "pv" in info_before else None

            board.push(move)
            info_after = engine.analyse(board, chess.engine.Limit(depth=DEPTH))

            if board.turn != color:
                eval_before = info_before["score"].pov(color).score(mate_score=10000)
                eval_after = info_after["score"].pov(color).score(mate_score=10000)
                if eval_before is not None and eval_after is not None:
                    loss = eval_before - eval_after
                    if loss > 0:
                        total_loss += loss
                        # Classify errors
                        if loss >= 300:
                            blunders += 1
                        elif loss >= 100:
                            mistakes += 1
                        elif loss >= 50:
                            inaccuracies += 1
                moves += 1
                if move == best_move:
                    best_moves += 1
            
            # Update progress bar
            pbar.update(1)
            node = node.variations[0]
    
    acpl = total_loss / moves if moves > 0 else 0
    best_percent = (best_moves / moves * 100) if moves > 0 else 0
    return acpl, blunders, mistakes, inaccuracies, best_percent, moves

print(f"{Fore.CYAN}Starting Stockfish analysis engine...{Style.RESET_ALL}")
with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
    print(f"{Fore.GREEN}Engine ready! Starting analysis...{Style.RESET_ALL}")
    board = game.board()
    white_stats = analyze_player(board.copy(), engine, chess.WHITE, "White", white_player)
    black_stats = analyze_player(board.copy(), engine, chess.BLACK, "Black", black_player)

def acpl_to_elo(acpl):
    return max(800, round(2800 - 25 * acpl))

def print_stats(color_name, player_name, stats):
    acpl, blunders, mistakes, inaccuracies, best_percent, moves = stats
    elo = acpl_to_elo(acpl)

    def color_val(val, thresholds, is_percent=False):
        if is_percent:
            return (Fore.GREEN if val >= thresholds[0] else
                    Fore.YELLOW if val >= thresholds[1] else Fore.RED) + f"{val:.1f}%" + Style.RESET_ALL
        return (Fore.GREEN if val <= thresholds[0] else
                Fore.YELLOW if val <= thresholds[1] else Fore.RED) + f"{val:.1f}" + Style.RESET_ALL

    print(f"\n=== {color_name} ({player_name}) ===")
    print(f"Moves played: {moves}")
    print(f"ACPL: {color_val(acpl, (20, 50))}")
    print(f"Estimated Elo: {Fore.CYAN}{elo}{Style.RESET_ALL}")
    print(f"Best move %: {color_val(best_percent, (70, 50), is_percent=True)}")
    print(f"Inaccuracies: {Fore.YELLOW}{inaccuracies}{Style.RESET_ALL}")
    print(f"Mistakes: {Fore.MAGENTA}{mistakes}{Style.RESET_ALL}")
    print(f"Blunders: {Fore.RED}{blunders}{Style.RESET_ALL}")

print_stats("White", white_player, white_stats)
print_stats("Black", black_player, black_stats)

print(f"\n{Fore.GREEN}Analysis complete!{Style.RESET_ALL}")
