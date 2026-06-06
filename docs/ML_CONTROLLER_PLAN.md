# ML Controller — Scoping & Design

A plan for teaching a machine to play Cave In, written for someone who is **not**
an ML engineer. It explains the concepts as it goes, lists everything we need to
build, and covers saving the trained "brain" so progress survives between runs.

---

## 1. The goal, in plain terms

We want a third game mode (alongside *Normal* and *Path Finder*) where the moves
are chosen by a program that **learned to play by practising**, rather than by a
hand-written algorithm like the path finder.

"Learned by practising" is the key idea. We are not going to write rules like
"walk toward the nearest stick." Instead we let the program play the game
thousands of times, tell it (with a numeric score) when it did well or badly, and
let it gradually adjust itself to score better. That family of techniques is
called **Reinforcement Learning (RL)**.

> **Honest expectation up front:** our path finder is already near the
> theoretical best for minimizing steps. A learned agent is unlikely to *beat* a
> near-optimal search — its value here is educational (watching it improve) and
> as groundwork. Where learning can genuinely shine is the **multi-stick** setting
> (`STICK_COUNT > 1`), where choosing *which* stick to chase next is a real
> decision. So we'll train and evaluate primarily with several sticks on the board.

---

## 2. The approach: Reinforcement Learning with a "DQN"

### 2.1 The mental model

Reinforcement learning has four nouns. Memorize these; everything below is built
from them:

- **Environment** — the game itself. It has a *state* (where the player, rocks,
  and sticks are) and it changes when the agent acts.
- **Observation** — the slice of the state the agent gets to "see," turned into
  numbers it can process.
- **Action** — what the agent can do this turn (move up/down/left/right, or use
  the cell it faces).
- **Reward** — a number we hand the agent after each action telling it how good
  that action was. **The reward function is how we define "playing well."**

The loop: the agent *observes*, picks an *action*, the *environment* updates and
returns a *reward* and the next observation. Repeat until the game ends (a
"cave-in," or a step limit). One full game is called an **episode**. The agent
plays many thousands of episodes and tries to collect as much total reward as
possible.

### 2.2 What the agent actually learns: a "Q-value"

We'll use a method called a **Deep Q-Network (DQN)** — the same basic idea
DeepMind used to learn Atari games. Here's the one concept it rests on:

For any situation, and any action you could take in it, there is a number called
the **Q-value**: *"if I take this action now and then keep playing well, how much
total reward should I expect?"* If the agent knew the true Q-value of every
action, playing perfectly would be trivial — just always pick the action with the
highest Q-value.

The agent doesn't know those numbers, so it **estimates** them, and improves the
estimates with experience. The thing that stores and produces those estimates is
a small **neural network** — which brings us to "the brain."

### 2.3 The "brain" = a neural network = a big bag of numbers

A neural network is, concretely, a stack of arithmetic: it takes the observation
numbers in, multiplies them by a large collection of internal numbers called
**weights**, and produces an output — here, one Q-value per possible action.

- **Training** = repeatedly nudging those weights so the Q-value estimates get
  more accurate.
- **The "brain" we save to disk is literally those weights** — a file full of
  numbers. Loading the brain = reading the numbers back so the agent plays with
  what it learned instead of starting from scratch. (More in §6.)

For a 10×10 board a *small* network is plenty, and it trains on a normal CPU in
minutes-to-hours — no special hardware needed.

### 2.4 Why DQN (and the simpler alternative)

DQN is the standard, well-documented choice for "learn to play a small grid
game," it produces a real neural-network brain (matching the project's stated
goal), and it runs fine on CPU. There's a simpler cousin called **tabular
Q-learning** that stores Q-values in a plain table instead of a network — even
more transparent, but it can't cope with seeing the whole board, so it needs
heavy hand-engineering of the observation. I recommend DQN; I mention the table
version only so you know the simpler option exists if we ever want it.

---

## 3. The design decisions (the important part)

These three choices *are* the agent. I'm proposing concrete starting points;
they're all tunable.

### 3.1 Observation — what the agent sees

The whole board, encoded as a few 10×10 grids of 0s and 1s ("layers"):

- Layer 1: a 1 where the **player** is, 0 elsewhere.
- Layer 2: a 1 in every **rock** cell.
- Layer 3: a 1 in every **stick** cell.

Plus a couple of plain numbers: **sticks currently held** and maybe **fraction of
the board filled**. This is a faithful, complete picture of the game and is easy
to explain. (It's the same trick image-based game AIs use: represent the screen
as stacked grids of numbers.)

### 3.2 Actions — what the agent can do

