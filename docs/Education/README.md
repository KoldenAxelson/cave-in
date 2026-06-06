# Cave In — a Python + ML curriculum

This folder is a self-guided course that uses the Cave In game as a worked
example, taking you from basic Python all the way to a neural network that learns
to play the game by itself.

## Who this is for

You should be comfortable with an afternoon's worth of Python: running a program,
writing a function, using variables, and knowing what a list is. Everything else
is taught here, building one idea on top of the previous one.

The trick that makes this work: **every concept is something you can go open and
read in this very project.** You're not learning abstract theory — you're
learning by understanding code that actually runs a game.

## How to use it

Work through the lessons in order. Each one follows the same shape:

1. **Goal** — what you'll be able to do afterward.
2. **Where it lives** — the real files in this project the lesson is about.
3. **The concept** — explained in plain language.
4. **In the code** — a walk through the actual implementation.
5. **Try it yourself** — small exercises to make it stick.
6. **Takeaways** and a pointer to the next lesson.

Keep the project open in an editor as you read. When a lesson mentions a file,
open it. Run things with the `Makefile` (see Lesson 1).

## The lessons

**Foundations**
- [Lesson 1 — Getting started & the big picture](01_GETTING_STARTED_LESSON.md)
- [Lesson 2 — Representing the world (tuples, dicts, the grid)](02_REPRESENTING_THE_WORLD_LESSON.md)
- [Lesson 3 — Objects and inheritance (the cells)](03_OBJECTS_AND_INHERITANCE_LESSON.md)
- [Lesson 4 — Constants, enums, and type hints](04_CONSTANTS_ENUMS_AND_TYPES_LESSON.md)

**Gameplay & algorithms**
- [Lesson 5 — The game loop and player input](05_THE_GAME_LOOP_AND_INPUT_LESSON.md)
- [Lesson 6 — Recursion and flood fill](06_RECURSION_AND_FLOOD_FILL_LESSON.md)
- [Lesson 7 — Pathfinding with breadth-first search](07_PATHFINDING_WITH_BFS_LESSON.md)

**Artificial intelligence & machine learning**
- [Lesson 8 — Interfaces and swappable brains](08_INTERFACES_AND_SWAPPABLE_BRAINS_LESSON.md)
- [Lesson 9 — Reinforcement learning basics](09_REINFORCEMENT_LEARNING_BASICS_LESSON.md)
- [Lesson 10 — Neural networks and DQN](10_NEURAL_NETWORKS_AND_DQN_LESSON.md)
- [Lesson 11 — Running experiments](11_RUNNING_EXPERIMENTS_LESSON.md)

## A note on the goal

By the end you won't just "know about" machine learning — you'll have read,
modified, and run a complete reinforcement-learning agent, and understand every
layer beneath it: the game, the data structures, the algorithms, and the training
loop. That foundation is far more valuable than any single framework.
