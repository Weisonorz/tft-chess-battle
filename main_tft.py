import pygame
import sys
from tft_game import TFTGame, GamePhase

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display - larger window with better spacing
    SCREEN_WIDTH = 1400
    SCREEN_HEIGHT = 1000
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("🏰 TFT Chess Battle ⚔️")
    
    # Set up the clock for frame rate
    clock = pygame.time.Clock()
    FPS = 60
    
    # Create TFT game instance
    game = TFTGame()
    
    # Add initial message to log
    game.add_to_log("TFT Chess Battle started! Buy pieces and prepare for war!")
    game.add_to_log("Shop is open - click items to buy with coins")
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    game.handle_click(mouse_x, mouse_y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.selected_piece and game.phase == GamePhase.BATTLE:
                    # Toggle action mode during battle
                    game.toggle_action_mode()
                elif event.key == pygame.K_b and game.phase in [GamePhase.SETUP, GamePhase.SHOP]:
                    # Start battle phase
                    game.start_battle_phase()
                elif event.key == pygame.K_n and game.phase == GamePhase.END_ROUND:
                    # Start next round
                    game.start_next_round()
                elif event.key == pygame.K_e and game.battle_ended and game.phase == GamePhase.BATTLE:
                    # End battle manually
                    game.end_battle_phase()
                elif event.key == pygame.K_r:  # Reset game
                    game = TFTGame()
                    game.add_to_log("Game reset! TFT Chess Battle restarted!")
                elif event.key == pygame.K_ESCAPE:  # Exit with ESC
                    running = False
        
        # Draw everything
        game.draw(screen)
        
        # Draw controls based on current phase
        draw_phase_controls(screen, game)
        
        # Update the display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
    
    # Quit
    pygame.quit()
    sys.exit()

def draw_phase_controls(screen: pygame.Surface, game: TFTGame):
    """Draw context-sensitive controls"""
    font = pygame.font.Font(None, 20)
    
    controls_area = pygame.Rect(50, 950, 1300, 25)
    pygame.draw.rect(screen, (30, 30, 50), controls_area)
    pygame.draw.rect(screen, (100, 100, 120), controls_area, 2)
    
    # Controls based on phase
    if game.phase == GamePhase.SHOP or game.phase == GamePhase.SETUP:
        controls = [
            "🛒 Shop open: Click items to buy with coins" if game.shop_open else "🔒 Shop closed: Prepare for battle",
            "🎯 Click empty board positions to deploy pieces from reserve",
            "🚀 Press B to start battle phase",
            "🔄 R = reset, ESC = quit"
        ]
    elif game.phase == GamePhase.BATTLE:
        controls = [
            "⚔️ Battle Phase: Move and attack enemies",
            "🖱️ Click pieces to select, SPACE = toggle move/attack",
            "🏁 Press E to end battle early",
            "🎯 Kill enemies to earn coins!"
        ]
    elif game.phase == GamePhase.END_ROUND:
        controls = [
            f"🏆 Round {game.round_number} Complete!",
            "💰 Both players earned +1 coin",
            "🚀 Press N for next round",
            f"🛒 Shop {'opens' if (game.round_number + 1) % 3 == 1 else 'stays closed'} next round"
        ]
    else:
        controls = ["🎮 Use keyboard shortcuts to control the game"]
    
    # Draw controls in a single line with larger font
    control_font = pygame.font.Font(None, 18)
    all_controls = " | ".join(controls)
    text = control_font.render(all_controls, True, (200, 200, 200))
    screen.blit(text, (controls_area.x + 5, controls_area.y + 5))

if __name__ == "__main__":
    main()