Five discrete choices per turn: **move up, move down, move left, move right, or
use the faced cell** (collect a stick / clear a rock). The controller turns the
chosen action into the `get_movement()` / `should_use_action()` answers the game
already expects, so it slots into the existing `AIInterface` with no changes to
the game.

### 3.3 Reward — how we define "good play" (researched)

This encodes the objective, so I checked current best practice on reward design
for grid navigation rather than guessing. Three findings drove the recipe:

- **Mostly-positive, not all-negative.** If *every* reward is a penalty, agents
  learn to **end the episode as fast as possible just to stop the bleeding** (the
  classic "suicidal agent"). In our game the episode ends at the cave-in, so an
  all-penalty scheme would literally teach it to bury the board and ignore sticks.
  The fix: make the *desired* behaviour clearly positive — collecting a stick must
  be worth far more than a step costs.

- **Dense guidance beats sparse — done the safe way.** Only rewarding the final
  goal ("sparse") learns very slowly because the agent must stumble onto sticks at
  random. Giving a little reward for *getting closer* ("dense") learns much
  faster, but a naive closeness bonus can be gamed — an agent can pace back and
  forth forever to farm "I got closer" reward.

- **Potential-based shaping fixes the gaming problem.** A foundational 1999 result
  (Ng, Harada & Russell) proves that if the closeness bonus is written as
  `γ·Φ(next) − Φ(current)` with `Φ = −(distance to nearest stick)`, it is
  **policy-preserving**: it speeds learning without changing what the best strategy
  is, and the back-and-forth exploit nets to zero. This is the principled way to
  teach "walk toward the stick."

**The recipe:**

- **+1.0** per stick collected — the main signal, deliberately the largest term.
- **Potential-based shaping** toward the nearest stick (small scale, ~0.1) for
  fast, exploit-free navigation learning. *(Front 1: walk to the stick.)*
- **−0.02** per step — a gentle "living cost" so it prefers shorter routes, kept
  well below the +1 so it never prefers ending the game over collecting.
  *(Front 2: fewer steps, which is what makes a stick-for-shortcut trade worth
  learning.)*
- **−0.1** for an illegal move (into a wall or an unaffordable rock) so it learns
  the rules fast.
- Episode ends at the cave-in (board full) or a safety step cap; no special
  end-of-game bonus.

All weights are tunable; we'll watch behaviour and adjust (normal practice).

> **Learns from scratch — no path hints.** Worth restating: the agent's inputs are
> the raw board and its outputs are the five primitive actions below. It is never
> shown a precomputed path or asked to "pick route 1/2/3." It has to discover
> navigation *and* the stick-for-shortcut trade entirely on its own. No
> pathfinding is involved.

---

## 4. What we'll build (the components)

1. **A training environment wrapper** (`src/ai/learning/environment.py`)
   A thin adapter around the existing game that exposes the two functions every RL
   trainer expects:
   - `reset()` → start a fresh game, return the first observation.
   - `step(action)` → apply one action, return `(observation, reward, done)`.
   This reuses the headless machinery we already built for the benchmark, so
   training never opens a window and runs fast.

2. **The neural network** (`src/ai/learning/network.py`)
   A small network: observation numbers in → 5 Q-values out. (A simple
   fully-connected net is enough for 10×10; we can upgrade to a tiny convolutional
   net later if useful.)

3. **The DQN trainer** (`tools/train_dqn.py`)
   The practice loop. It contains three standard DQN ingredients, each explained
   in the glossary: **experience replay**, **epsilon-greedy exploration**, and a
   **target network**. It plays episodes, learns, prints progress, and saves the
   brain periodically.

4. **Brain persistence** (`src/ai/learning/storage.py`) — see §6.

5. **The play-time controller** (`src/ai/learning/neural_controller.py`)
   A `NeuralController(AIInterface)` that loads a saved brain and, each turn,
   picks the highest-Q action. No exploration, no learning — just play. This is
   what the game uses.

6. **Menu + game wiring**
   Add a "Neural Net" entry to the start menu and a branch in `Game._configure_ai`
   (mirroring how `PathFinder` is wired today). If no brain file exists yet, the
   option explains it needs training first.

7. **Evaluation**
   Extend the existing `tools/benchmark_pathfinder.py` (or a sibling) to score the
   trained agent on the same seeds as the path finder, so we get an apples-to-
   apples steps/sticks comparison.

8. **Tests**
   Unit tests for the *environment* (observation shape, reward signs, `done`
   triggers, illegal-move handling) and a **save/load round-trip** test for the
   brain. We do **not** unit-test "did it learn well" — learning is stochastic;
   we test the plumbing, and judge learning from the metrics/benchmark.

