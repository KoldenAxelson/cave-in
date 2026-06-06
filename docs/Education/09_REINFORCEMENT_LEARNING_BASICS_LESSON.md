# Lesson 9 — Reinforcement learning basics

## Goal

Understand the core idea of **reinforcement learning (RL)** — learning by trial,
error, and reward — and see how this project turns the game into something an agent
can learn on.

## Where it lives

- `src/ai/learning/environment.py` — the `CaveInEnv` training environment.
- `docs/ML_CONTROLLER_PLAN.md` — the design doc, if you want the deeper version.

> New dependency from here on: the ML code uses NumPy and PyTorch. Install with
> `make install-ml` (or `pip install -r requirements-ml.txt`).

## The concept: learning the way a dog learns tricks

You don't teach a dog to sit by explaining the rules. You let it try things, and
when it happens to sit, you give a treat. Over time it does more of what earns
treats. That's reinforcement learning. There's no rulebook — just **actions** and
**rewards**, and the learner figures out a strategy that earns the most reward.

RL has four nouns. Memorize these; the rest of the ML lessons are built from them:

- **Environment** — the game (the world the agent acts in).
- **Observation** — what the agent gets to *see* of that world, as numbers.
- **Action** — what it can *do* this turn.
- **Reward** — a number after each action saying how good that action was.

The agent observes, picks an action, the environment responds with a reward and the
next observation, and the loop repeats. One full game is an **episode**. Play
thousands of episodes, chase the reward, and a strategy emerges.

Notice the contrast with Lesson 7's path finder: there we *told* the agent exactly
how to navigate. Here we tell it *nothing* about how to play — only what counts as
good (the reward) — and let it discover the "how" itself.

## Turning a game into a learnable environment

RL tools expect the environment to offer two functions:

- `reset()` — start a fresh episode, return the first observation.
- `step(action)` — apply one action, return `(observation, reward, done)`.

Open `src/ai/learning/environment.py`. The `CaveInEnv` class wraps our game in
exactly that shape. Let's look at the three design choices that *are* the learning
problem.

### Observation — what the agent sees

```python
OBSERVATION_SIZE = 3 * GRID_SIZE * GRID_SIZE + 2
```

The board is encoded as three 10×10 grids of 0s and 1s — one marking the player,
one the rocks, one the sticks — plus two extra numbers (sticks held, how full the
board is). 302 numbers total. That's the board expressed as something math can
chew on. (This is the same trick used to feed video-game screens to AIs: turn the
picture into stacked grids of numbers.)

### Action — what it can do

Five choices: move up, right, down, left, or **use** the faced cell. The agent only
ever outputs one of these per turn. Crucially, it gets the **raw** board and emits
**raw** moves — no pathfinding, no shortcuts. It has to learn navigation from
scratch.

### Reward — how we define "good"

This is the most important design decision in all of RL, because the reward
*defines what the agent will try to do*. Read `step()` in the environment. The
recipe (researched, see the plan doc) is:

- **+1** for collecting a stick — the goal, and the biggest term.
- **−0.02** per step — a gentle "hurry up" so it prefers shorter routes.
- **−0.1** for an illegal move (into a wall) — learn the rules fast.
- a small **shaping** nudge toward the nearest stick to speed up early learning.

One subtle lesson baked in here: if you made *every* reward negative, the agent
would learn to end the game as fast as possible just to stop the penalties — and
ignore sticks entirely. The desired behavior must be clearly, dominantly
*positive*. Reward design is where RL projects most often succeed or fail.

## See it run (badly, for now)

You can drive the environment with totally random actions:

```python
import random
from src.ai.learning.environment import CaveInEnv, NUM_ACTIONS

env = CaveInEnv(stick_count=3)
obs = env.reset()
done = False
total = 0.0
while not done:
    obs, reward, done, info = env.step(random.randrange(NUM_ACTIONS))
    total += reward
print("random agent total reward:", total)
```

A random agent collects almost nothing and racks up step penalties, so its reward
is badly negative. That's our baseline. Lesson 10 builds the brain that turns
random flailing into competent play.

## Try it yourself

1. Run the random-agent snippet above a few times. Note how negative the reward is
   — that number is the bar the trained agent has to clear.
2. In `environment.py`, find the reward weights. Predict what would happen if you
   bumped the stick reward to **+10**. (More eager to collect? At what cost to
   step-efficiency?)
3. Why does the agent get the *whole board* as its observation rather than just the
   cells next to it? What could it not learn if it could only see its neighbors?

## Takeaways

- RL learns from **reward**, not rules — like training a dog with treats.
- The four nouns: **environment, observation, action, reward**.
- An environment exposes `reset()` and `step(action)`.
- The **reward function defines the goal** — design it carefully, and keep the
  desired behavior positive.

Next: [Lesson 10 — Neural networks and DQN](10_NEURAL_NETWORKS_AND_DQN_LESSON.md),
where we build the brain.
