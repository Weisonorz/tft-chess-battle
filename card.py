from enum import Enum

class CardType(Enum):
    ARROW_VOLLEY = "arrow_volley"
    DISARM = "disarm"
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
            return "Arrow Volley: -1 HP all units"
        elif self.card_type == CardType.DISARM:
            return "Disarm: Set attack=0"
        else:
            return "Unknown effect"

    def apply_effect(self, game, player):
        """Apply the card's effect to the game. For immediate cards only."""
        if self.card_type == CardType.ARROW_VOLLEY:
            # Arrow Volley: deal 1 damage to all units
            for row in range(8):
                for col in range(8):
                    piece = game.board.grid[row][col]
                    if piece and piece.is_alive() and piece.color != player:
                        piece.hp = max(0, piece.hp - 1)
            # Remove dead pieces from board
            for row in range(8):
                for col in range(8):
                    piece = game.board.grid[row][col]
                    if piece and not piece.is_alive():
                        game.board.grid[row][col] = None
            game.add_to_log(f"{player.value.title()} used Arrow Volley! Enemy units take 1 damage.")
        # Disarm is stored, effect applied later via inventory UI
        # Add more card effects here as needed
