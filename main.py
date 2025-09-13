import pygame
import sys
from game import Game

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 900
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("⚔️ Retro Pixel Chess Battle ⚔️")
    
    # Set up the clock for frame rate
    clock = pygame.time.Clock()
    FPS = 60
    
    # Create game instance
    game = Game()
    
    # Add initial message to log
    game.add_to_log("Game started! White moves first.")
    
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
                if event.key == pygame.K_SPACE and game.selected_piece:  # Toggle mode with spacebar
                    game.action_mode = "attack" if game.action_mode == "move" else "move"
                    mode_msg = f"Switched to {game.action_mode.upper()} mode"
                    game.add_to_log(mode_msg)
                if event.key == pygame.K_r:  # Reset game with R key
                    game.reset()
                    game.add_to_log("Game reset! White moves first.")
                elif event.key == pygame.K_ESCAPE:  # Exit with ESC
                    running = False
        
        # Draw everything
        game.draw(screen)
        
        # Draw instructions panel
        font = pygame.font.Font(None, 24)
        instructions_x = SCREEN_WIDTH - 300
        instructions_y = 150
        panel_width = 280
        panel_height = 200
        
        # Instructions panel background
        pygame.draw.rect(screen, (40, 40, 60), (instructions_x, instructions_y, panel_width, panel_height))
        pygame.draw.rect(screen, (100, 100, 120), (instructions_x, instructions_y, panel_width, panel_height), 2)
        
        # Panel title
        title = font.render("🎮 CONTROLS", True, (255, 215, 100))
        screen.blit(title, (instructions_x + 10, instructions_y + 10))
        
        instructions = [
            "🖱️ Click to select pieces",
            "⚪ White pieces = Your army", 
            "🔴 Red pieces = Enemy army",
            "🟡 Yellow = selected piece",
            "🟢 Green = move targets",
            "🔴 Red = attack targets",
            "⌨️ SPACE = toggle mode",
            "🔄 R = reset, 🚪 ESC = quit"
        ]
        
        small_font = pygame.font.Font(None, 18)
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (instructions_x + 10, instructions_y + 40 + i * 25))
        
        # Update the display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
    
    # Quit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()