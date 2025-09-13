import pygame
import sys
from piece import Color
from tft_game import TFTGame, GamePhase

def main():
    # Initialize Pygame
    pygame.init()
    
    # Allow custom screen size via command line or default
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=1600, help="Screen width")
    parser.add_argument("--height", type=int, default=1000, help="Screen height")
    args, _ = parser.parse_known_args()
    # Default to fullscreen
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("🏰 TFT Chess Battle ⚔️")
    SCREEN_WIDTH = pygame.display.Info().current_w
    SCREEN_HEIGHT = pygame.display.Info().current_h

    # Set up the clock for frame rate
    clock = pygame.time.Clock()
    FPS = 60

    # Create TFT game instance
    game = TFTGame(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
    
    # Add initial message to log
    game.add_to_log("TFT Chess Battle started! Buy pieces and prepare for war!")
    game.add_to_log("Shop is open - click items to buy with coins")
    
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                game = TFTGame(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

            # --- Mouse handling ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.end:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    SCREEN_WIDTH = pygame.display.Info().current_w
                    SCREEN_HEIGHT = pygame.display.Info().current_h
                    game = TFTGame(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                    game.add_to_log("Game reset! TFT Chess Battle restarted!")
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    # First try drag from reserve
                    game.handle_mouse_down(mouse_x, mouse_y)
                    # If not dragging, treat it as a normal click (shop/board/etc.)
                    if not game.dragging_piece:
                        game.handle_click(mouse_x, mouse_y)

            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                game.handle_mouse_motion(mouse_x, mouse_y)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click released
                    
                    mouse_x, mouse_y = event.pos
                    if game.dragging_piece:
                        
                        game.handle_mouse_up(mouse_x, mouse_y)
                    else:
                        # This ensures clicks still register properly
                        game.handle_click(mouse_x, mouse_y)
                    

            # --- Keyboard handling ---
            elif event.type == pygame.KEYDOWN:
                if game.end:
                    SCREEN_WIDTH = pygame.display.Info().current_w
                    SCREEN_HEIGHT = pygame.display.Info().current_h
                    game = TFTGame(screen_width=SCREEN_WIDTH, screen_height = SCREEN_HEIGHT)
                    game.add_to_log("Game reset! TFT Chess Battle restarted!")
                if event.key == pygame.K_SPACE and game.selected_piece and game.phase == GamePhase.BATTLE:
                    game.toggle_action_mode()
                elif event.key == pygame.K_b and game.phase in [GamePhase.SETUP, GamePhase.SHOP]:
                    game.start_battle_phase()
                elif event.key == pygame.K_n and game.phase == GamePhase.END_ROUND:
                    game.start_next_round()
                elif event.key == pygame.K_r:  # Reset game
                    if not game.end:
                        game = TFTGame()
                        game.add_to_log("Game reset! TFT Chess Battle restarted!")
                elif event.key == pygame.K_ESCAPE:
                    running = False

        
        # Draw everything
        game.draw(screen)
        
        # Draw controls based on current phase
        draw_phase_controls(screen, game)
        
        # Overlay CRT scanline effect
        try:
            crt_overlay = pygame.image.load("Hackathon_image/crt_scanlines.png").convert_alpha()
            crt_overlay = pygame.transform.scale(crt_overlay, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(crt_overlay, (0, 0))
        except Exception:
            pass

        # Update the display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
    
    # Quit
    pygame.quit()
    sys.exit()

def draw_phase_controls(screen: pygame.Surface, game: TFTGame):
    """Draw context-sensitive controls at the very bottom, not blocking UI"""
    font = pygame.font.Font(None, 20)
    controls_area = pygame.Rect(0, screen.get_height() - 40, screen.get_width(), 35)
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
    screen.blit(text, (controls_area.x + 10, controls_area.y + 8))

if __name__ == "__main__":
    main()