9. **Dependency**
   **PyTorch (CPU build)** — the standard, reliable library for this. It's a
   biggish install (a few hundred MB) but removes a huge amount of error-prone
   hand-written math. (Alternative if you'd rather avoid the dependency: hand-roll
   a tiny network in NumPy. More transparent, more code, easier to get subtly
   wrong. My recommendation is PyTorch for reliability, since you can't easily
   sanity-check the math from your side.)

---

## 5. Build plan (phased, each phase is independently checkable)

**Phase 1 — Environment + tests.** Build the `reset()`/`step()` wrapper and its
tests. *Checkpoint you can verify:* tests pass, and a script that takes random
actions runs games end-to-end and prints rewards. No ML yet — this is just the
game made trainable.

**Phase 2 — Network + persistence + a "do-nothing" controller.** Add the network,
the save/load code (with a round-trip test), and a `NeuralController` that loads a
(random, untrained) brain and plays. *Checkpoint:* the new menu option runs in the
game and the brain saves/loads to a file. It'll play badly — that's expected.

**Phase 3 — The DQN trainer.** Implement the practice loop; train a real brain;
watch the average reward / steps improve over episodes. *Checkpoint:* a printed
learning curve that trends upward, and a saved brain file.

**Phase 4 — Evaluation + tuning.** Benchmark the trained agent against the path
finder on identical seeds; tune the reward/observation if needed. *Checkpoint:* a
results table comparing the two.

**Phase 5 — Polish + docs.** Update the README (promote "Neural Net" from
"planned" to real), document how to train and where the brain lives.

---

## 6. Saving the brain (your persistence requirement)

This is a first-class feature, not an afterthought.

- **Where:** a `models/` folder, e.g. `models/cave_in_dqn.pt`.
- **What we save:** not just the network weights, but also the **optimizer state**
  (so training can *resume* mid-progress, not just play), the **episode count and
  exploration level**, and a small **metadata block** recording the settings the
  brain was trained under (`GRID_SIZE`, `STICK_COUNT`, `ROCK_REMOVAL_COST`,
  observation format version).
- **Why the metadata matters:** a brain trained on, say, a 10×10 board with 5
  sticks won't make sense on a 15×15 board with 1 stick — the inputs/outputs no
  longer line up. On load we'll **check the metadata matches the current config**
  and refuse (with a clear message) rather than silently misbehave.
- **Two modes:**
  - *Training* loads the brain if present and **continues** improving it, saving
    periodically (so a crash or quit never loses more than the last checkpoint).
  - *Playing* loads the brain read-only and just acts.
- **Version control:** by default we'll `.gitignore` the `models/` folder
  (trained weights are generated artifacts), but you can choose to commit a
  "known-good" brain so anyone cloning the repo can play without training first.

In short: quit any time; the saved file means the next run picks up where you
left off.

---

## 7. Glossary (plain language)

- **Episode** — one full game, start to cave-in (or step cap).
- **Policy** — the agent's strategy: state → action. For us, "pick the highest
  Q-value action."
- **Q-value** — predicted total future reward of an action in a state.
- **Epsilon-greedy exploration** — during training, the agent mostly plays its
  best guess but sometimes (probability *epsilon*) acts **randomly**, so it
  discovers moves it would never have tried. *Epsilon* starts high (lots of
  random trying) and **decays** toward near-zero (mostly exploiting what it
  learned). This is how it escapes "I only do what I already know" ruts.
- **Experience replay** — instead of learning only from the most recent move, the
  agent stores past `(observation, action, reward, next observation)` tuples in a
  memory buffer and learns from **random batches** of them. This stabilizes
  learning and squeezes more out of each experience.
- **Target network** — a slowly-updated *copy* of the brain used as a stable
  reference while computing learning updates. Without it, the agent is "chasing
  its own tail" (updating toward a target that moves every step) and training can
  diverge. Standard DQN trick.
- **Weights** — the internal numbers of the network that get tuned during
  training; collectively, "the brain."

---

## 8. Decisions — resolved

1. **Training board:** `STICK_COUNT = 3`, `GRID_SIZE = 10`, `ROCK_REMOVAL_COST = 1`.
2. **Objective / reward:** the researched recipe in §3.3 — "collect sticks in as
   few steps as possible," with potential-based navigation shaping.
3. **Dependency:** PyTorch (CPU) approved (goal is to learn Python, not to
   hand-roll the math).

**Next:** Phase 1 — the environment wrapper + its tests. Pure plumbing (the game
made trainable), nothing to second-guess, verified together before any learning.
