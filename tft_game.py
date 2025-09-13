import pygame
from typing import Optional, List, Tuple, Dict
from board import Board
from piece import Piece, Color, PieceType
from game import GameState
import random
from enum import Enum
from card import Card, CardType

class GamePhase(Enum):
    SETUP = "setup"
    BATTLE = "battle"
    SHOP = "shop"
    END_ROUND = "end_round"

class TFTGame:
    def __init__(self, screen_width=1600, screen_height=1000):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Center board and UI based on screen size
        board_size = min(screen_width, screen_height) * 0.7
        cell_size = int(board_size // 8)
        board_offset_x = (screen_width - cell_size * 8) // 2
        board_offset_y = max(80, (screen_height - cell_size * 8) // 2)
        self.board = Board(cell_size=cell_size, board_offset_x=board_offset_x, board_offset_y=board_offset_y)
        self.current_player = Color.WHITE
        self.selected_piece = None
        self.selected_row = -1
        self.selected_col = -1
        self.valid_moves = []
        self.attack_targets = []
        self.game_state = GameState.PLAYING
        self.action_mode = "move"
        self.game_log = []
        self.end = False
        
        # TFT-specific systems
        self.round_number = 1
        self.phase = GamePhase.SETUP
        self.white_coins = 3  # Starting coins
        self.black_coins = 3
        self.white_reserve = []  # Reserve pieces
        self.black_reserve = []
        self.white_shop_items = []  # White's shop
        self.black_shop_items = []  # Black's shop
        self.shop_open = True  # Shop starts open
        self.battle_ended = False

        # Card inventory for each player
        self.white_card_inventory = []
        self.black_card_inventory = []

        # Drag and drop state
        self.dragging_piece = None
        self.dragging_from_reserve = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.actions_taken = {Color.WHITE: False, Color.BLACK: False}

        # Combat animation state
        self.combat_anim = None  # None or dict with attacker, defender, start_time, type

        # UI elements
        self.font = None
        self.title_font = None
        self.small_font = None
        self.card_icons = {}
        self.load_assets()
        self.setup_initial_board()
        self.generate_shop()
        
        # UI layout - adjusted to prevent overlap and screen size
        reserve_width = int(screen_width * 0.12)
        reserve_height = int(screen_height * 0.6)
        shop_width = int(screen_width * 0.12)
        shop_height = int(screen_height * 0.4)
        panel_width = int(screen_width * 0.25)
        panel_height = int(screen_height * 0.18)
        self.white_shop_area = pygame.Rect(20, board_offset_y, shop_width, shop_height)
        self.white_reserve_area = pygame.Rect(20, board_offset_y + shop_height + 20, reserve_width, reserve_height - shop_height)
        self.black_reserve_area = pygame.Rect(screen_width - reserve_width - 20, board_offset_y, reserve_width, reserve_height // 2)
        self.shop_area = pygame.Rect(screen_width - shop_width - 20, board_offset_y + reserve_height // 2 + 20, shop_width, shop_height)
        self.economy_panel_rect = pygame.Rect(screen_width - panel_width - 40, 40, panel_width, panel_height)
        
        
    def load_assets(self):
        pygame.font.init()
        # Load pixel font provided by user
        PIXEL_FONT_PATH = "Hackathon_image/pixel_font.ttf"  # Replace with actual filename
        self.font = pygame.font.Font(PIXEL_FONT_PATH, 28)
        self.title_font = pygame.font.Font(PIXEL_FONT_PATH, 40)
        self.small_font = pygame.font.Font(PIXEL_FONT_PATH, 22)

        # Retro color palette
        self.palette = {
            "bg": (10, 10, 20),
            "panel": (30, 30, 50),
            "border": (80, 255, 180),
            "neon_green": (80, 255, 80),
            "neon_cyan": (80, 255, 255),
            "neon_yellow": (255, 255, 80),
            "neon_red": (255, 80, 80),
            "white": (255, 255, 255),
            "gray": (120, 120, 120),
            "black": (0, 0, 0),
        }

        # Load piece sprites from Hackathon_image directory
        self.piece_sprites = {}
        piece_files = {
            PieceType.PAWN: "pawn.png",
            PieceType.KNIGHT: "knight.png", 
            PieceType.BISHOP: "bishop.png",
            PieceType.ROOK: "rook.png",
            PieceType.QUEEN: "queen4.png",
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

        # Load card icons (use placeholder if missing)
        card_icon_files = {
            CardType.ARROW_VOLLEY: "arrow_volley.png",
            CardType.DISARM: "disarm.png",
            CardType.REDEMPTION: "redemption.png"
        }
        for card_type, filename in card_icon_files.items():
            try:
                icon_path = f"Hackathon_image/{filename}"
                icon = pygame.image.load(icon_path)
                self.card_icons[card_type] = icon
            except Exception:
                # Placeholder: colored square
                surf = pygame.Surface((40, 40))
                surf.fill((200, 200, 100) if card_type == CardType.ARROW_VOLLEY else (180, 80, 80))
                self.card_icons[card_type] = surf
                
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
        """Generate 5 random items for each shop: pieces, cards, consumables"""
        piece_types = [PieceType.PAWN, PieceType.KNIGHT, PieceType.BISHOP, 
                      PieceType.ROOK, PieceType.QUEEN]
        weights = [40, 25, 20, 10, 5]  # Pawn most common, Queen rarest

        self.white_shop_items = []
        self.black_shop_items = []
        for _ in range(5):
            roll = random.random()
            if roll < 0.5:
                # Piece (50%)
                wt = random.choices(piece_types, weights=weights)[0]
                bt = random.choices(piece_types, weights=weights)[0]
                self.white_shop_items.append(Piece(wt, Color.WHITE, 0, 0))
                self.black_shop_items.append(Piece(bt, Color.BLACK, 0, 0))
            elif roll < 0.8:
                # Card (30%)
                arrow_card = Card(CardType.ARROW_VOLLEY, True, "Hackathon_image/arrow_volley.png", "Arrow Volley", 3)
                disarm_card = Card(CardType.DISARM, False, "Hackathon_image/disarm.png", "Disarm", 3)
                redemption_card = Card(CardType.REDEMPTION, True, "Hackathon_image/redemption.png", "Redemption", 3)
                # Randomly pick one card
                wc = random.choice([arrow_card, disarm_card, redemption_card])
                bc = random.choice([arrow_card, disarm_card, redemption_card])
                self.white_shop_items.append(wc)
                self.black_shop_items.append(bc)
            else:
                # Consumable (20%)
                # Placeholder: leave as is, or add your consumable logic here
                wt = random.choices(piece_types, weights=weights)[0]
                bt = random.choices(piece_types, weights=weights)[0]
                self.white_shop_items.append(Piece(wt, Color.WHITE, 0, 0))
                self.black_shop_items.append(Piece(bt, Color.BLACK, 0, 0))
            
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
        """Buy a piece or card from the correct shop and add to reserve/inventory"""
        shop_list = self.white_shop_items if player == Color.WHITE else self.black_shop_items
        if not (0 <= shop_index < len(shop_list)):
            return False

        item = shop_list[shop_index]
        # Handle Card purchase
        if isinstance(item, Card):
            cost = item.cost
            coins = self.white_coins if player == Color.WHITE else self.black_coins
            if coins < cost:
                return False
            # Deduct coins
            if player == Color.WHITE:
                self.white_coins -= cost
            else:
                self.black_coins -= cost
            # Immediate effect
            if item.immediate:
                if item.card_type == CardType.ARROW_VOLLEY:
                # Arrow Volley: use card's effect logic
                    item.apply_effect(self, player)
                elif item.card_type == CardType.REDEMPTION:
                    item.apply_effect(self, player)
            elif not item.immediate and item.card_type == CardType.DISARM:
                # Disarm: add to inventory
                if player == Color.WHITE:
                    self.white_card_inventory.append(item)
                else:
                    self.black_card_inventory.append(item)
                self.add_to_log(f"{player.value.title()} bought Disarm card (stored in inventory).")
            # Remove from shop
            shop_list.pop(shop_index)
            return True
        # Handle Piece purchase
        cost = self.get_piece_cost(item.piece_type)
        if not self.can_afford(player, item.piece_type):
            return False
        if player == Color.WHITE:
            self.white_coins -= cost
            new_piece = Piece(item.piece_type, Color.WHITE, 0, 0)
            self.white_reserve.append(new_piece)
        else:
            self.black_coins -= cost
            new_piece = Piece(item.piece_type, Color.BLACK, 0, 0)
            self.black_reserve.append(new_piece)
        shop_list.pop(shop_index)
        self.add_to_log(f"{player.value.title()} bought {item.piece_type.value.title()} for {cost} coins")
        return True
        
    def deploy_from_reserve(self, player: Color, reserve_index: int, board_row: int, board_col: int) -> bool:
        """Deploy piece from reserve to board"""
        if player == Color.WHITE:
            if not (0 <= reserve_index < len(self.white_reserve)):
                return False
            piece = self.white_reserve[reserve_index]
            if not (5 <= board_row <= 7):
                return False
        else:
            if not (0 <= reserve_index < len(self.black_reserve)):
                return False
            piece = self.black_reserve[reserve_index]
            if not (0 <= board_row <= 2):
                return False
                
        if self.board.grid[board_row][board_col] is not None:
            return False
            
        piece.row = board_row
        piece.col = board_col
        self.board.grid[board_row][board_col] = piece
        
        if player == Color.WHITE:
            self.white_reserve.remove(piece)
        else:
            self.black_reserve.remove(piece)
        
        # Play placement/click sound
        if self.snd_click:
            self.snd_click.play()
            
        self.add_to_log(f"{player.value.title()} deployed {piece.piece_type.value.title()}")
        return True
        
    def start_battle_phase(self):
        """Start the battle phase"""
        self.phase = GamePhase.BATTLE
        self.shop_open = False
        self.battle_ended = False
        self.current_player = Color.WHITE
        self.add_to_log(f"Round {self.round_number} Battle begins!")
        self.actions_taken = {Color.WHITE: False, Color.BLACK: False}

        
    def end_battle_phase(self):
        """End battle and distribute rewards"""
        self.phase = GamePhase.END_ROUND
        self.battle_ended = True
        
        # Give base income
        self.white_coins += 1
        self.black_coins += 1
        
        self.add_to_log(f"Round {self.round_number} ended! +1 coin to both players")
        if not self.end:
            self.start_next_round()

    def end_game(self):
        """End the game"""
        self.add_to_log("Click anywhere to reset the game")
        self.end = True

        
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
        player = self.dragging_piece.color
        # Try deploying to board
        row, col = self.board.get_cell_from_mouse(mouse_x, mouse_y)
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
        if self.shop_open and (self.shop_area.collidepoint(mouse_x, mouse_y) or self.white_shop_area.collidepoint(mouse_x, mouse_y)):
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
        """Handle clicks on shop items for both white and black shops"""
        if not self.shop_open:
            return

        shop_width = self.shop_area.width
        shop_height = self.shop_area.height
        white_shop_rect = self.white_shop_area
        black_shop_rect = self.shop_area

        # Check white shop
        if white_shop_rect.collidepoint(mouse_x, mouse_y):
            relative_x = mouse_x - white_shop_rect.x
            relative_y = mouse_y - white_shop_rect.y
            if relative_y >= 40:
                shop_index = (relative_y - 40) // 65
            else:
                shop_index = -1
            if 0 <= shop_index < len(self.white_shop_items):
                self.buy_piece(Color.WHITE, shop_index)
                return

        # Check black shop
        if black_shop_rect.collidepoint(mouse_x, mouse_y):
            relative_x = mouse_x - black_shop_rect.x
            relative_y = mouse_y - black_shop_rect.y
            if relative_y >= 40:
                shop_index = (relative_y - 40) // 65
            else:
                shop_index = -1
            if 0 <= shop_index < len(self.black_shop_items):
                self.buy_piece(Color.BLACK, shop_index)
                return
                
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
        if player == Color.WHITE and not (6 <= row <= 7):
            self.add_to_log("White can only deploy in rows 7-8 (bottom 2 rows)")
            return False
        elif player == Color.BLACK and not (0 <= row <= 1):
            self.add_to_log("Black can only deploy in rows 1-2 (top 2 rows)")
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
            
        self.actions_taken[self.current_player] = True
        if all(self.actions_taken.values()):
            self.end_battle_phase()
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

        # Start combat animation
        self.combat_anim = {
            "attacker": attacking_piece,
            "defender": target_piece,
            "start_time": pygame.time.get_ticks(),
            "type": f"{attacking_piece.piece_type.value}_vs_{target_piece.piece_type.value}",
            "attacker_pos": (attacker_row, attacker_col),
            "defender_pos": (target_row, target_col)
        }
        self.actions_taken[self.current_player] = True
        if all(self.actions_taken.values()):
            self.end_battle_phase()

        self.actions_taken[self.current_player] = True
        if all(self.actions_taken.values()):
            self.end_battle_phase()

        # Handle combat after animation (delayed)
        # The actual damage and removal will be handled after animation in draw()

    
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
            self.end_game()
        elif not black_king_alive:
            self.add_to_log("WHITE WINS THE BATTLE! Black King defeated!")
            self.white_coins += 3  # Bonus for winning
            self.end_battle_phase()
            self.end_game()
    
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

        # Draw hover window for piece info
        # (Removed duplicate rendering; now only drawn at the end of draw())

        # Combat animation rendering
        if self.combat_anim:
            self.draw_combat_animation(screen, self.combat_anim)
            # Animation duration: 600ms
            elapsed = pygame.time.get_ticks() - self.combat_anim["start_time"]
            if elapsed > 600:
                # After animation, apply combat logic and cleanup
                attacker = self.combat_anim["attacker"]
                defender = self.combat_anim["defender"]
                self.handle_combat(attacker, defender)
                # Remove dead pieces and give rewards
                if not defender.is_alive():
                    row, col = self.combat_anim["defender_pos"]
                    self.board.grid[row][col] = None
                    self.handle_piece_death(defender, attacker.color)
                self.deselect_piece()
                self.switch_player()
                self.check_battle_end()
                self.combat_anim = None

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
        
        # Draw battle mode feedback
        if self.phase == GamePhase.BATTLE:
            banner_rect = pygame.Rect(0, 0, self.screen_width, 38)
            pygame.draw.rect(screen, (255, 80, 80), banner_rect)
            banner_text = self.title_font.render("⚔️ BATTLE MODE ⚔️", True, (255, 255, 255))
            screen.blit(banner_text, (self.screen_width // 2 - banner_text.get_width() // 2, 4))

        # --- Draw hover window for piece info (always on top) ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Board hover
        hovered_piece = None
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece and piece.is_alive():
                    px = self.board.board_offset_x + col * self.board.cell_size
                    py = self.board.board_offset_y + row * self.board.cell_size
                    rect = pygame.Rect(px, py, self.board.cell_size, self.board.cell_size)
                    if rect.collidepoint(mouse_x, mouse_y):
                        hovered_piece = piece
                        break
            if hovered_piece:
                break
        # Shop hover
        hovered_shop_piece = None
        if self.shop_open:
            shop_width = self.shop_area.width
            shop_height = self.shop_area.height
            white_shop_rect = pygame.Rect(self.shop_area.x - shop_width - 30, self.shop_area.y, shop_width, shop_height)
            black_shop_rect = pygame.Rect(self.shop_area.x, self.shop_area.y, shop_width, shop_height)
            # White shop hover
            for i in range(len(self.white_shop_items)):
                x = white_shop_rect.x + 12
                y = white_shop_rect.y + 48 + i * 65
                item_width, item_height = shop_width - 24, 56
                rect = pygame.Rect(x, y, item_width, item_height)
                if rect.collidepoint(mouse_x, mouse_y):
                    hovered_shop_piece = self.white_shop_items[i]
                    break
            # Black shop hover (takes priority if both overlap)
            for i in range(len(self.black_shop_items)):
                x = black_shop_rect.x + 12
                y = black_shop_rect.y + 48 + i * 65
                item_width, item_height = shop_width - 24, 56
                rect = pygame.Rect(x, y, item_width, item_height)
                if rect.collidepoint(mouse_x, mouse_y):
                    hovered_shop_piece = self.black_shop_items[i]
                    break
        # Draw hover window (shop takes priority)
        info_width, info_height = 180, 110
        info_x = min(max(mouse_x + 20, 10), self.screen_width - info_width - 10)
        info_y = min(max(mouse_y + 20, 10), self.screen_height - info_height - 10)
        if hovered_shop_piece:
            item = hovered_shop_piece
            info_rect = pygame.Rect(info_x, info_y, info_width, info_height)
            pygame.draw.rect(screen, (30, 30, 50), info_rect)
            pygame.draw.rect(screen, (100, 255, 180), info_rect, 2)
            font = pygame.font.Font("Hackathon_image/pixel_font.ttf", 22)
            if isinstance(item, Card):
                title = item.name
                cost = f"Cost: {item.cost}"
                card_type = "Immediate" if item.immediate else "Stored"
                effectDict = {CardType.ARROW_VOLLEY: "Arrow Volley: -1 HP all units", 
                              CardType.DISARM: "Disarm: Set attack=0", 
                              CardType.REDEMPTION: "Redemption: black tiles take 1 dmg; white tiles gain 1 health"}
                effect = effectDict[item.card_type]
                lines = [title, cost, f"Type: {card_type}", effect, "Shop Card"]
            else:
                title = f"{item.piece_type.value.title()[:12]}"
                hp = f"HP: {item.hp}/{item.max_hp}"
                atk = f"ATK: {item.attack}"
                cost = f"Cost: {item.cost}"
                pos = "Shop Item"
                lines = [title, hp, atk, cost, pos]
            for i, line in enumerate(lines):
                text = font.render(line[:22], True, (255, 255, 255))
                screen.blit(text, (info_x + 12, info_y + 12 + i * 20))
        elif hovered_piece:
            piece = hovered_piece
            info_rect = pygame.Rect(info_x, info_y, info_width, info_height)
            pygame.draw.rect(screen, (30, 30, 50), info_rect)
            pygame.draw.rect(screen, (100, 255, 180), info_rect, 2)
            font = pygame.font.Font("Hackathon_image/pixel_font.ttf", 22)
            title = f"{piece.color.value.title()} {piece.piece_type.value.title()}"
            hp = f"HP: {piece.hp}/{piece.max_hp}"
            atk = f"ATK: {piece.attack}"
            cost = f"Cost: {piece.cost}"
            pos = f"Pos: {chr(ord('a')+piece.col)}{8-piece.row}"
            lines = [title, hp, atk, cost, pos]
            for i, line in enumerate(lines):
                text = font.render(line[:22], True, (255, 255, 255))
                screen.blit(text, (info_x + 12, info_y + 12 + i * 20))
        
    def draw_tft_ui(self, screen: pygame.Surface):
        """Draw TFT-specific UI elements"""
        # Draw title
        title_text = f"🏰 TFT Chess Battle - Round {self.round_number} 🏰"
        title_surface = self.title_font.render(title_text, True, (255, 215, 100))
        title_x = screen.get_width() // 2 - title_surface.get_width() // 2 - 200
        screen.blit(title_surface, (title_x, 10))
        
        # Draw phase and turn indicator
        phase_text = f"Phase: {self.phase.value.upper()}"
        phase_surface = self.font.render(phase_text, True, (200, 200, 255))
        screen.blit(phase_surface, (50, 40))
        
        # Draw current player turn
        turn_color = (255, 255, 100) if self.current_player == Color.WHITE else (255, 150, 150)
        turn_text = f"Turn: {self.current_player.value.upper()}"
        turn_surface = self.font.render(turn_text, True, turn_color)
        screen.blit(turn_surface, (50, 80))
        
        # Draw action mode if piece is selected
        if self.selected_piece:
            mode_color = (100, 255, 100) if self.action_mode == "move" else (255, 100, 100)
            mode_text = f"Mode: {self.action_mode.upper()}"
            mode_surface = self.font.render(mode_text, True, mode_color)
            screen.blit(mode_surface, (350, 60))
        
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
        # Economy panel positioning - dynamic
        panel_width = int(self.screen_width * 0.25)
        panel_height = int(self.screen_height * 0.13)
        panel_x = self.screen_width - panel_width - 40
        panel_y = 20
        
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
        screen.blit(white_value_surface, (panel_x + 280, white_y))
        
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
        screen.blit(black_value_surface, (panel_x + 280, black_y))
        
        # Economic info
        eco_y = panel_y + 75
        income_text = f"Round Income: +1 🪙 | Kill Reward: +½ cost"
        income_surface = self.small_font.render(income_text, True, (150, 200, 150))
        screen.blit(income_surface, (panel_x + 10, eco_y))
        
    def draw_reserve_area(self, screen: pygame.Surface, area: pygame.Rect, reserve: List[Piece], player: Color):
        """Draw reserve area in retro pixel-art style"""
        # Draw background panel with pixel border
        pygame.draw.rect(screen, self.palette["panel"], area)
        pygame.draw.rect(screen, self.palette["border"], area, 4)
        pixel_size = 10
        pygame.draw.rect(screen, self.palette["border"], (area.x, area.y, pixel_size, pixel_size))
        pygame.draw.rect(screen, self.palette["border"], (area.x + area.width - pixel_size, area.y, pixel_size, pixel_size))
        pygame.draw.rect(screen, self.palette["border"], (area.x, area.y + area.height - pixel_size, pixel_size, pixel_size))
        pygame.draw.rect(screen, self.palette["border"], (area.x + area.width - pixel_size, area.y + area.height - pixel_size, pixel_size, pixel_size))

        # Draw label in pixel font
        label = f"{player.value.upper()} RESERVE"
        label_surface = self.font.render(label, True, self.palette["neon_cyan"])
        screen.blit(label_surface, (area.x + 8, area.y + 8))

        # Draw reserve slots as pixel frames
        pieces_per_row = 3
        max_slots = 8
        slot_width, slot_height = 50, 55
        time_ms = pygame.time.get_ticks()
        flicker = (time_ms // 200) % 2 == 0

        for i in range(max_slots):
            col = i % pieces_per_row
            row = i // pieces_per_row
            x = area.x + 12 + col * 55
            y = area.y + 32 + row * 60

            # Draw pixel frame for slot
            pygame.draw.rect(screen, self.palette["bg"], (x, y, slot_width, slot_height))
            pygame.draw.rect(screen, self.palette["border"], (x, y, slot_width, slot_height), 3)
            # Pixel corners
            pygame.draw.rect(screen, self.palette["border"], (x, y, 7, 7))
            pygame.draw.rect(screen, self.palette["border"], (x + slot_width - 7, y, 7, 7))
            pygame.draw.rect(screen, self.palette["border"], (x, y + slot_height - 7, 7, 7))
            pygame.draw.rect(screen, self.palette["border"], (x + slot_width - 7, y + slot_height - 7, 7, 7))

            if i < len(reserve):
                piece = reserve[i]
                # Piece sprite
                sprite = self.piece_sprites.get(piece.piece_type)
                if sprite:
                    sprite_size = min(slot_width - 12, slot_height - 12)
                    small_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                    if piece.color == Color.BLACK:
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
                    symbol = self.get_piece_symbol(piece.piece_type)
                    symbol_surface = self.font.render(symbol, True, self.palette["white"])
                    symbol_x = x + slot_width // 2 - symbol_surface.get_width() // 2
                    symbol_y = y + slot_height // 2 - symbol_surface.get_height() // 2
                    screen.blit(symbol_surface, (symbol_x, symbol_y))
                # Tiny pixel HP bar below sprite
                hp_bar_y = y + slot_height - 12
                hp_bar_x = x + 8
                hp_bar_w = slot_width - 16
                hp_ratio = piece.hp / piece.max_hp if piece.max_hp > 0 else 0
                hp_fill = int(hp_bar_w * hp_ratio)
                pygame.draw.rect(screen, self.palette["neon_red"], (hp_bar_x, hp_bar_y, hp_bar_w, 6))
                pygame.draw.rect(screen, self.palette["neon_green"], (hp_bar_x, hp_bar_y, hp_fill, 6))
                pygame.draw.rect(screen, self.palette["white"], (hp_bar_x, hp_bar_y, hp_bar_w, 6), 1)
            else:
                # Empty slot: flickering "EMPTY" in pixel font (smaller)
                if flicker:
                    placeholder = "EMPTY"
                    small_font = pygame.font.Font("Hackathon_image/pixel_font.ttf", 12)
                    placeholder_surface = small_font.render(placeholder, True, self.palette["neon_yellow"])
                    px = x + slot_width // 2 - placeholder_surface.get_width() // 2
                    py = y + slot_height // 2 - placeholder_surface.get_height() // 2
                    screen.blit(placeholder_surface, (px, py))
    def draw_shop(self, screen: pygame.Surface):
        """Draw white shop at far left and black shop at right"""
        shop_width = self.shop_area.width
        shop_height = self.shop_area.height
        white_shop_rect = self.white_shop_area
        black_shop_rect = self.shop_area

        # Draw white shop
        pygame.draw.rect(screen, self.palette["panel"], white_shop_rect)
        pygame.draw.rect(screen, self.palette["border"], white_shop_rect, 4)
        shop_title = "WHITE SHOP"
        title_surface = self.title_font.render(shop_title, True, self.palette["neon_yellow"])
        screen.blit(title_surface, (white_shop_rect.x + 18, white_shop_rect.y + 8))
        for i, item in enumerate(self.white_shop_items):
            x = white_shop_rect.x + 12
            y = white_shop_rect.y + 48 + i * 65
            item_width, item_height = shop_width - 24, 56
            pygame.draw.rect(screen, self.palette["bg"], (x, y, item_width, item_height))
            pygame.draw.rect(screen, self.palette["border"], (x, y, item_width, item_height), 3)
            if isinstance(item, Card):
                # Card UI
                icon = self.card_icons.get(item.card_type)
                if icon:
                    icon_size = min(item_height - 12, 32)
                    card_icon = pygame.transform.scale(icon, (icon_size, icon_size))
                    screen.blit(card_icon, (x + 12, y + (item_height - icon_size) // 2))
                name_surface = self.font.render(item.name, True, self.palette["neon_cyan"])
                screen.blit(name_surface, (x + 60, y + 8))
                cost_text = f"{item.cost}"
                cost_surface = self.font.render(cost_text, True, self.palette["neon_yellow"])
                screen.blit(cost_surface, (x + 60, y + 28))
                # Coin icon
                try:
                    coin_img = pygame.image.load("Hackathon_image/coin.png")
                    coin_img = pygame.transform.scale(coin_img, (18, 18))
                    screen.blit(coin_img, (x + 90, y + 28))
                except Exception:
                    pass
                # Immediate card icon
                if item.immediate:
                    flash_surface = self.font.render("⚡", True, (255, 255, 80))
                    screen.blit(flash_surface, (x + item_width - 32, y + 8))
                can_afford = self.white_coins >= item.cost
            else:
                # Piece/consumable UI
                sprite = self.piece_sprites.get(item.piece_type)
                if sprite:
                    sprite_size = min(item_height - 12, 32)
                    shop_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                    sprite_x = x + 12
                    sprite_y = y + (item_height - sprite_size) // 2
                    screen.blit(shop_sprite, (sprite_x, sprite_y))
                else:
                    symbol = self.get_piece_symbol(item.piece_type)
                    symbol_surface = self.font.render(symbol, True, self.palette["white"])
                    sprite_x = x + 12
                    sprite_y = y + (item_height - 32) // 2
                    screen.blit(symbol_surface, (sprite_x, sprite_y))
                name_text = item.piece_type.value.upper()
                name_surface = self.font.render(name_text, True, self.palette["neon_cyan"])
                screen.blit(name_surface, (x + 60, y + 8))
                cost = self.get_piece_cost(item.piece_type)
                cost_text = f"{cost}"
                cost_surface = self.font.render(cost_text, True, self.palette["neon_yellow"])
                screen.blit(cost_surface, (x + 60, y + 28))
                try:
                    coin_img = pygame.image.load("Hackathon_image/coin.png")
                    coin_img = pygame.transform.scale(coin_img, (18, 18))
                    screen.blit(coin_img, (x + 90, y + 28))
                except Exception:
                    pass
                can_afford = self.white_coins >= cost
            if not can_afford:
                try:
                    red_overlay = pygame.image.load("Hackathon_image/red_overlay.png")
                    red_overlay = pygame.transform.scale(red_overlay, (item_width, item_height))
                    screen.blit(red_overlay, (x, y))
                except Exception:
                    overlay = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
                    overlay.fill((255, 0, 0, 120))
                    screen.blit(overlay, (x, y))

        # Draw black shop
        pygame.draw.rect(screen, self.palette["panel"], black_shop_rect)
        pygame.draw.rect(screen, self.palette["border"], black_shop_rect, 4)
        shop_title = "BLACK SHOP"
        title_surface = self.title_font.render(shop_title, True, self.palette["neon_yellow"])
        screen.blit(title_surface, (black_shop_rect.x + 18, black_shop_rect.y + 8))
        for i, item in enumerate(self.black_shop_items):
            x = black_shop_rect.x + 12
            y = black_shop_rect.y + 48 + i * 65
            item_width, item_height = shop_width - 24, 56
            pygame.draw.rect(screen, self.palette["bg"], (x, y, item_width, item_height))
            pygame.draw.rect(screen, self.palette["border"], (x, y, item_width, item_height), 3)
            if isinstance(item, Card):
                # Card UI
                icon = self.card_icons.get(item.card_type)
                if icon:
                    icon_size = min(item_height - 12, 32)
                    card_icon = pygame.transform.scale(icon, (icon_size, icon_size))
                    screen.blit(card_icon, (x + 12, y + (item_height - icon_size) // 2))
                name_surface = self.font.render(item.name, True, self.palette["neon_cyan"])
                screen.blit(name_surface, (x + 60, y + 8))
                cost_text = f"{item.cost}"
                cost_surface = self.font.render(cost_text, True, self.palette["neon_yellow"])
                screen.blit(cost_surface, (x + 60, y + 28))
                # Coin icon
                try:
                    coin_img = pygame.image.load("Hackathon_image/coin.png")
                    coin_img = pygame.transform.scale(coin_img, (18, 18))
                    screen.blit(coin_img, (x + 90, y + 28))
                except Exception:
                    pass
                # Immediate card icon
                if item.immediate:
                    flash_surface = self.font.render("⚡", True, (255, 255, 80))
                    screen.blit(flash_surface, (x + item_width - 32, y + 8))
                can_afford = self.black_coins >= item.cost
            else:
                # Piece/consumable UI
                sprite = self.piece_sprites.get(item.piece_type)
                if sprite:
                    sprite_size = min(item_height - 12, 32)
                    shop_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                    sprite_x = x + 12
                    sprite_y = y + (item_height - sprite_size) // 2
                    screen.blit(shop_sprite, (sprite_x, sprite_y))
                else:
                    symbol = self.get_piece_symbol(item.piece_type)
                    symbol_surface = self.font.render(symbol, True, self.palette["white"])
                    sprite_x = x + 12
                    sprite_y = y + (item_height - 32) // 2
                    screen.blit(symbol_surface, (sprite_x, sprite_y))
                name_text = item.piece_type.value.upper()
                name_surface = self.font.render(name_text, True, self.palette["neon_cyan"])
                screen.blit(name_surface, (x + 60, y + 8))
                cost = self.get_piece_cost(item.piece_type)
                cost_text = f"{cost}"
                cost_surface = self.font.render(cost_text, True, self.palette["neon_yellow"])
                screen.blit(cost_surface, (x + 60, y + 28))
                try:
                    coin_img = pygame.image.load("Hackathon_image/coin.png")
                    coin_img = pygame.transform.scale(coin_img, (18, 18))
                    screen.blit(coin_img, (x + 90, y + 28))
                except Exception:
                    pass
                can_afford = self.black_coins >= cost
            if not can_afford:
                try:
                    red_overlay = pygame.image.load("Hackathon_image/red_overlay.png")
                    red_overlay = pygame.transform.scale(red_overlay, (item_width, item_height))
                    screen.blit(red_overlay, (x, y))
                except Exception:
                    overlay = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
                    overlay.fill((255, 0, 0, 120))
                    screen.blit(overlay, (x, y))
            
    def draw_shop_closed(self, screen: pygame.Surface):
        """Draw shop closed message for both shops"""
        # Black shop
        pygame.draw.rect(screen, (40, 40, 50), self.shop_area)
        pygame.draw.rect(screen, (100, 100, 120), self.shop_area, 2)
        closed_text = "🔒 Shop Closed"
        next_open = 3 - (self.round_number % 3)
        if next_open == 3:
            next_open = 0
        info_text = f"Opens in {next_open} rounds"
        closed_surface = self.font.render(closed_text, True, (150, 150, 150))
        info_surface = self.small_font.render(info_text, True, (120, 120, 120))
        # Black shop
        closed_x = self.shop_area.x + self.shop_area.width // 2 - closed_surface.get_width() // 2
        info_x = self.shop_area.x + self.shop_area.width // 2 - info_surface.get_width() // 2
        closed_y = self.shop_area.y + int(self.shop_area.height * 0.35)
        info_y = self.shop_area.y + int(self.shop_area.height * 0.55)
        screen.blit(closed_surface, (closed_x, closed_y))
        screen.blit(info_surface, (info_x, info_y))
        # White shop
        pygame.draw.rect(screen, (40, 40, 50), self.white_shop_area)
        pygame.draw.rect(screen, (100, 100, 120), self.white_shop_area, 2)
        closed_x_w = self.white_shop_area.x + self.white_shop_area.width // 2 - closed_surface.get_width() // 2
        info_x_w = self.white_shop_area.x + self.white_shop_area.width // 2 - info_surface.get_width() // 2
        closed_y_w = self.white_shop_area.y + int(self.white_shop_area.height * 0.35)
        info_y_w = self.white_shop_area.y + int(self.white_shop_area.height * 0.55)
        screen.blit(closed_surface, (closed_x_w, closed_y_w))
        screen.blit(info_surface, (info_x_w, info_y_w))
        
    def draw_battle_log(self, screen: pygame.Surface):
        """Draw battle log in retro terminal style with typewriter effect and color coding"""
        log_width = int(self.screen_width * 0.45)
        log_height = 100
        log_x = (self.screen_width - log_width) // 2
        log_y = self.screen_height - log_height - 20
        log_area = pygame.Rect(log_x, log_y, log_width, log_height)
        pygame.draw.rect(screen, self.palette["black"], log_area)
        pygame.draw.rect(screen, self.palette["neon_green"], log_area, 3)
        pixel_size = 8
        pygame.draw.rect(screen, self.palette["neon_green"], (log_area.x, log_area.y, pixel_size, pixel_size))
        pygame.draw.rect(screen, self.palette["neon_green"], (log_area.x + log_area.width - pixel_size, log_area.y, pixel_size, pixel_size))
        pygame.draw.rect(screen, self.palette["neon_green"], (log_area.x, log_area.y + log_area.height - pixel_size, pixel_size, pixel_size))
        pygame.draw.rect(screen, self.palette["neon_green"], (log_area.x + log_area.width - pixel_size, log_area.y + log_area.height - pixel_size, pixel_size, pixel_size))

        log_title = self.font.render("BATTLE LOG", True, self.palette["neon_green"])
        screen.blit(log_title, (log_area.x + 8, log_area.y + 8))

        # Typewriter effect for last message
        messages = self.game_log[-3:]
        typewriter_speed = 30  # ms per character
        time_ms = pygame.time.get_ticks()
        for i, message in enumerate(messages):
            # Color code: red for damage, green for heals, yellow for gold
            if "damage" in message or "attack" in message:
                color = self.palette["neon_red"]
            elif "heal" in message or "HP" in message:
                color = self.palette["neon_green"]
            elif "coin" in message or "gold" in message:
                color = self.palette["neon_yellow"]
            else:
                color = self.palette["neon_green"]
            # Typewriter effect for last message
            if i == len(messages) - 1:
                chars = min(len(message), (time_ms // typewriter_speed) % (len(message) + 1))
                display_msg = message[:chars]
            else:
                display_msg = message
            log_surface = self.font.render(display_msg, True, color)
            screen.blit(log_surface, (log_area.x + 12, log_area.y + 32 + i * 22))
            
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
        import math
        time_ms = pygame.time.get_ticks()

        # Retro jump animation for selected piece (frame-step, not smooth)
        def retro_jump_offset(frame, total_frames=3, jump_height=18):
            # Returns y offset for jump animation (3 frames: up, peak, down)
            if frame == 0:
                return -jump_height
            elif frame == 1:
                return -jump_height // 2
            else:
                return 0

        # If combat animation is active, skip drawing attacker/defender pieces here
        anim_attacker = None
        anim_defender = None
        if self.combat_anim:
            anim_attacker = self.combat_anim["attacker"]
            anim_defender = self.combat_anim["defender"]

        # Determine jump frame for selected piece
        selected_jump_frame = ((time_ms // 160) % 3)  # 3-frame cycle, 160ms per frame (slower float)

        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece is not None and piece.is_alive():
                    # Skip attacker/defender during animation
                    if piece is anim_attacker or piece is anim_defender:
                        continue

                    x = self.board.board_offset_x + col * self.board.cell_size
                    y = self.board.board_offset_y + row * self.board.cell_size

                    # Snap piece to grid, apply retro jump if selected
                    is_selected = (
                        self.selected_piece is piece
                        and self.selected_row == row
                        and self.selected_col == col
                    )
                    y_anim = y + retro_jump_offset(selected_jump_frame) if is_selected else y

                    # Get the sprite for this piece type
                    sprite = self.piece_sprites.get(piece.piece_type)

                    if sprite:
                        # Nearest-neighbor scaling for pixel art
                        piece_size = self.board.cell_size - 10
                        scaled_sprite = pygame.transform.scale(sprite, (piece_size, piece_size))
                        # Apply color tint for different players
                        if piece.color == Color.BLACK:
                            tinted_sprite = scaled_sprite.copy()
                            dark_overlay = pygame.Surface((piece_size, piece_size))
                            dark_overlay.set_alpha(100)
                            dark_overlay.fill((100, 50, 50))
                            tinted_sprite.blit(dark_overlay, (0, 0))
                            scaled_sprite = tinted_sprite
                        screen.blit(scaled_sprite, (x + 5, y_anim + 5))
                        # Draw piece border to distinguish colors better
                        border_color = (255, 255, 255) if piece.color == Color.WHITE else (150, 50, 50)
                        pygame.draw.rect(screen, border_color, (x + 3, y_anim + 3, piece_size + 4, piece_size + 4), 2)
                    else:
                        # Fallback to text rendering if image not available
                        symbol = self.get_piece_symbol(piece.piece_type)
                        font = pygame.font.Font(None, 36)
                        text_color = (255, 255, 255) if piece.color == Color.WHITE else (150, 50, 50)
                        text = font.render(symbol, True, text_color)
                        text_rect = text.get_rect(center=(x + self.board.cell_size // 2, y_anim + self.board.cell_size // 2))
                        screen.blit(text, text_rect)

                    # Draw HP bar above piece if damaged
                    if piece.hp < piece.max_hp:
                        bar_width = self.board.cell_size - 20
                        bar_height = 6
                        bar_x = x + 10
                        bar_y = y_anim - 10
                        pygame.draw.rect(screen, (200, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                        health_ratio = piece.hp / piece.max_hp
                        health_width = int(bar_width * health_ratio)
                        pygame.draw.rect(screen, (50, 200, 50), (bar_x, bar_y, health_width, bar_height))
                        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def draw_combat_animation(self, screen: pygame.Surface, anim: dict):
        """Draw modular combat animation for attacker and defender"""
        import math
        attacker = anim["attacker"]
        defender = anim["defender"]
        attacker_row, attacker_col = anim["attacker_pos"]
        defender_row, defender_col = anim["defender_pos"]
        elapsed = pygame.time.get_ticks() - anim["start_time"]
        duration = 600

        # Get positions
        ax = self.board.board_offset_x + attacker_col * self.board.cell_size
        ay = self.board.board_offset_y + attacker_row * self.board.cell_size
        dx = self.board.board_offset_x + defender_col * self.board.cell_size
        dy = self.board.board_offset_y + defender_row * self.board.cell_size

        # Animation: attacker moves toward defender, defender shakes
        progress = min(elapsed / duration, 1.0)
        # Ease-in/ease-out for smoother attack motion
        ease = 0.5 - 0.5 * math.cos(math.pi * progress)
        if attacker.piece_type == PieceType.KNIGHT:
            # Knight: jump attack
            jump = int(-18 * math.sin(math.pi * progress))
            ax_anim = ax + int((dx - ax) * ease * 0.7)
            ay_anim = ay + int((dy - ay) * ease * 0.7) + jump
        elif attacker.piece_type == PieceType.ROOK:
            # Rook: slide attack
            ax_anim = ax + int((dx - ax) * ease * 0.8)
            ay_anim = ay + int((dy - ay) * ease * 0.8)
        elif attacker.piece_type == PieceType.BISHOP:
            # Bishop: diagonal slide
            ax_anim = ax + int((dx - ax) * ease * 0.8)
            ay_anim = ay + int((dy - ay) * ease * 0.8)
        elif attacker.piece_type == PieceType.QUEEN:
            # Queen: fast dash
            ax_anim = ax + int((dx - ax) * ease)
            ay_anim = ay + int((dy - ay) * ease)
        elif attacker.piece_type == PieceType.KING:
            # King: slow, powerful move
            ax_anim = ax + int((dx - ax) * ease * 0.5)
            ay_anim = ay + int((dy - ay) * ease * 0.5)
        else:
            # Pawn: simple step
            ax_anim = ax + int((dx - ax) * ease * 0.6)
            ay_anim = ay + int((dy - ay) * ease * 0.6)

        # Defender shake effect (stronger, more dynamic)
        shake = int(10 * math.sin(progress * 12 * math.pi) * (1 - abs(0.5 - progress) * 2)) if progress > 0.6 else 0

        # Draw attacker
        sprite_a = self.piece_sprites.get(attacker.piece_type)
        if sprite_a:
            piece_size = self.board.cell_size - 10
            scaled_sprite = pygame.transform.scale(sprite_a, (piece_size, piece_size))
            if attacker.color == Color.BLACK:
                tinted_sprite = scaled_sprite.copy()
                dark_overlay = pygame.Surface((piece_size, piece_size))
                dark_overlay.set_alpha(100)
                dark_overlay.fill((100, 50, 50))
                tinted_sprite.blit(dark_overlay, (0, 0))
                scaled_sprite = tinted_sprite
            screen.blit(scaled_sprite, (ax_anim + 5, ay_anim + 5))
            border_color = (255, 255, 255) if attacker.color == Color.WHITE else (150, 50, 50)
            pygame.draw.rect(screen, border_color, (ax_anim + 3, ay_anim + 3, piece_size + 4, piece_size + 4), 2)
        # Draw defender
        sprite_d = self.piece_sprites.get(defender.piece_type)
        if sprite_d:
            piece_size = self.board.cell_size - 10
            scaled_sprite = pygame.transform.scale(sprite_d, (piece_size, piece_size))
            if defender.color == Color.BLACK:
                tinted_sprite = scaled_sprite.copy()
                dark_overlay = pygame.Surface((piece_size, piece_size))
                dark_overlay.set_alpha(100)
                dark_overlay.fill((100, 50, 50))
                tinted_sprite.blit(dark_overlay, (0, 0))
                scaled_sprite = tinted_sprite
            screen.blit(scaled_sprite, (dx + 5 + shake, dy + 5))
            border_color = (255, 255, 255) if defender.color == Color.WHITE else (150, 50, 50)
            pygame.draw.rect(screen, border_color, (dx + 3 + shake, dy + 3, piece_size + 4, piece_size + 4), 2)
