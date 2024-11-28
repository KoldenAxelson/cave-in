# Cave In

A Python-based educational game demonstrating pathfinding, AI decision-making, and game development fundamentals.

## 🎯 Overview

Cave In started as a simple puzzle game but has evolved into an educational platform showcasing different AI approaches to game problem-solving. Players can experience the game from multiple perspectives:

- **Manual Mode**: Play traditionally using keyboard controls
- **Pathfinding AI**: Watch an AI solve the puzzle using advanced pathfinding algorithms
- **Neural Network** (Coming Soon): Observe machine learning in action as a neural network learns to play

## 🤖 AI Disclosure

This project uses AI-assisted development practices:
- Documentation and docstrings are primarily AI-generated for consistency
- Core game mechanics and architecture are human-designed
- Code implementation is a collaborative effort between human and AI

We believe in transparency about AI usage in development. While AI helps with standardization and boilerplate code, all critical design decisions and game mechanics are human-directed.

## 🎮 Game Mechanics

1. Navigate a procedurally generated cave system
2. Collect sticks (brown squares) to increase your score
3. Use sticks to remove rocks (gray squares) blocking your path
4. Plan carefully - getting trapped ends the game!

## 🤖 AI Features

### Pathfinding AI
- Implements A* pathfinding with dynamic path recalculation
- Demonstrates optimal resource collection strategies
- Visualizes decision-making process in real-time

### Neural Network Mode (Coming Soon)
- Watch an AI learn to play through reinforcement learning
- Compare performance against pathfinding AI
- Observe different training strategies

## 🛠️ Technical Implementation

Built with Python and Pygame, featuring:
- Object-oriented design with dataclass implementation
- Abstract base classes for AI interfaces
- Modular architecture supporting multiple AI implementations
- Configurable difficulty and visualization settings

## 🚀 Getting Started

1. Ensure Python 3.7+ is installed
2. Clone and set up the repository:
```bash
    git clone https://github.com/KoldenAxelson/cave-in.git
    cd cave-in
    python -m venv venv
    source venv/bin/activate
    pip install pygame
    python main.py
```

## 🎯 How to Play

1. Navigate the cave using WASD keys
2. Collect brown sticks to increase your score
3. When facing rocks (gray squares), press SPACE to remove them using a stick
4. Plan your moves carefully - the game ends if you get trapped!
5. Try to move as little as possible before the cave collapses!

## 🔧 Technical Details

- Built with Python and Pygame
- Uses a grid-based movement system
- Implements a viewport system that follows the player
- Features a modular cell-based architecture for easy expansion

## 📝 Educational Value

This project serves as a practical demonstration of:
- Pathfinding algorithms in game environments
- AI decision-making strategies
- Game development patterns and practices
- Neural network applications in gaming

## 🤝 Contributing

Contributions welcome! Particularly interested in:
- Neural network implementation
- Additional AI strategies
- Performance optimizations
- Educational documentation

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- None currently reported

## 🎨 Credits

Created by Kolden Axelson

---

Made with ❤️, Python, and a passion for AI education


