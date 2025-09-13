import pygame
from typing import Optional, List, Tuple
from piece import *

class Board:
    def __init__(self, cell_size=90, board_offset_x=250, board_offset_y=150):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.board_sprite = None
        self.cell_size = cell_size
        self.board_offset_x = board_offset_x
        self.board_offset_y = board_offset_y
        self.border_width = 20
        self.setup_initial_pieces()
        
    def setup_initial_pieces(self):
        # Setup white pieces - Mix of different piece types for testing
        self.grid[7][4] = King(Color.WHITE, 7, 4)      # King in center
        self.grid[7][0] = Rook(Color.WHITE, 7, 0)      # Rook on left
        self.grid[7][7] = Rook(Color.WHITE, 7, 7)      # Rook on right
        self.grid[7][1] = Knight(Color.WHITE, 7, 1)    # Knight
        self.grid[7][6] = Knight(Color.WHITE, 7, 6)    # Knight
        self.grid[7][2] = Bishop(Color.WHITE, 7, 2)    # Bishop
        self.grid[7][5] = Bishop(Color.WHITE, 7, 5)    # Bishop
        self.grid[7][3] = Queen(Color.WHITE, 7, 3)     # Queen
        
        # White pawns
        for col in range(8):
            self.grid[6][col] = Pawn(Color.WHITE, 6, col)
            
        # Setup black pieces - Mirror of white
        self.grid[0][4] = King(Color.BLACK, 0, 4)      # King in center
        self.grid[0][0] = Rook(Color.BLACK, 0, 0)      # Rook on left
        self.grid[0][7] = Rook(Color.BLACK, 0, 7)      # Rook on right
        self.grid[0][1] = Knight(Color.BLACK, 0, 1)    # Knight
        self.grid[0][6] = Knight(Color.BLACK, 0, 6)    # Knight
        self.grid[0][2] = Bishop(Color.BLACK, 0, 2)    # Bishop
        self.grid[0][5] = Bishop(Color.BLACK, 0, 5)    # Bishop
        self.grid[0][3] = Queen(Color.BLACK, 0, 3)     # Queen
        
        # Black pawns
        for col in range(8):
            self.grid[1][col] = Pawn(Color.BLACK, 1, col)
    
    def load_board_sprite(self, sprite_path: str):
        self.board_sprite = pygame.image.load(sprite_path)
        
    def get_piece_at(self, row: int, col: int) -> Optional[Piece]:
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None
    
    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8
    
    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> Optional[Piece]:
        if not (self.is_valid_position(from_row, from_col) and 
                self.is_valid_position(to_row, to_col)):
            return None
            
        piece = self.grid[from_row][from_col]
        if piece is None:
            return None
            
        target_piece = self.grid[to_row][to_col]
        
        # Move the piece
        self.grid[from_row][from_col] = None
        self.grid[to_row][to_col] = piece
        piece.move_to(to_row, to_col)
        
        return target_piece
    
    def get_all_pieces(self, color: Optional[Color] = None) -> List[Piece]:
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None and (color is None or piece.color == color):
                    pieces.append(piece)
        return pieces
    
    def get_king(self, color: Color) -> Optional[Piece]:
        for piece in self.get_all_pieces(color):
            if piece.piece_type == PieceType.KING:
                return piece
        return None
    
    def is_king_alive(self, color: Color) -> bool:
        king = self.get_king(color)
        return king is not None and king.is_alive()
    
    def get_cell_from_mouse(self, mouse_x: int, mouse_y: int) -> Tuple[int, int]:
        col = (mouse_x - self.board_offset_x) // self.cell_size
        row = (mouse_y - self.board_offset_y) // self.cell_size
        return row, col
    
    def get_cell_center(self, row: int, col: int) -> Tuple[int, int]:
        x = self.board_offset_x + col * self.cell_size + self.cell_size // 2
        y = self.board_offset_y + row * self.cell_size + self.cell_size // 2
        return x, y
    
    def draw(self, screen: pygame.Surface, palette=None, pixel_font_path=None):
        # Use retro palette if provided
        if palette is None:
            palette = {
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
        # Draw chunky pixel border
        border_rect = pygame.Rect(
            self.board_offset_x - self.border_width,
            self.board_offset_y - self.border_width,
            8 * self.cell_size + 2 * self.border_width,
            8 * self.cell_size + 2 * self.border_width
        )
        pygame.draw.rect(screen, palette["border"], border_rect, 0)
        pygame.draw.rect(screen, palette["neon_cyan"], border_rect, 4)

        # Draw chess squares with solid retro colors
        light_color = (40, 40, 60)
        dark_color = (20, 20, 30)
        for row in range(8):
            for col in range(8):
                color = light_color if (row + col) % 2 == 0 else dark_color
                x = self.board_offset_x + col * self.cell_size
                y = self.board_offset_y + row * self.cell_size
                pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size))
                # Draw chunky pixel outline for each cell
                pygame.draw.rect(screen, palette["border"], (x, y, self.cell_size, self.cell_size), 3)

        # Draw coordinate labels in pixel font
        font = pygame.font.Font(pixel_font_path or "Hackathon_image/pixel_font.ttf", 18)
        for col in range(8):
            letter = chr(ord('a') + col)
            text = font.render(letter, True, palette["neon_green"])
            x = self.board_offset_x + col * self.cell_size + self.cell_size // 2 - 8
            y = self.board_offset_y + 8 * self.cell_size + 5
            screen.blit(text, (x, y))
        for row in range(8):
            number = str(8 - row)
            text = font.render(number, True, palette["neon_green"])
            x = self.board_offset_x - 22
            y = self.board_offset_y + row * self.cell_size + self.cell_size // 2 - 10
            screen.blit(text, (x, y))
    
    def draw_pieces(self, screen: pygame.Surface):
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None and piece.is_alive():
                    x = self.board_offset_x + col * self.cell_size + 8
                    y = self.board_offset_y + row * self.cell_size + 8
                    
                    if piece.sprite:
                        # Scale sprite to fit cell with better proportions
                        scaled_sprite = pygame.transform.scale(piece.sprite, (self.cell_size - 16, self.cell_size - 16))
                        screen.blit(scaled_sprite, (x, y))
                    else:
                        # Enhanced fallback with better color distinction
                        if piece.color == Color.WHITE:
                            base_color = (240, 240, 250)    # Light cream/white
                            shadow_color = (200, 200, 210)
                            border_color = (100, 100, 120)
                            text_color = (50, 50, 100)      # Dark blue text
                        else:
                            base_color = (80, 50, 50)       # Dark red/brown
                            shadow_color = (40, 25, 25)
                            border_color = (120, 80, 80)
                            text_color = (255, 200, 200)    # Light red text
                        
                        # Draw piece shadow
                        pygame.draw.circle(screen, shadow_color, (x + 32, y + 34), 26)
                        # Draw main piece
                        pygame.draw.circle(screen, base_color, (x + 30, y + 32), 25)
                        # Draw border to make pieces more distinct
                        pygame.draw.circle(screen, border_color, (x + 30, y + 32), 25, 3)
                        
                        # Draw piece symbol with better distinction
                        font = pygame.font.Font(None, 32)
                        symbols = {
                            PieceType.KING: '♔',
                            PieceType.QUEEN: '♕', 
                            PieceType.ROOK: '♖',
                            PieceType.BISHOP: '♗',
                            PieceType.KNIGHT: '♘',
                            PieceType.PAWN: '♙'
                        }
                        symbol = symbols.get(piece.piece_type, '?')
                        text = font.render(symbol, True, text_color)
                        text_rect = text.get_rect(center=(x + 30, y + 32))
                        screen.blit(text, text_rect)
                    
                    # Draw HP bar above piece
                    if piece.hp < piece.max_hp:
                        bar_width = self.cell_size - 20
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
    
    def highlight_cell(self, screen: pygame.Surface, row: int, col: int, color: Tuple[int, int, int]):
        # Draw chunky neon pixel outline for retro highlight
        if self.is_valid_position(row, col):
            x = self.board_offset_x + col * self.cell_size
            y = self.board_offset_y + row * self.cell_size
            outline_color = color
            # Draw 3-pixel thick neon border
            pygame.draw.rect(screen, outline_color, (x, y, self.cell_size, self.cell_size), 3)
            # Draw pixel corners for extra retro effect
            pixel_size = 7
            pygame.draw.rect(screen, outline_color, (x, y, pixel_size, pixel_size))
            pygame.draw.rect(screen, outline_color, (x + self.cell_size - pixel_size, y, pixel_size, pixel_size))
            pygame.draw.rect(screen, outline_color, (x, y + self.cell_size - pixel_size, pixel_size, pixel_size))
            pygame.draw.rect(screen, outline_color, (x + self.cell_size - pixel_size, y + self.cell_size - pixel_size, pixel_size, pixel_size))
    
    def highlight_moves(self, screen: pygame.Surface, moves: List[Tuple[int, int]]):
        for row, col in moves:
            self.highlight_cell(screen, row, col, (0, 255, 0))
