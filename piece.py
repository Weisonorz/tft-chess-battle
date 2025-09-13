import pygame
from typing import List, Tuple, Optional
from enum import Enum

class PieceType(Enum):
    PAWN = "pawn"
    KNIGHT = "knight" 
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class Piece:
    def __init__(self, piece_type: PieceType, color: Color, row: int, col: int):
        self.piece_type = piece_type
        self.color = color
        self.row = row
        self.col = col
        self.max_hp = self._get_max_hp()
        self.hp = self.max_hp
        self.attack = self._get_attack()
        self.cost = self._get_cost()
        self.sprite = None
        
    def _get_max_hp(self) -> int:
        hp_values = {
            PieceType.PAWN: 3,
            PieceType.KNIGHT: 6,
            PieceType.BISHOP: 5,
            PieceType.ROOK: 8,
            PieceType.QUEEN: 10,
            PieceType.KING: 12
        }
        return hp_values[self.piece_type]
    
    def _get_attack(self) -> int:
        attack_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 2,
            PieceType.ROOK: 4,
            PieceType.QUEEN: 5,
            PieceType.KING: 2
        }
        return attack_values[self.piece_type]
    
    def _get_cost(self) -> int:
        cost_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: float('inf')
        }
        return cost_values[self.piece_type]
    
    def load_sprite(self, sprite_path: str):
        self.sprite = pygame.image.load(sprite_path)
        
    def get_attack_range(self) -> int:
        """Get the attack range for this piece type"""
        attack_ranges = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 1, 
            PieceType.BISHOP: 3,
            PieceType.ROOK: 3,
            PieceType.QUEEN: 3,
            PieceType.KING: 1
        }
        return attack_ranges[self.piece_type]
    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        moves = []
        
        if self.piece_type == PieceType.PAWN:
            moves = self._get_pawn_moves(board)
        elif self.piece_type == PieceType.KNIGHT:
            moves = self._get_knight_moves(board)
        elif self.piece_type == PieceType.BISHOP:
            moves = self._get_bishop_moves(board)
        elif self.piece_type == PieceType.ROOK:
            moves = self._get_rook_moves(board)
        elif self.piece_type == PieceType.QUEEN:
            moves = self._get_queen_moves(board)
        elif self.piece_type == PieceType.KING:
            moves = self._get_king_moves(board)
            
        return moves
    
    def _get_pawn_moves(self, board) -> List[Tuple[int, int]]:
        moves = []
        direction = -1 if self.color == Color.WHITE else 1
        start_row = 6 if self.color == Color.WHITE else 1
        
        # Move forward one square
        new_row = self.row + direction
        if 0 <= new_row < 8 and board[new_row][self.col] is None:
            moves.append((new_row, self.col))
            
            # Move forward two squares from starting position
            if self.row == start_row:
                new_row = self.row + 2 * direction
                if 0 <= new_row < 8 and board[new_row][self.col] is None:
                    moves.append((new_row, self.col))
        
        return moves
    
    def _get_pawn_attack_targets(self, board) -> List[Tuple[int, int]]:
        """Pawn attack: Diagonal captures"""
        targets = []
        direction = -1 if self.color == Color.WHITE else 1
        
        # Diagonal attacks
        for col_offset in [-1, 1]:
            new_row = self.row + direction
            new_col = self.col + col_offset
            if (0 <= new_row < 8 and 0 <= new_col < 8):
                target_piece = board[new_row][new_col]
                if (target_piece and target_piece.color != self.color and target_piece.is_alive()):
                    targets.append((new_row, new_col))
                    
        return targets
    
    def _get_knight_moves(self, board) -> List[Tuple[int, int]]:
        """Knight movement: L-shape (2+1) to empty squares only"""
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row = self.row + dr
            new_col = self.col + dc
            if (0 <= new_row < 8 and 0 <= new_col < 8 and 
                board[new_row][new_col] is None):  # Only empty squares for movement
                moves.append((new_row, new_col))
                
        return moves
    
    def _get_knight_attack_targets(self, board) -> List[Tuple[int, int]]:
        """Knight attack: Same L-shape pattern but targeting enemies"""
        targets = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row = self.row + dr
            new_col = self.col + dc
            if (0 <= new_row < 8 and 0 <= new_col < 8):
                target_piece = board[new_row][new_col]
                if (target_piece and target_piece.color != self.color and target_piece.is_alive()):
                    targets.append((new_row, new_col))
                    
        return targets
    
    def _get_bishop_moves(self, board) -> List[Tuple[int, int]]:
        """Bishop movement: Diagonal paths to empty squares until blocked"""
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + i * dr
                new_col = self.col + i * dc
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                    
                if board[new_row][new_col] is None:
                    moves.append((new_row, new_col))
                else:
                    break  # Stop at any piece for movement
                    
        return moves
    
    def _get_bishop_attack_targets(self, board) -> List[Tuple[int, int]]:
        """Bishop attack: Attack first enemy found along diagonal paths"""
        targets = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + i * dr
                new_col = self.col + i * dc
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                    
                target_piece = board[new_row][new_col]
                if target_piece:
                    if target_piece.color != self.color and target_piece.is_alive():
                        targets.append((new_row, new_col))
                    break  # Stop at first piece found
                    
        return targets
    
    def _get_rook_moves(self, board) -> List[Tuple[int, int]]:
        """Rook movement: Vertical/horizontal paths to empty squares until blocked"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + i * dr
                new_col = self.col + i * dc
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                    
                if board[new_row][new_col] is None:
                    moves.append((new_row, new_col))
                else:
                    break  # Stop at any piece for movement
                    
        return moves
    
    def _get_rook_attack_targets(self, board) -> List[Tuple[int, int]]:
        """Rook attack: Attack first enemy found along vertical/horizontal paths"""
        targets = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = self.row + i * dr
                new_col = self.col + i * dc
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                    
                target_piece = board[new_row][new_col]
                if target_piece:
                    if target_piece.color != self.color and target_piece.is_alive():
                        targets.append((new_row, new_col))
                    break  # Stop at first piece found
                    
        return targets
    
    def _get_queen_moves(self, board) -> List[Tuple[int, int]]:
        """Queen movement: Combination of rook and bishop movement"""
        return self._get_rook_moves(board) + self._get_bishop_moves(board)
    
    def _get_queen_attack_targets(self, board) -> List[Tuple[int, int]]:
        """Queen attack: Attack first enemy in any straight or diagonal direction"""
        return self._get_rook_attack_targets(board) + self._get_bishop_attack_targets(board)
    
    def _get_king_moves(self, board) -> List[Tuple[int, int]]:
        """King movement: 1 square in any direction to empty squares"""
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_row = self.row + dr
            new_col = self.col + dc
            if (0 <= new_row < 8 and 0 <= new_col < 8 and 
                board[new_row][new_col] is None):  # Only empty squares for movement
                moves.append((new_row, new_col))
                
        return moves
    
    def _get_king_attack_targets(self, board) -> List[Tuple[int, int]]:
        """King attack: Attack enemy in any adjacent square"""
        targets = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_row = self.row + dr
            new_col = self.col + dc
            if (0 <= new_row < 8 and 0 <= new_col < 8):
                target_piece = board[new_row][new_col]
                if (target_piece and target_piece.color != self.color and target_piece.is_alive()):
                    targets.append((new_row, new_col))
                    
        return targets
    
    def take_damage(self, damage: int):
        self.hp = max(0, self.hp - damage)
        
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def move_to(self, row: int, col: int):
        self.row = row
        self.col = col
    
    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
        """Get all enemy pieces this piece can attack"""
        if self.piece_type == PieceType.PAWN:
            return self._get_pawn_attack_targets(board)
        elif self.piece_type == PieceType.KNIGHT:
            return self._get_knight_attack_targets(board)
        elif self.piece_type == PieceType.BISHOP:
            return self._get_bishop_attack_targets(board)
        elif self.piece_type == PieceType.ROOK:
            return self._get_rook_attack_targets(board)
        elif self.piece_type == PieceType.QUEEN:
            return self._get_queen_attack_targets(board)
        elif self.piece_type == PieceType.KING:
            return self._get_king_attack_targets(board)
        
        return []
    
    def can_attack(self, target_row: int, target_col: int, board) -> bool:
        """Check if this piece can attack the target position"""
        if not (0 <= target_row < 8 and 0 <= target_col < 8):
            return False
            
        target_piece = board[target_row][target_col]
        if not target_piece or target_piece.color == self.color or not target_piece.is_alive():
            return False
            
        # Use the specific attack targets logic for each piece type
        attack_targets = self.get_attack_targets(board)
        return (target_row, target_col) in attack_targets