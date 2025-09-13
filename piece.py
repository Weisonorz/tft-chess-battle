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
    def __init__(self, piece_type: PieceType, color: Color, row: int, col: int, attack = 0, hp = 0, max_hp = 0, cost = float('inf')):
        self.piece_type = piece_type
        self.color = color
        self.row = row
        self.col = col
        self.max_hp = max_hp
        self.hp = hp
        self.attack = attack
        self.cost = cost
        self.sprite = None
        

    
    
    def load_sprite(self, sprite_path: str):
        self.sprite = pygame.image.load(sprite_path)

    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        moves = []
        return moves

    
    
    def take_damage(self, damage: int):
        self.hp = max(0, self.hp - damage)
        
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def move_to(self, row: int, col: int):
        self.row = row
        self.col = col
    
    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
        
        
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


class Pawn(Piece):
    def __init__(self, color: Color, row: int, col: int):
        super().__init__(PieceType.PAWN, color, row, col)
        self.max_hp = 3
        self.hp = self.max_hp
        self.attack = 1
        self.cost = 1
        self.sprite = None

    def get_cost(self) -> int:
        return self.cost

    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
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

    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
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

class Knight(Piece):
    def __init__(self, color: Color, row: int, col: int):
        super().__init__(PieceType.KNIGHT, color, row, col)
        self.max_hp = 6
        self.hp = self.max_hp
        self.attack = 3
        self.cost = 3
        self.sprite = None

    def get_cost(self) -> int:
        return self.cost

    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Knight movement: L-shape (2+1) to empty squares or enemy pieces"""
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row = self.row + dr
            new_col = self.col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board[new_row][new_col]
                if target_piece is None or (target_piece.color != self.color and target_piece.is_alive()):
                    moves.append((new_row, new_col))
        return moves

    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
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

class Bishop(Piece):
    def __init__(self, color: Color, row: int, col: int):
        super().__init__(PieceType.BISHOP, color, row, col)
        self.max_hp = 5
        self.hp = self.max_hp
        self.attack = 2
        self.cost = 3
        self.sprite = None

    def get_cost(self) -> int:
        return self.cost

    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
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

    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
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


class Rook(Piece):
    def __init__(self, color: Color, row: int, col: int):
        super().__init__(PieceType.ROOK, color, row, col)
        self.max_hp = 8
        self.hp = self.max_hp
        self.attack = 4
        self.cost = 5
        self.sprite = None

    def get_cost(self) -> int:
        return self.cost

    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
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

    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
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

    
class Tower(Piece):
    def __init__(self, color: Color, row: int, col: int):
        super().__init__(PieceType.ROOK, color, row, col)
        self.max_hp = 8
        self.hp = self.max_hp
        self.attack = 4
        self.cost = 0
        self.sprite = None

    def get_cost(self) -> int:
        return self.cost

    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        return []
    
    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
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

class Queen(Piece):
    def __init__(self, color: Color, row: int, col: int):
        super().__init__(PieceType.QUEEN, color, row, col)
        self.max_hp = 10
        self.hp = self.max_hp
        self.attack = 5
        self.cost = 9
        self.sprite = None

    def get_cost(self) -> int:
        return self.cost

    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Queen movement: Combination of rook and bishop movement"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
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

    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
        """Queen attack: Attack first enemy in any straight or diagonal direction"""
        targets = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
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

class King(Piece):
    def __init__(self, color: Color, row: int, col: int):
        super().__init__(PieceType.KING, color, row, col)
        self.max_hp = 12
        self.hp = self.max_hp
        self.attack = 2
        self.cost = float('inf')
        self.sprite = None

    def get_cost(self) -> int:
        return self.cost

    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
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

    def get_attack_targets(self, board) -> List[Tuple[int, int]]:
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