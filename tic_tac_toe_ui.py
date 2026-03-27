import http.server
import socketserver
import json
import urllib.parse
import os
import webbrowser
import threading
import time

# Configuration
PORT = 5500
# Ensure we serve from the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class TicTacToeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [None] * 9
        self.current_player = "X"
        self.winner = None
        self.winning_line = None
        self.scores = {"X": 0, "O": 0}
        self.draw = False

    def make_move(self, index):
        if index < 0 or index > 8 or self.board[index] or self.winner or self.draw:
            return False
        
        self.board[index] = self.current_player
        if self.check_winner():
            self.winner = self.current_player
            self.scores[self.current_player] += 1
        elif all(self.board):
            self.draw = True
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
        return True

    def check_winner(self):
        win_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Cols
            [0, 4, 8], [2, 4, 6]             # Diagonals
        ]
        for combo in win_combinations:
            if self.board[combo[0]] and self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]]:
                self.winning_line = combo
                return True
        return False

# Global game state
game = TicTacToeGame()

class GameRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            state = {
                "board": game.board,
                "currentPlayer": game.current_player,
                "winner": game.winner,
                "winningLine": game.winning_line,
                "scores": game.scores,
                "draw": game.draw
            }
            self.wfile.write(json.dumps(state).encode())
        elif parsed_path.path == '/move':
            query = urllib.parse.parse_qs(parsed_path.query)
            try:
                idx = int(query.get('index', [0])[0])
                success = game.make_move(idx)
            except (ValueError, IndexError):
                success = False
            self.send_response(200 if success else 400)
            self.end_headers()
        elif parsed_path.path == '/reset':
            game.reset()
            self.send_response(200)
            self.end_headers()
        else:
            super().do_GET()

    def log_message(self, format, *args):
        # Suppress logging for cleaner terminal output
        return

def open_browser():
    time.sleep(1.5) # Wait for server to start
    url = f"http://localhost:{PORT}"
    print(f"\n[INFO] Opening game in browser: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    print("-" * 45)
    print("      TIC TAC TOE - MODERN EDITION")
    print("-" * 45)
    print(f"Starting server on port {PORT}...")
    
    # Run browser opener in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    Handler = GameRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server is LIVE at http://localhost:{PORT}")
            print("Press Ctrl+C to shut down.")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:
            print(f"\n[ERROR] Port {PORT} is already in use.")
            print("The game might already be running, or another app is using this port.")
            print("Please close other instances or try a different port.")
        else:
            print(f"\n[ERROR] OS error: {e}")
    except KeyboardInterrupt:
        print("\n\nStopping server. Thanks for playing!")
    except Exception as e:
        print(f"\n[ERROR] {e}")
