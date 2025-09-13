from enum import Enum
import random
from piece import *

class CardType(Enum):
    ARROW_VOLLEY = "arrow_volley"
    DISARM = "disarm"
    REDEMPTION = "redemption"
    LIGHTNING = 'lightning'
    TOWER = 'Tower Defense'
    # Add more card types here as needed

class Card:
    def __init__(self, card_type: CardType, immediate: bool, icon_path: str, name: str, cost: int = 3):
        self.card_type = card_type
        self.immediate = immediate
        self.icon_path = icon_path
        self.name = name
        self.cost = cost

    def get_effect_description(self):
        if self.card_type == CardType.ARROW_VOLLEY:
            return "Arrow Volley: -1 HP all opponent units"
        elif self.card_type == CardType.DISARM:
            return "Disarm: Set attack=0"
        elif self.card_type == CardType.REDEMPTION:
            return "Redemption: all units on black tiles take 1 damage; all units on white tiles gain 1 health"
        elif self.card_type == CardType.LIGHTNING:
            return "Lightning: 3 dmg to five random tiles on the board"
        elif self.card_type == CardType.Tower:
            return "Gain 2 rooks that cannot move."
        else:
            return "Unknown effect"
    
    def cleanup(self, game, player):
        for row in range(8):
            for col in range(8):
                piece = game.board.grid[row][col]
                if piece and not piece.is_alive():
                    game.board.grid[row][col] = None
        

    def apply_effect(self, game, player):
        """Apply the card's effect to the game. For immediate cards only."""
        if self.card_type == CardType.ARROW_VOLLEY:
            # Arrow Volley: deal 1 damage to all units
            for row in range(8):
                for col in range(8):
                    piece = game.board.grid[row][col]
                    if piece and piece.is_alive() and piece.color != player:
                        piece.hp = max(0, piece.hp - 1)
            game.add_to_log(f"{player.value.title()} used Arrow Volley! Enemy units take 1 damage.")
        # Disarm is stored, effect applied later via inventory UI
        # Add more card effects here as needed
        elif self.card_type == CardType.REDEMPTION:
            for row in range(8):
                for col in range(8):
                    piece = game.board.grid[row][col]
                    if (row + col) % 2 == 1: # black
                        if piece and piece.is_alive():
                            piece.hp = max(0, piece.hp-1)
                    else:
                        if piece and piece.is_alive():
                            piece.hp = min(piece.max_hp, piece.hp+1)
            game.add_to_log(f"{player.value.title()} used Redemption! Black tiles take 1 dmg; white tiles gain 1 health.")

        elif self.card_type == CardType.LIGHTNING:
            numbers = random.sample(range(64), 5)
            for i in numbers:
                row = i // 8
                col = i % 8
                piece = game.board.grid[row][col]
                if piece and piece.is_alive():
                    piece.hp = max(0, piece.hp-3)
            game.add_to_log(f"{player.value.title()} used Lightning! Five random tiles take 3 dmg.")
        elif self.card_type == CardType.TOWER:
            if player == Color.WHITE:
                game.white_reserve.append(Tower(player, 0, 0))
                game.white_reserve.append(Tower(player, 0, 0))
            elif player == Color.BLACK:
                game.black_reserve.append(Tower(player, 0, 0))
                game.black_reserve.append(Tower(player, 0, 0))
            game.add_to_log(f"{player.value.title()} used Tower Defense! Gain 2 rooks that cannot move.")
        self.cleanup(game, player)
