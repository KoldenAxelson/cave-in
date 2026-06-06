# Lesson 8 — Interfaces and swappable brains

## Goal

Understand **abstract interfaces** — the contract that lets the path finder *and* a
neural network plug into the game interchangeably, without the game knowing the
difference.

## Where it lives

- `src/ai/ai_interface.py` — the `AIInterface` contract.
- `src/ai/pathfinding/pathfinder.py` — one implementation (the path finder).
- `src/ai/learning/neural_controller.py` — another (the neural net, from Lesson 10).

## The concept: a contract, not an implementation

Back in Lesson 5 we saw that the game asks `get_movement()` for a direction and
doesn't care who answers. To make that work safely, we need a **contract**: any
computer player must promise to provide certain methods. That contract is an
**abstract base class (ABC)**.

Open `src/ai/ai_interface.py`:

```python
class AIInterface(ABC):
    @abstractmethod
    def get_movement(self) -> Position: ...

    @abstractmethod
    def should_use_action(self) -> bool: ...

    @abstractmethod
    def update(self, world) -> None: ...
```

`ABC` means "abstract base class," and `@abstractmethod` means "any real subclass
**must** provide this method." You can't create an `AIInterface` directly — it's
not a player, it's the *promise* of one. It says: "to be an AI for this game, you
must be able to (1) choose a movement, (2) say whether to use the faced cell, and
(3) update yourself with the latest world."

## Why this is powerful

Think of it like a wall socket. The socket defines a shape (the contract). A lamp,
a charger, a toaster — anything that matches the plug shape works, and the wall
doesn't need to know which is plugged in.

Here, `AIInterface` is the socket. The path finder is one appliance; the neural
network is another. The game code is the wall — it just calls `get_movement()` and
trusts the contract. Look at how the game chooses one (`game.py`):

```python
if self.chosen_mode == "pathfinder":
    self.ai_controller = PathFinder(self.world)
elif self.chosen_mode == "neural":
    from src.ai.learning.neural_controller import NeuralController
    self.ai_controller = NeuralController(self.world)
```

Both `PathFinder` and `NeuralController` satisfy `AIInterface`, so both drop into
the same `ai_controller` slot. The hundreds of lines of game and rendering code
underneath don't change at all when you switch brains. **That separation is what
made it possible to add machine learning to this project without rewriting the
game.**

## This is the hinge of the whole course

Everything before this lesson was about the game and classic algorithms.
Everything after is about machine learning. This interface is the seam between the
two halves: the ML agent we're about to build is "just another `AIInterface`." When
you train a neural network in the coming lessons, the payoff is an object that
implements these three methods — and then it plays Cave In through the exact same
door every other controller uses.

## Try it yourself

1. Open `neural_controller.py` and confirm it defines `get_movement`,
   `should_use_action`, and `update`. That's the contract being fulfilled.
2. What error do you think you'd get if you wrote a new controller class that
   inherited from `AIInterface` but forgot to implement `should_use_action`?
   (Python refuses to let you create it — try it in a shell.)
3. Sketch the methods a `RandomController` (moves in a random direction each turn)
   would need. You now know enough to write one — it's a great warm-up.

## Takeaways

- An **abstract base class** defines a *contract*: methods every implementation
  must provide.
- It lets unrelated classes (path finder, neural net) be used interchangeably.
- This one interface is the seam that connects the "game" half of the project to
  the "machine learning" half.

Next: [Lesson 9 — Reinforcement learning basics](09_REINFORCEMENT_LEARNING_BASICS_LESSON.md).
