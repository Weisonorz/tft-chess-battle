# 🏰 TFT Chess Battle ⚔️

A revolutionary chess game that combines traditional chess mechanics with **Teamfight Tactics (TFT)** gameplay elements. Built for HackCMU's "Retro - Turn Something New into Something Old" track.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-v2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎮 Game Overview

Transform traditional chess into an exciting strategy game where pieces have **HP**, **Attack values**, and **unique abilities**. Combine this with TFT's economic system, shop mechanics, and strategic army building for an entirely new gaming experience!

### 🌟 Key Features

- **🎯 RPG-Style Chess**: Each piece has HP, Attack, and Cost stats
- **💰 Economic System**: Earn coins, buy pieces, build your army
- **🛒 Dynamic Shop**: Rotating piece selection every 3 rounds
- **⚔️ Combat System**: Damage-based battles with piece elimination
- **🎨 Retro Pixel Art**: Beautiful 16-bit style graphics
- **🔄 Turn-Based Strategy**: Classic chess movement with modern mechanics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Pygame 2.0+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Weisonorz/tft-chess-battle.git
   cd tft-chess-battle
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**
   ```bash
   python main_tft.py
   ```

## 🎯 How to Play

### Game Modes

#### **🛒 Shop Phase** (Rounds 1, 4, 7...)
- Click shop items to purchase pieces with coins
- Build your army strategically
- Each piece has different costs and abilities

#### **⚔️ Battle Phase**
- **Click pieces** to select (only your pieces during your turn)
- **Green highlights** = valid movement positions
- **Press SPACE** to toggle between MOVE and ATTACK modes
- **Red highlights** = attack targets
- **Click to execute** moves or attacks

#### **📈 Economy**
- **Starting coins**: 3 per player
- **Round income**: +1 coin per round
- **Kill rewards**: Earn coins for eliminating enemies
- **Victory bonus**: +3 coins for winning battles

### 🎲 Piece Stats

| Piece | HP | Attack | Cost | Special |
|-------|----|---------|----|---------|
| ♙ **Pawn** | 3 | 1 | 1🪙 | Cheap & reliable |
| ♘ **Knight** | 6 | 3 | 3🪙 | L-shaped movement |
| ♗ **Bishop** | 5 | 2 | 3🪙 | Diagonal strikes |
| ♖ **Rook** | 8 | 4 | 5🪙 | Line domination |
| ♕ **Queen** | 10 | 5 | 9🪙 | Ultimate power |
| ♔ **King** | 12 | 2 | ∞ | Must protect! |

### 🎮 Controls

| Action | Key/Mouse | Description |
|--------|-----------|-------------|
| **Select Piece** | Left Click | Select your pieces |
| **Move/Attack** | Left Click | Execute highlighted actions |
| **Toggle Mode** | SPACE | Switch between MOVE/ATTACK |
| **Start Battle** | B | Begin combat phase |
| **Next Round** | N | Advance to next round |
| **Reset Game** | R | Start over |
| **Quit** | ESC | Exit game |

---

## 🃏 Effect Cards & Shop System

### Card System

- **Effect cards** are now integrated into the shop and economy.
- Shop appears every 3 rounds, with 5 slots per shop:
  - **50%** chance for chess piece
  - **30%** chance for effect card
  - **20%** chance for consumable
- Cards cost **3 coins**.

#### Card Types

- **Arrow Volley** (Immediate): Instantly deals 1 damage to all enemy units on the board. Dead units are removed and their spaces freed.
- **Disarm** (Stored): Added to your Card Inventory. Click to select an enemy unit and set its attack to 0 permanently.

#### UI Integration

- Shop UI displays cards with icons, name, cost, and a ⚡ for immediate cards.
- Stored cards appear in a Card Inventory panel and are clickable for targeted effects.

#### Usage

- Buying a card deducts coins.
- Immediate cards resolve instantly.
- Stored cards are added to inventory for later use.

#### Restart Behavior

- After game over, the UI does **not** restart automatically.
- Manual restart is required via mouse click or key press.
- Restarted game always launches in fullscreen mode.

---

## 🏗️ Technical Architecture

### Project Structure
```
tft-chess-battle/
├── main_tft.py          # Main game launcher
├── tft_game.py          # Core TFT game logic
├── card.py              # Card system and effects
├── game.py              # Original chess game
├── piece.py             # Chess piece classes
├── board.py             # Game board management
├── Hackathon_image/     # Game assets
│   ├── king.png
│   ├── queen.png
│   ├── knight.png
│   ├── pawn.png
│   └── ...
├── requirements.txt     # Dependencies
└── README.md           # This file
```

### Core Components

- **`TFTGame`**: Main game controller with shop/economy systems
- **`Piece`**: Individual chess pieces with RPG stats
- **`Board`**: 8x8 game board with rendering
- **`Card`**: Effect card system and logic
- **UI System**: Vertical layout preventing component blocking

## 🎨 Game Phases

### 1. **Setup Phase**
- Position your pieces strategically
- Plan your army composition
- Prepare for battle

### 2. **Shop Phase** (Every 3 rounds)
- 5 random items available for purchase (pieces, cards, consumables)
- Weighted selection (Pawns common, Queens rare, cards and consumables mixed)
- Build your reserve army and card inventory

### 3. **Battle Phase**
- Turn-based combat
- Move and attack with your pieces
- Eliminate enemy king to win

### 4. **End Round**
- Distribute rewards
- Advance to next round
- Economy grows over time

## 🛠️ Development

### Built With
- **Python 3.8+** - Core language
- **Pygame 2.0+** - Graphics and game engine
- **Custom Assets** - Retro pixel art pieces

### Game Design Principles
- **Accessible**: Easy to learn, hard to master
- **Strategic**: Multiple layers of decision making
- **Visual**: Clear feedback and beautiful graphics
- **Balanced**: Each piece has unique value proposition

## 🏆 HackCMU - Retro Track

This project was created for HackCMU's "Retro - Turn Something New into Something Old" track, successfully combining:

- **Classic Chess** (Old) with **Modern TFT Mechanics** (New)
- **Retro Pixel Art** aesthetic
- **Strategic Depth** of both game genres
- **Innovative Gameplay** that respects both traditions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🎯 Future Enhancements

- [ ] **Multiplayer Support**: Online battles
- [ ] **Advanced Pieces**: Special abilities and effects
- [ ] **Tournaments**: Competitive play modes
- [ ] **Sound Effects**: Retro chip-tune audio
- [ ] **Animations**: Smooth piece movements
- [ ] **AI Opponents**: Single-player campaigns

## 🙏 Acknowledgments

- **HackCMU** for the inspiring challenge
- **Chess Community** for the timeless game mechanics
- **TFT/Auto-battler** games for economic inspiration
- **Retro Gaming** for the aesthetic direction

---

Made with ❤️ for HackCMU 2025

**Play, Strategize, Conquer!** 🏆
