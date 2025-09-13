import pygame
from typing import Optional, List, Tuple, Dict
from board import Board
from piece import Piece, Color, PieceType
from game import GameState
import random
from enum import Enum

class GamePhase(Enum):
    SETUP = "setup"
    BATTLE = "battle"
    SHOP = "shop"
    END_ROUND = "end_round"

class TFTGame:
    def __init__(self):
        self.board = Board()
        self.current_player = Color.WHITE
        self.selected_piece = None
        self.selected_row = -1
        self.selected_col = -1
        self.valid_moves = []
        self.attack_targets = []
        self.game_state = GameState.PLAYING
        self.action_mode = "move"
        self.game_log = []
        
        # TFT-specific systems
        self.round_number = 1
        self.phase = GamePhase.SETUP
        self.white_coins = 3  # Starting coins
        self.black_coins = 3
        self.white_reserve = []  # Reserve pieces
        self.black_reserve = []
        self.shop_items = []  # Available pieces in shop
        self.shop_open = True  # Shop starts open
        self.battle_ended = False
        
        # Drag and drop state
        self.dragging_piece = None
        self.dragging_from_reserve = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # UI elements
        self.font = None
        self.title_font = None
        self.small_font = None
        self.load_assets()
        self.setup_initial_board()
        self.generate_shop()
        
        # UI layout - redesigned with larger spacing and no board blocking
        # Board is now at (250, 150) with size 720x720 (8*90)
        self.white_reserve_area = pygame.Rect(50, 150, 180, 600)   # Left side - wider with more space
        self.black_reserve_area = pygame.Rect(1000, 150, 180, 350)  # Right side top - wider  
        self.shop_area = pygame.Rect(1200, 150, 180, 400)           # Far right - wider
        
    def load_assets(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 28)        # Larger main font
        self.title_font = pygame.font.Font(None, 40)  # Larger title font
        self.small_font = pygame.font.Font(None, 22)  # Larger small font
        
        # Load piece sprites from Hackathon_image directory
        self.piece_sprites = {}
        piece_files = {
            PieceType.PAWN: "pawn.png",
            PieceType.KNIGHT: "knight.png", 
            PieceType.BISHOP: "king1.png",  # Using king1 as bishop
            PieceType.ROOK: "king2.png",    # Using king2 as rook
            PieceType.QUEEN: "queen.png",
            PieceType.KING: "king.png"
        }
        
        for piece_type, filename in piece_files.items():
            try:
                sprite_path = f"Hackathon_image/{filename}"
                sprite = pygame.image.load(sprite_path)
                self.piece_sprites[piece_type] = sprite
                print(f"Loaded sprite for {piece_type.value}")
            except Exception as e:
                print(f"Could not load sprite for {piece_type}: {e}")
                self.piece_sprites[piece_type] = None
                
    def setup_initial_board(self):
        # Clear board first
        self.board.grid = [[None for _ in range(8)] for _ in range(8)]
        
        # Setup initial pieces: 4 pawns + 1 king per side
        # White pieces (bottom)
        self.board.grid[7][2] = Piece(PieceType.KING, Color.WHITE, 7, 2)
        self.board.grid[6][1] = Piece(PieceType.PAWN, Color.WHITE, 6, 1)
        self.board.grid[6][2] = Piece(PieceType.PAWN, Color.WHITE, 6, 2)
        self.board.grid[6][3] = Piece(PieceType.PAWN, Color.WHITE, 6, 3)
        self.board.grid[6][4] = Piece(PieceType.PAWN, Color.WHITE, 6, 4)
        
        # Black pieces (top)
        self.board.grid[0][5] = Piece(PieceType.KING, Color.BLACK, 0, 5)
        self.board.grid[1][4] = Piece(PieceType.PAWN, Color.BLACK, 1, 4)
        self.board.grid[1][5] = Piece(PieceType.PAWN, Color.BLACK, 1, 5)
        self.board.grid[1][6] = Piece(PieceType.PAWN, Color.BLACK, 1, 6)
        self.board.grid[1][7] = Piece(PieceType.PAWN, Color.BLACK, 1, 7)
        
    def generate_shop(self):
        """Generate 5 random pieces for the shop"""
        piece_types = [PieceType.PAWN, PieceType.KNIGHT, PieceType.BISHOP, 
                      PieceType.ROOK, PieceType.QUEEN]
        weights = [40, 25, 20, 10, 5]  # Pawn most common, Queen rarest
        
        self.shop_items = []
        for _ in range(5):
            piece_type = random.choices(piece_types, weights=weights)[0]
            # Create a neutral piece for display
            piece = Piece(piece_type, Color.WHITE, 0, 0)  # Will be recolored when bought
            self.shop_items.append(piece)
            
    def get_piece_cost(self, piece_type: PieceType) -> int:
        """Get the cost of a piece type"""
        costs = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 99  # Can't buy kings
        }
        return costs.get(piece_type, 99)
        
    def can_afford(self, player: Color, piece_type: PieceType) -> bool:
        """Check if player can afford a piece"""
        cost = self.get_piece_cost(piece_type)
        coins = self.white_coins if player == Color.WHITE else self.black_coins
        return coins >= cost
        
    def buy_piece(self, player: Color, shop_index: int) -> bool:
        """Buy a piece from shop and add to reserve"""
        if not (0 <= shop_index < len(self.shop_items)):
            return False
            
        piece_template = self.shop_items[shop_index]
        cost = self.get_piece_cost(piece_template.piece_type)
        
        if not self.can_afford(player, piece_template.piece_type):
            return False
            
        # Deduct coins
        if player == Color.WHITE:
            self.white_coins -= cost
            # Create piece for white player
            new_piece = Piece(piece_template.piece_type, Color.WHITE, 0, 0)
            self.white_reserve.append(new_piece)
        else:
            self.black_coins -= cost
            # Create piece for black player  
            new_piece = Piece(piece_template.piece_type, Color.BLACK, 0, 0)
            self.black_reserve.append(new_piece)
            
        # Remove from shop and replace
        self.shop_items.pop(shop_index)
        
        # Add new item to shop
        piece_types = [PieceType.PAWN, PieceType.KNIGHT, PieceType.BISHOP, 
                      PieceType.ROOK, PieceType.QUEEN]
        weights = [40, 25, 20, 10, 5]
        new_type = random.choices(piece_types, weights=weights)[0]
        new_shop_piece = Piece(new_type, Color.WHITE, 0, 0)
        self.shop_items.insert(shop_index, new_shop_piece)
        
        self.add_to_log(f"{player.value.title()} bought {piece_template.piece_type.value.title()} for {cost} coins")
        return True
        
    def deploy_from_reserve(self, player: Color, reserve_index: int, board_row: int, board_col: int) -> bool:
        """Deploy piece from reserve to board"""
        if player == Color.WHITE:
            if not (0 <= reserve_index < len(self.white_reserve)):
                return False
            piece = self.white_reserve[reserve_index]
            # Check if position is in white's deployment zone (rows 5-7)
            if not (5 <= board_row <= 7):
                return False
        else:
            if not (0 <= reserve_index < len(self.black_reserve)):
                return False
            piece = self.black_reserve[reserve_index]
            # Check if position is in black's deployment zone (rows 0-2)
            if not (0 <= board_row <= 2):
                return False
                
        # Check if target position is empty
        if self.board.grid[board_row][board_col] is not None:
            return False
            
        # Deploy piece
        piece.row = board_row
        piece.col = board_col
        self.board.grid[board_row][board_col] = piece
        
        # Remove from reserve
        if player == Color.WHITE:
            self.white_reserve.remove(piece)
        else:
            self.black_reserve.remove(piece)
            
        self.add_to_log(f"{player.value.title()} deployed {piece.piece_type.value.title()}")
        return True
        
    def start_battle_phase(self):
        """Start the battle phase"""
        self.phase = GamePhase.BATTLE
        self.shop_open = False
        self.battle_ended = False
        self.current_player = Color.WHITE
        self.add_to_log(f"Round {self.round_number} Battle begins!")
        
    def end_battle_phase(self):
        """End battle and distribute rewards"""
        self.phase = GamePhase.END_ROUND
        self.battle_ended = True
        
        # Give base income
        self.white_coins += 1
        self.black_coins += 1
        
        self.add_to_log(f"Round {self.round_number} ended! +1 coin to both players")
        
    def start_next_round(self):
        """Start the next round"""
        self.round_number += 1
        
        # Shop opens every 3 rounds
        if self.round_number % 3 == 1:
            self.shop_open = True
            self.phase = GamePhase.SHOP
            self.generate_shop()  # Refresh shop
            self.add_to_log(f"Round {self.round_number}: Shop is open!")
        else:
            self.shop_open = False
            self.phase = GamePhase.SETUP
            self.add_to_log(f"Round {self.round_number}: Prepare for battle")
            
        self.battle_ended = False
        
    def handle_piece_death(self, dead_piece: Piece, killer_color: Color):
        """Handle when a piece dies, giving coins to killer"""
        reward = self.get_piece_cost(dead_piece.piece_type) // 2  # Half the piece cost
        if reward < 1:
            reward = 1
            
        if killer_color == Color.WHITE:
            self.white_coins += reward
            self.add_to_log(f"White gains {reward} coins for killing {dead_piece.piece_type.value.title()}")
        else:
            self.black_coins += reward
            self.add_to_log(f"Black gains {reward} coins for killing {dead_piece.piece_type.value.title()}")
            
    def add_to_log(self, message: str):
        """Add message to game log"""
        self.game_log.append(message)
        if len(self.game_log) > 8:
            self.game_log.pop(0)

    def handle_mouse_down(self, mouse_x: int, mouse_y: int):
        """Start dragging if click on reserve piece"""
        # Check white reserve
        reserve_index = self.handle_reserve_click(mouse_x, mouse_y, Color.WHITE)
        if reserve_index is not None:
            self.dragging_piece = self.white_reserve[reserve_index]
            self.dragging_from_reserve = True
            self.dragging_index = reserve_index
            self.drag_offset_x = mouse_x
            self.drag_offset_y = mouse_y
            return

        # Check black reserve
        reserve_index = self.handle_reserve_click(mouse_x, mouse_y, Color.BLACK)
        if reserve_index is not None:
            self.dragging_piece = self.black_reserve[reserve_index]
            self.dragging_from_reserve = True
            self.dragging_index = reserve_index
            self.drag_offset_x = mouse_x
            self.drag_offset_y = mouse_y
            return

    def handle_mouse_motion(self, mouse_x: int, mouse_y: int):
        """Update dragging piece position"""
        if self.dragging_piece:
            # Simply move the sprite with the mouse
            self.drag_offset_x = mouse_x
            self.drag_offset_y = mouse_y

    def handle_mouse_up(self, mouse_x: int, mouse_y: int):
        """Try to deploy piece or return to reserve"""
        if not self.dragging_piece:
            return

        # Try deploying to board
        row, col = self.board.get_cell_from_mouse(mouse_x, mouse_y)
        player = self.dragging_piece.color

        if self.try_deploy_to_position(player, self.dragging_index, row, col):
            self.add_to_log(f"{player.value.title()} deployed {self.dragging_piece.piece_type.value.title()} to {chr(ord('a')+col)}{8-row}")
        else:
            # Return to reserve
            self.add_to_log(f"Cannot deploy {self.dragging_piece.piece_type.value.title()} there. Returned to reserve.")

        # Clear dragging state
        self.dragging_piece = None
        self.dragging_from_reserve = False
        self.dragging_index = None
            
    # Add methods from original game for compatibility
    def handle_click(self, mouse_x: int, mouse_y: int):
        """Handle mouse clicks - extended for TFT features"""
        # Handle shop clicks
        if self.shop_open and self.shop_area.collidepoint(mouse_x, mouse_y):
            self.handle_shop_click(mouse_x, mouse_y)
            return
            
        # Handle reserve clicks
        if self.white_reserve_area.collidepoint(mouse_x, mouse_y):
            self.handle_reserve_click(mouse_x, mouse_y, Color.WHITE)
            return
        elif self.black_reserve_area.collidepoint(mouse_x, mouse_y):
            self.handle_reserve_click(mouse_x, mouse_y, Color.BLACK)
            return
            
        # Handle board clicks 
        # Check if click is in board area
        board_area = pygame.Rect(
            self.board.board_offset_x,
            self.board.board_offset_y,
            8 * self.board.cell_size,
            8 * self.board.cell_size
        )
        
        if board_area.collidepoint(mouse_x, mouse_y):
            self.handle_board_click(mouse_x, mouse_y)
            return
            
    def handle_shop_click(self, mouse_x: int, mouse_y: int):
        """Handle clicks on shop items"""
        if not self.shop_open:
            return
            
        # Calculate which shop item was clicked
        relative_x = mouse_x - self.shop_area.x
        relative_y = mouse_y - self.shop_area.y
        
        # Vertical layout with larger items
        if relative_y >= 40:  # Below title
            shop_index = (relative_y - 40) // 65  # Match new item height spacing
        else:
            shop_index = -1
                
        if 0 <= shop_index < len(self.shop_items):
            # Try to buy for current player
            self.buy_piece(self.current_player, shop_index)
                
    def handle_reserve_click(self, mouse_x: int, mouse_y: int, player: Color):
        """Handle clicks on reserve area for deployment"""
        if self.phase not in [GamePhase.SETUP, GamePhase.SHOP]:
            return
            
        reserve = self.white_reserve if player == Color.WHITE else self.black_reserve
        area = self.white_reserve_area if player == Color.WHITE else self.black_reserve_area
        
        # Calculate which piece was clicked
        relative_x = mouse_x - area.x
        relative_y = mouse_y - area.y
        
        if relative_y < 25:  # Clicked on title area
            return
            
        # Layout for reserves - matches drawing layout
        pieces_per_row = 3
        slot_width = 55
        slot_height = 60
        
        adjusted_y = relative_y - 30  # Match drawing offset
        if adjusted_y < 0:
            return
            
        col = (relative_x - 10) // slot_width  # Account for 10px left margin
        row = adjusted_y // slot_height
        
        if col >= pieces_per_row:
            return
            
        piece_index = row * pieces_per_row + col
        
        if 0 <= piece_index < len(reserve):
            piece = reserve[piece_index]
            self.add_to_log(f"Selected {piece.piece_type.value.title()} from reserve - drag to board to deploy!")
            return piece_index
        
        return None
        
    def handle_deployment_click(self, mouse_x: int, mouse_y: int):
        """Handle deployment of pieces from reserve to board during setup"""
        row, col = self.board.get_cell_from_mouse(mouse_x, mouse_y)
        
        if not self.board.is_valid_position(row, col):
            return
            
        # Check if position is empty
        if self.board.get_piece_at(row, col) is not None:
            self.add_to_log("Position is occupied!")
            return
            
        # Show deployment options for current player
        player = self.current_player
        reserve = self.white_reserve if player == Color.WHITE else self.black_reserve
        
        if not reserve:
            self.add_to_log(f"No pieces in {player.value.title()} reserve to deploy!")
            return
            
        # For simplicity, deploy the first piece in reserve (can be enhanced to show selection UI)
        if self.try_deploy_to_position(player, 0, row, col):
            self.add_to_log(f"{player.value.title()} deployed piece to {chr(ord('a')+col)}{8-row}")
        
    def try_deploy_to_position(self, player: Color, reserve_index: int, row: int, col: int) -> bool:
        """Try to deploy a piece from reserve to a specific board position"""
        reserve = self.white_reserve if player == Color.WHITE else self.black_reserve
        
        if not (0 <= reserve_index < len(reserve)):
            return False
            
        # Check deployment zones
        if player == Color.WHITE and not (5 <= row <= 7):
            self.add_to_log("White can only deploy in rows 6-8 (bottom 3 rows)")
            return False
        elif player == Color.BLACK and not (0 <= row <= 2):
            self.add_to_log("Black can only deploy in rows 1-3 (top 3 rows)")
            return False
            
        # Check if position is empty
        if self.board.get_piece_at(row, col) is not None:
            return False
            
        # Deploy the piece
        piece = reserve[reserve_index]
        piece.row = row
        piece.col = col
        self.board.grid[row][col] = piece
        reserve.remove(piece)
        
        return True
        
    def handle_board_click(self, mouse_x: int, mouse_y: int):
        """Handle clicks on the game board"""
        # During SETUP/SHOP: handle deployment
        if self.phase in [GamePhase.SETUP, GamePhase.SHOP]:
            self.handle_deployment_click(mouse_x, mouse_y)
            return
            
        # Only allow movement during BATTLE phase
        if self.phase != GamePhase.BATTLE:
            return
            
        row, col = self.board.get_cell_from_mouse(mouse_x, mouse_y)
        
        if not self.board.is_valid_position(row, col):
            return
            
        clicked_piece = self.board.get_piece_at(row, col)
        
        # If no piece is selected
        if self.selected_piece is None:
            # Only allow selecting pieces belonging to current player
            if clicked_piece and clicked_piece.is_alive() and clicked_piece.color == self.current_player:
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
            # If clicking on another piece of the current player
            elif clicked_piece and clicked_piece.is_alive() and clicked_piece.color == self.current_player:
                self.select_piece(clicked_piece, row, col)
            else:
                self.deselect_piece()
    
    def select_piece(self, piece: Piece, row: int, col: int):
        """Select a piece for movement/attack"""
        self.selected_piece = piece
        self.selected_row = row
        self.selected_col = col
        self.valid_moves = piece.get_valid_moves(self.board.grid)
        self.attack_targets = piece.get_attack_targets(self.board.grid)
        self.action_mode = "move"
        
    def deselect_piece(self):
        """Deselect current piece"""
        self.selected_piece = None
        self.selected_row = -1
        self.selected_col = -1
        self.valid_moves = []
        self.attack_targets = []
        self.action_mode = "move"
        
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """Move a piece"""
        moving_piece = self.board.get_piece_at(from_row, from_col)
        
        if not moving_piece or not moving_piece.is_alive():
            return
            
        # Move the piece (should only be to empty squares)
        target_piece = self.board.get_piece_at(to_row, to_col)
        if target_piece is None:  # Only move to empty squares
            self.board.move_piece(from_row, from_col, to_row, to_col)
            
        self.deselect_piece()
        self.switch_player()
        self.check_battle_end()
    
    def make_attack(self, attacker_row: int, attacker_col: int, target_row: int, target_col: int):
        """Attack an enemy piece"""
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
        
        # Remove dead pieces and give rewards
        if not target_piece.is_alive():
            self.board.grid[target_row][target_col] = None
            self.handle_piece_death(target_piece, attacking_piece.color)
            
        self.deselect_piece()
        self.switch_player()
        self.check_battle_end()
    
    def handle_combat(self, attacker: Piece, defender: Piece):
        """Handle combat between two pieces"""
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
        """Switch to the other player"""
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        turn_msg = f"{self.current_player.value.title()}'s turn"
        self.add_to_log(turn_msg)
    
    def check_battle_end(self):
        """Check if battle should end"""
        # Only check for battle end during battle phase
        if self.phase != GamePhase.BATTLE:
            return
            
        white_king_alive = self.board.is_king_alive(Color.WHITE)
        black_king_alive = self.board.is_king_alive(Color.BLACK)
        
        if not white_king_alive:
            self.add_to_log("BLACK WINS THE BATTLE! White King defeated!")
            self.black_coins += 3  # Bonus for winning
            self.end_battle_phase()
        elif not black_king_alive:
            self.add_to_log("WHITE WINS THE BATTLE! Black King defeated!")
            self.white_coins += 3  # Bonus for winning
            self.end_battle_phase()
    
    def toggle_action_mode(self):
        """Toggle between move and attack modes"""
        if self.selected_piece:
            self.action_mode = "attack" if self.action_mode == "move" else "move"
            mode_msg = f"Switched to {self.action_mode.upper()} mode"
            self.add_to_log(mode_msg)
        
    def draw(self, screen: pygame.Surface):
        """Draw the complete TFT game"""
        # Clear screen
        screen.fill((15, 20, 35))
        
        # Draw board without background image
        self.draw_simple_board(screen)
        
        # Draw highlights during battle and setup phases
        if self.phase in [GamePhase.BATTLE, GamePhase.SETUP] and self.selected_piece:
            self.board.highlight_cell(screen, self.selected_row, self.selected_col, (255, 255, 0))
            
            # Highlight valid moves and attack targets based on current mode
            if self.action_mode == "move":
                self.board.highlight_moves(screen, self.valid_moves)  # Green for moves
            elif self.action_mode == "attack":
                # Red for attack targets
                for row, col in self.attack_targets:
                    self.board.highlight_cell(screen, row, col, (255, 100, 100))
        
        # Draw pieces with custom rendering using loaded images
        self.draw_pieces_with_images(screen)

        # Draw dragging piece at mouse position if dragging from reserve
        if self.dragging_piece and self.dragging_from_reserve:
            sprite = self.piece_sprites.get(self.dragging_piece.piece_type)
            if sprite:
                piece_size = self.board.cell_size - 10
                scaled_sprite = pygame.transform.scale(sprite, (piece_size, piece_size))
                if self.dragging_piece.color == Color.BLACK:
                    tinted_sprite = scaled_sprite.copy()
                    dark_overlay = pygame.Surface((piece_size, piece_size))
                    dark_overlay.set_alpha(100)
                    dark_overlay.fill((100, 50, 50))
                    tinted_sprite.blit(dark_overlay, (0, 0))
                    scaled_sprite = tinted_sprite
                screen.blit(scaled_sprite, (self.drag_offset_x - piece_size // 2, self.drag_offset_y - piece_size // 2))
            else:
                symbol = self.get_piece_symbol(self.dragging_piece.piece_type)
                font = pygame.font.Font(None, 36)
                text_color = (255, 255, 255) if self.dragging_piece.color == Color.WHITE else (150, 50, 50)
                text = font.render(symbol, True, text_color)
                text_rect = text.get_rect(center=(self.drag_offset_x, self.drag_offset_y))
                screen.blit(text, text_rect)
        
        # Draw UI elements
        self.draw_tft_ui(screen)
        
    def draw_tft_ui(self, screen: pygame.Surface):
        """Draw TFT-specific UI elements"""
        # Draw title
        title_text = f"🏰 TFT Chess Battle - Round {self.round_number} 🏰"
        title_surface = self.title_font.render(title_text, True, (255, 215, 100))
        title_x = screen.get_width() // 2 - title_surface.get_width() // 2
        screen.blit(title_surface, (title_x, 10))
        
        # Draw phase and turn indicator
        phase_text = f"Phase: {self.phase.value.upper()}"
        phase_surface = self.font.render(phase_text, True, (200, 200, 255))
        screen.blit(phase_surface, (50, 40))
        
        # Draw current player turn
        turn_color = (255, 255, 100) if self.current_player == Color.WHITE else (255, 150, 150)
        turn_text = f"Turn: {self.current_player.value.upper()}"
        turn_surface = self.font.render(turn_text, True, turn_color)
        screen.blit(turn_surface, (200, 40))
        
        # Draw action mode if piece is selected
        if self.selected_piece:
            mode_color = (100, 255, 100) if self.action_mode == "move" else (255, 100, 100)
            mode_text = f"Mode: {self.action_mode.upper()}"
            mode_surface = self.font.render(mode_text, True, mode_color)
            screen.blit(mode_surface, (350, 40))
        
        # Draw detailed economic system UI
        self.draw_economy_panel(screen)
        
        # Draw reserve areas
        self.draw_reserve_area(screen, self.white_reserve_area, self.white_reserve, Color.WHITE)
        self.draw_reserve_area(screen, self.black_reserve_area, self.black_reserve, Color.BLACK)
        
        # Draw shop
        if self.shop_open:
            self.draw_shop(screen)
        else:
            self.draw_shop_closed(screen)
            
        # Draw battle log (smaller)
        self.draw_battle_log(screen)
        
    def draw_economy_panel(self, screen: pygame.Surface):
        """Draw detailed economic system information"""
        # Economy panel positioning - moved to fit new layout
        panel_x = 700
        panel_y = 50
        panel_width = 400
        panel_height = 120
        
        # Draw economy panel background
        economy_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (30, 40, 60), economy_rect)
        pygame.draw.rect(screen, (100, 120, 150), economy_rect, 2)
        
        # Title
        title_text = "💰 ECONOMY SYSTEM"
        title_surface = self.font.render(title_text, True, (255, 215, 100))
        screen.blit(title_surface, (panel_x + 10, panel_y + 5))
        
        # White player economics
        white_y = panel_y + 30
        white_coins_text = f"White: {self.white_coins} 🪙"
        white_reserve_text = f"Reserve: {len(self.white_reserve)}/8"
        white_army_value = sum(self.get_piece_cost(p.piece_type) for p in self.white_reserve)
        white_value_text = f"Army Value: {white_army_value} 🪙"
        
        white_coins_surface = self.small_font.render(white_coins_text, True, (255, 255, 255))
        white_reserve_surface = self.small_font.render(white_reserve_text, True, (200, 200, 200))
        white_value_surface = self.small_font.render(white_value_text, True, (180, 180, 180))
        
        screen.blit(white_coins_surface, (panel_x + 10, white_y))
        screen.blit(white_reserve_surface, (panel_x + 120, white_y))
        screen.blit(white_value_surface, (panel_x + 220, white_y))
        
        # Black player economics
        black_y = panel_y + 50
        black_coins_text = f"Black: {self.black_coins} 🪙"
        black_reserve_text = f"Reserve: {len(self.black_reserve)}/8"
        black_army_value = sum(self.get_piece_cost(p.piece_type) for p in self.black_reserve)
        black_value_text = f"Army Value: {black_army_value} 🪙"
        
        black_coins_surface = self.small_font.render(black_coins_text, True, (255, 150, 150))
        black_reserve_surface = self.small_font.render(black_reserve_text, True, (200, 150, 150))
        black_value_surface = self.small_font.render(black_value_text, True, (180, 150, 150))
        
        screen.blit(black_coins_surface, (panel_x + 10, black_y))
        screen.blit(black_reserve_surface, (panel_x + 120, black_y))
        screen.blit(black_value_surface, (panel_x + 220, black_y))
        
        # Economic info
        eco_y = panel_y + 75
        income_text = f"Round Income: +1 🪙 | Kill Reward: +½ cost | Win Bonus: +3 🪙"
        income_surface = self.small_font.render(income_text, True, (150, 200, 150))
        screen.blit(income_surface, (panel_x + 10, eco_y))
        
    def draw_reserve_area(self, screen: pygame.Surface, area: pygame.Rect, reserve: List[Piece], player: Color):
        """Draw reserve area for a player"""
        # Draw background
        color = (40, 60, 80) if player == Color.WHITE else (80, 40, 40)
        pygame.draw.rect(screen, color, area)
        pygame.draw.rect(screen, (150, 150, 150), area, 2)
        
        # Draw label
        label = f"{player.value.title()} Reserve ({len(reserve)}/8)"
        label_surface = self.small_font.render(label, True, (255, 255, 255))
        screen.blit(label_surface, (area.x + 5, area.y + 5))
        
        # Draw reserve pieces in improved layout
        pieces_per_row = 3  # 3 pieces per row for wider reserve areas
        
        for i, piece in enumerate(reserve[:8]):  # Max 8 in reserve
            col = i % pieces_per_row
            row = i // pieces_per_row
            x = area.x + 10 + col * 55
            y = area.y + 30 + row * 60
            slot_width, slot_height = 50, 55
            
            # Draw piece background
            piece_color = (200, 200, 220) if player == Color.WHITE else (220, 150, 150)
            pygame.draw.rect(screen, piece_color, (x, y, slot_width, slot_height))
            pygame.draw.rect(screen, (100, 100, 100), (x, y, slot_width, slot_height), 1)
            
            # Use actual piece image if available
            sprite = self.piece_sprites.get(piece.piece_type)
            if sprite:
                # Scale to fit reserve slot
                sprite_size = min(slot_width - 10, slot_height - 10)
                small_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                if piece.color == Color.BLACK:
                    # Apply dark tint for black pieces
                    tinted = small_sprite.copy()
                    overlay = pygame.Surface((sprite_size, sprite_size))
                    overlay.set_alpha(80)
                    overlay.fill((100, 50, 50))
                    tinted.blit(overlay, (0, 0))
                    small_sprite = tinted
                sprite_x = x + (slot_width - sprite_size) // 2
                sprite_y = y + (slot_height - sprite_size) // 2
                screen.blit(small_sprite, (sprite_x, sprite_y))
            else:
                # Fallback to symbol
                symbol = self.get_piece_symbol(piece.piece_type)
                symbol_surface = self.small_font.render(symbol, True, (50, 50, 50))
                symbol_x = x + slot_width // 2 - symbol_surface.get_width() // 2
                symbol_y = y + slot_height // 2 - symbol_surface.get_height() // 2
                screen.blit(symbol_surface, (symbol_x, symbol_y))
            
    def draw_shop(self, screen: pygame.Surface):
        """Draw the shop interface"""
        # Draw shop background
        pygame.draw.rect(screen, (50, 50, 70), self.shop_area)
        pygame.draw.rect(screen, (150, 150, 200), self.shop_area, 3)
        
        # Draw shop title
        shop_title = "🛒 SHOP (Click to Buy)"
        title_surface = self.font.render(shop_title, True, (255, 215, 100))
        screen.blit(title_surface, (self.shop_area.x + 10, self.shop_area.y + 10))
        
        # Draw shop items in vertical layout for wider shop area
        items_per_row = 1  # Keep vertical for better organization
        
        for i, piece in enumerate(self.shop_items):
            # Vertical layout with larger items
            x = self.shop_area.x + 10
            y = self.shop_area.y + 40 + i * 65
            item_width, item_height = self.shop_area.width - 20, 60
            
            # Draw item background
            cost = self.get_piece_cost(piece.piece_type)
            can_afford_white = self.white_coins >= cost
            can_afford_black = self.black_coins >= cost
            
            if can_afford_white or can_afford_black:
                bg_color = (100, 120, 100)  # Affordable
            else:
                bg_color = (120, 100, 100)  # Too expensive
                
            pygame.draw.rect(screen, bg_color, (x, y, item_width, item_height))
            pygame.draw.rect(screen, (200, 200, 200), (x, y, item_width, item_height), 2)
            
            # Draw piece image or symbol
            sprite = self.piece_sprites.get(piece.piece_type)
            if sprite:
                # Scale to fit shop slot - larger sprite
                sprite_size = min(item_height - 10, 45)
                shop_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                sprite_x = x + 10
                sprite_y = y + (item_height - sprite_size) // 2
                screen.blit(shop_sprite, (sprite_x, sprite_y))
                
                # Draw piece name and cost next to image
                name_text = piece.piece_type.value.title()
                name_surface = self.small_font.render(name_text, True, (255, 255, 255))
                screen.blit(name_surface, (x + sprite_size + 20, y + 10))
                
                cost_text = f"{cost}🪙"
                cost_surface = self.small_font.render(cost_text, True, (255, 255, 100))
                screen.blit(cost_surface, (x + sprite_size + 20, y + 35))
            else:
                # Fallback to symbol
                symbol = self.get_piece_symbol(piece.piece_type)
                symbol_surface = self.font.render(symbol, True, (255, 255, 255))
                symbol_x = x + item_width // 2 - symbol_surface.get_width() // 2
                symbol_y = y + item_height // 2 - symbol_surface.get_height() // 2
                screen.blit(symbol_surface, (symbol_x, symbol_y))
            
    def draw_shop_closed(self, screen: pygame.Surface):
        """Draw shop closed message"""
        pygame.draw.rect(screen, (40, 40, 50), self.shop_area)
        pygame.draw.rect(screen, (100, 100, 120), self.shop_area, 2)
        
        closed_text = "🔒 Shop Closed"
        next_open = 3 - (self.round_number % 3)
        if next_open == 3:
            next_open = 0
        
        info_text = f"Opens in {next_open} rounds"
        
        closed_surface = self.font.render(closed_text, True, (150, 150, 150))
        info_surface = self.small_font.render(info_text, True, (120, 120, 120))
        
        closed_x = self.shop_area.x + self.shop_area.width // 2 - closed_surface.get_width() // 2
        info_x = self.shop_area.x + self.shop_area.width // 2 - info_surface.get_width() // 2
        
        screen.blit(closed_surface, (closed_x, self.shop_area.y + 60))
        screen.blit(info_surface, (info_x, self.shop_area.y + 90))
        
    def draw_battle_log(self, screen: pygame.Surface):
        """Draw battle log at bottom of screen"""
        log_area = pygame.Rect(250, 880, 720, 100)  # Bottom of screen, aligned with board width
        pygame.draw.rect(screen, (25, 25, 40), log_area)
        pygame.draw.rect(screen, (80, 80, 100), log_area, 2)
        
        log_title = self.small_font.render("📜 Battle Log", True, (255, 215, 100))
        screen.blit(log_title, (log_area.x + 5, log_area.y + 5))
        
        for i, message in enumerate(self.game_log[-3:]):  # Show 3 messages to fit smaller area
            log_surface = self.small_font.render(message, True, (180, 180, 200))
            screen.blit(log_surface, (log_area.x + 5, log_area.y + 25 + i * 18))
            
    def get_piece_symbol(self, piece_type: PieceType) -> str:
        """Get symbol for piece type"""
        symbols = {
            PieceType.KING: '♔',
            PieceType.QUEEN: '♕', 
            PieceType.ROOK: '♖',
            PieceType.BISHOP: '♗',
            PieceType.KNIGHT: '♘',
            PieceType.PAWN: '♙'
        }
        return symbols.get(piece_type, '?')
    
    def draw_simple_board(self, screen: pygame.Surface):
        """Draw a simple chess board without background image"""
        # Draw alternating squares
        colors = [(240, 217, 181), (181, 136, 99)]  # Light and dark squares
        
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x = self.board.board_offset_x + col * self.board.cell_size
                y = self.board.board_offset_y + row * self.board.cell_size
                pygame.draw.rect(screen, color, (x, y, self.board.cell_size, self.board.cell_size))
        
        # Draw board border
        border_rect = pygame.Rect(
            self.board.board_offset_x - 5,
            self.board.board_offset_y - 5,
            8 * self.board.cell_size + 10,
            8 * self.board.cell_size + 10
        )
        pygame.draw.rect(screen, (100, 70, 40), border_rect, 5)
        
    def draw_pieces_with_images(self, screen: pygame.Surface):
        """Draw pieces using loaded images"""
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece is not None and piece.is_alive():
                    x = self.board.board_offset_x + col * self.board.cell_size
                    y = self.board.board_offset_y + row * self.board.cell_size
                    
                    # Get the sprite for this piece type
                    sprite = self.piece_sprites.get(piece.piece_type)
                    
                    if sprite:
                        # Scale sprite to fit cell
                        piece_size = self.board.cell_size - 10
                        scaled_sprite = pygame.transform.scale(sprite, (piece_size, piece_size))
                        
                        # Apply color tint for different players
                        if piece.color == Color.BLACK:
                            # Create a dark tinted version for black pieces
                            tinted_sprite = scaled_sprite.copy()
                            dark_overlay = pygame.Surface((piece_size, piece_size))
                            dark_overlay.set_alpha(100)
                            dark_overlay.fill((100, 50, 50))  # Dark red tint
                            tinted_sprite.blit(dark_overlay, (0, 0))
                            scaled_sprite = tinted_sprite
                        
                        # Draw the piece
                        screen.blit(scaled_sprite, (x + 5, y + 5))
                        
                        # Draw piece border to distinguish colors better
                        border_color = (255, 255, 255) if piece.color == Color.WHITE else (150, 50, 50)
                        pygame.draw.rect(screen, border_color, (x + 3, y + 3, piece_size + 4, piece_size + 4), 2)
                        
                    else:
                        # Fallback to text rendering if image not available
                        symbol = self.get_piece_symbol(piece.piece_type)
                        font = pygame.font.Font(None, 36)
                        text_color = (255, 255, 255) if piece.color == Color.WHITE else (150, 50, 50)
                        text = font.render(symbol, True, text_color)
                        text_rect = text.get_rect(center=(x + self.board.cell_size // 2, y + self.board.cell_size // 2))
                        screen.blit(text, text_rect)
                    
                    # Draw HP bar above piece if damaged
                    if piece.hp < piece.max_hp:
                        bar_width = self.board.cell_size - 20
                        bar_height = 6
                        bar_x = x + 10
                        bar_y = y - 10
                        
                        # Background bar (red)
                        pygame.draw.rect(screen, (200, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                        
                        # Health bar (green)
                        health_ratio = piece.hp / piece.max_hp
                        health_width = int(bar_width * health_ratio)
                        pygame.draw.rect(screen, (50, 200, 50), (bar_x, bar_y, health_width, bar_height))
                        
                        # Bar border
                        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
