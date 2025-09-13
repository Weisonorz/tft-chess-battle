import pygame
from typing import Optional, List, Tuple
from board import Board
from piece import Piece, Color, PieceType
from enum import Enum

class GameState(Enum):
    PLAYING = "playing"
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    PAUSED = "paused"

class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = Color.WHITE
        self.selected_piece = None
        self.selected_row = -1
        self.selected_col = -1
        self.valid_moves = []
        self.attack_targets = []
        self.game_state = GameState.PLAYING
        self.action_mode = "move"  # "move" or "attack"
        self.game_log = []
        self.font = None
        self.load_assets()
        
    def load_assets(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        
        # Load board sprite
        try:
            self.board.load_board_sprite("Hackathon_image/chessboard.png")
        except:
            print("Could not load board sprite")
            
        # Load piece sprites
        piece_files = {
            PieceType.PAWN: "pawn.png",
            PieceType.KNIGHT: "knight.png", 
            PieceType.BISHOP: "king1.png",  # Using king1 as bishop placeholder
            PieceType.ROOK: "king2.png",    # Using king2 as rook placeholder
            PieceType.QUEEN: "queen.png",
            PieceType.KING: "king.png"
        }
        
        for piece_type, filename in piece_files.items():
            try:
                sprite_path = f"Hackathon_image/{filename}"
                sprite = pygame.image.load(sprite_path)
                
                # Apply sprite to all pieces of this type
                for piece in self.board.get_all_pieces():
                    if piece.piece_type == piece_type:
                        piece.sprite = sprite
            except:
                print(f"Could not load sprite for {piece_type}")
    
    def handle_click(self, mouse_x: int, mouse_y: int):
        if self.game_state != GameState.PLAYING:
            return
            
        row, col = self.board.get_cell_from_mouse(mouse_x, mouse_y)
        
        if not self.board.is_valid_position(row, col):
            return
            
        clicked_piece = self.board.get_piece_at(row, col)
        
        # If no piece is selected
        if self.selected_piece is None:
            if clicked_piece and clicked_piece.color == self.current_player and clicked_piece.is_alive():
                self.select_piece(clicked_piece, row, col)
        else:
            # If clicking on the same piece, deselect
            if row == self.selected_row and col == self.selected_col:
                self.deselect_piece()
            # If clicking on a valid move
            elif (row, col) in self.valid_moves and self.action_mode == "move":
                self.make_move(self.selected_row, self.selected_col, row, col)
            # If clicking on a valid attack target
            elif (row, col) in self.attack_targets and self.action_mode == "attack":
                self.make_attack(self.selected_row, self.selected_col, row, col)
            # If clicking on another piece of the same color
            elif clicked_piece and clicked_piece.color == self.current_player and clicked_piece.is_alive():
                self.select_piece(clicked_piece, row, col)
            else:
                self.deselect_piece()
    
    def select_piece(self, piece: Piece, row: int, col: int):
        self.selected_piece = piece
        self.selected_row = row
        self.selected_col = col
        self.valid_moves = piece.get_valid_moves(self.board.grid)
        self.attack_targets = piece.get_attack_targets(self.board.grid)
        self.action_mode = "move"  # Start with movement mode
        
    def deselect_piece(self):
        self.selected_piece = None
        self.selected_row = -1
        self.selected_col = -1
        self.valid_moves = []
        self.attack_targets = []
        self.action_mode = "move"
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        moving_piece = self.board.get_piece_at(from_row, from_col)
        
        if not moving_piece or not moving_piece.is_alive():
            return
            
        # Move the piece (should only be to empty squares)
        target_piece = self.board.get_piece_at(to_row, to_col)
        if target_piece is None:  # Only move to empty squares
            self.board.move_piece(from_row, from_col, to_row, to_col)
            move_msg = f"{moving_piece.piece_type.value.title()} moves to {chr(ord('a') + to_col)}{8 - to_row}"
            self.add_to_log(move_msg)
            
        self.deselect_piece()
        self.switch_player()
        self.check_win_condition()
    
    def make_attack(self, attacker_row: int, attacker_col: int, target_row: int, target_col: int):
        attacking_piece = self.board.get_piece_at(attacker_row, attacker_col)
        target_piece = self.board.get_piece_at(target_row, target_col)
        
        if not attacking_piece or not attacking_piece.is_alive():
            return
        if not target_piece or not target_piece.is_alive():
            return
            
        # Check if attack is valid
        if not attacking_piece.can_attack(target_row, target_col, self.board.grid):
            return
            
        # Handle combat
        self.handle_combat(attacking_piece, target_piece)
        
        # Remove dead pieces (only defender should die in normal attacks)
        if not target_piece.is_alive():
            self.board.grid[target_row][target_col] = None
            
        self.deselect_piece()
        self.switch_player()
        self.check_win_condition()
    
    def handle_combat(self, attacker: Piece, defender: Piece):
        # Attacker deals damage to defender
        defender.take_damage(attacker.attack)
        combat_msg = f"{attacker.color.value.title()} {attacker.piece_type.value.title()} attacks {defender.color.value.title()} {defender.piece_type.value.title()} for {attacker.attack} damage"
        self.add_to_log(combat_msg)
        
        # Check if defender is destroyed
        if not defender.is_alive():
            death_msg = f"{defender.color.value.title()} {defender.piece_type.value.title()} is destroyed!"
            self.add_to_log(death_msg)
        else:
            hp_msg = f"{defender.color.value.title()} {defender.piece_type.value.title()} has {defender.hp}/{defender.max_hp} HP remaining"
            self.add_to_log(hp_msg)
    
    def switch_player(self):
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        turn_msg = f"{self.current_player.value.title()}'s turn"
        self.add_to_log(turn_msg)
    
    def check_win_condition(self):
        white_king_alive = self.board.is_king_alive(Color.WHITE)
        black_king_alive = self.board.is_king_alive(Color.BLACK)
        
        if not white_king_alive:
            self.game_state = GameState.BLACK_WINS
            self.add_to_log("BLACK WINS! White King defeated!")
        elif not black_king_alive:
            self.game_state = GameState.WHITE_WINS
            self.add_to_log("WHITE WINS! Black King defeated!")
    
    def add_to_log(self, message: str):
        self.game_log.append(message)
        if len(self.game_log) > 8:  # Keep only last 8 messages
            self.game_log.pop(0)
    
    def draw_ui(self, screen: pygame.Surface):
        # Draw elegant title with shadow
        shadow_color = (50, 50, 50)
        title_color = (255, 215, 100)  # Gold
        title_text = "♔ RETRO PIXEL CHESS BATTLE ♔"
        
        title_shadow = self.title_font.render(title_text, True, shadow_color)
        title_main = self.title_font.render(title_text, True, title_color)
        
        title_x = screen.get_width() // 2 - title_main.get_width() // 2
        screen.blit(title_shadow, (title_x + 2, 22))
        screen.blit(title_main, (title_x, 20))
        
        # Draw turn indicator with elegant styling
        if self.game_state == GameState.PLAYING:
            turn_color = (255, 255, 100) if self.current_player == Color.WHITE else (150, 150, 255)
            turn_text = f"⚔ {self.current_player.value.upper()}'S TURN ⚔"
            turn_surface = self.font.render(turn_text, True, turn_color)
            turn_x = screen.get_width() // 2 - turn_surface.get_width() // 2
            screen.blit(turn_surface, (turn_x, 75))
        elif self.game_state == GameState.WHITE_WINS:
            win_text = self.title_font.render("⚔ WHITE VICTORY! ⚔", True, (255, 215, 100))
            win_x = screen.get_width() // 2 - win_text.get_width() // 2
            screen.blit(win_text, (win_x, 75))
        elif self.game_state == GameState.BLACK_WINS:
            win_text = self.title_font.render("⚔ BLACK VICTORY! ⚔", True, (255, 215, 100))
            win_x = screen.get_width() // 2 - win_text.get_width() // 2
            screen.blit(win_text, (win_x, 75))
        
        # Enhanced stats panel
        if self.selected_piece:
            panel_x = 50
            panel_y = 150
            panel_width = 180
            panel_height = 120
            
            # Draw stats panel background
            panel_color = (40, 40, 60)
            border_color = (100, 100, 120)
            pygame.draw.rect(screen, panel_color, (panel_x, panel_y, panel_width, panel_height))
            pygame.draw.rect(screen, border_color, (panel_x, panel_y, panel_width, panel_height), 2)
            
            # Panel title
            title = self.font.render("SELECTED PIECE", True, (255, 215, 100))
            screen.blit(title, (panel_x + 10, panel_y + 10))
            
            # Piece info
            piece_name = self.selected_piece.piece_type.value.upper()
            color_name = self.selected_piece.color.value.upper()
            
            info_lines = [
                f"{color_name} {piece_name}",
                f"❤ HP: {self.selected_piece.hp}/{self.selected_piece.max_hp}",
                f"⚔ ATK: {self.selected_piece.attack}",
                f"💰 Cost: {self.selected_piece.cost if self.selected_piece.cost != float('inf') else '∞'}"
            ]
            
            for i, line in enumerate(info_lines):
                color = (255, 255, 255) if i == 0 else (200, 200, 200)
                text = self.small_font.render(line, True, color)
                screen.blit(text, (panel_x + 10, panel_y + 35 + i * 18))
            
            # Show current action mode
            mode_text = f"Mode: {self.action_mode.upper()}"
            mode_color = (100, 255, 100) if self.action_mode == "move" else (255, 100, 100)
            mode_surface = self.small_font.render(mode_text, True, mode_color)
            screen.blit(mode_surface, (panel_x + 10, panel_y + 95))
        
        # Enhanced game log - moved higher to not block board
        log_x = 50
        log_y = screen.get_height() - 140  # Reduced from 180 to 140
        log_width = screen.get_width() - 100
        log_height = 120  # Reduced from 150 to 120
        
        # Log panel background
        log_color = (30, 30, 50)
        log_border = (80, 80, 100)
        pygame.draw.rect(screen, log_color, (log_x, log_y, log_width, log_height))
        pygame.draw.rect(screen, log_border, (log_x, log_y, log_width, log_height), 2)
        
        # Log title
        log_title = self.font.render("📜 BATTLE LOG", True, (255, 215, 100))
        screen.blit(log_title, (log_x + 10, log_y + 10))
        
        # Log messages - reduced to 4 lines to fit smaller space
        for i, message in enumerate(self.game_log[-4:]):  # Show last 4 messages
            log_text = self.small_font.render(message, True, (180, 180, 200))
            screen.blit(log_text, (log_x + 10, log_y + 35 + i * 18))
    
    def draw(self, screen: pygame.Surface):
        # Clear screen with gradient-like background
        screen.fill((20, 25, 40))  # Dark blue-grey
        
        # Add some texture with subtle rectangles
        for i in range(0, screen.get_width(), 100):
            for j in range(0, screen.get_height(), 100):
                if (i + j) % 200 == 0:
                    pygame.draw.rect(screen, (25, 30, 45), (i, j, 50, 50))
        
        # Draw board
        self.board.draw(screen)
        
        # Highlight selected piece
        if self.selected_piece:
            self.board.highlight_cell(screen, self.selected_row, self.selected_col, (255, 255, 0))
            
        # Highlight valid moves and attack targets based on current mode
        if self.action_mode == "move":
            self.board.highlight_moves(screen, self.valid_moves)  # Green for moves
        elif self.action_mode == "attack":
            # Red for attack targets
            for row, col in self.attack_targets:
                self.board.highlight_cell(screen, row, col, (255, 100, 100))
        
        # Draw pieces
        self.board.draw_pieces(screen)
        
        # Draw UI
        self.draw_ui(screen)
    
    def reset(self):
        self.__init__()