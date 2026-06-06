# Lesson 10 — Neural networks and DQN

## Goal

Understand what a **neural network** actually is, what a **Q-value** means, and how
the **DQN** training loop turns a random network into an agent that plays well.

## Where it lives

- `src/ai/learning/network.py` — the network ("the brain").
- `src/ai/learning/replay_buffer.py` — the agent's memory.
- `src/ai/learning/trainer.py` — the learning loop.
- `src/ai/learning/storage.py` — saving/loading the brain.

## A neural network is a big adjustable function

Strip away the mystique: a neural network is a function made of lots of
multiplications and additions, controlled by a big collection of numbers called
**weights**. Numbers go in, numbers come out, and by tuning the weights you change
what outputs you get for a given input. "Training" just means **adjusting the
weights until the outputs are useful.**

Open `src/ai/learning/network.py`:

```python
self.layers = nn.Sequential(
    nn.Linear(input_size, hidden_size),   # 302 numbers in -> 128
    nn.ReLU(),
    nn.Linear(hidden_size, hidden_size),  # 128 -> 128
    nn.ReLU(),
    nn.Linear(hidden_size, num_actions),  # 128 -> 5 numbers out
)
```

- `nn.Linear` is one layer of "multiply by weights and add" — the adjustable part.
- `nn.ReLU` is a tiny rule between layers (`keep positives, zero out negatives`)
  that lets the network learn curvy, non-trivial patterns instead of only straight
  lines.
- In goes the 302-number observation; out come **5 numbers, one per action.**

`PyTorch` (the `nn` library) handles the calculus of adjusting the weights for us —
which is exactly why we use it instead of doing the math by hand.

## What the 5 output numbers mean: Q-values

Each output is a **Q-value**: the network's estimate of *"if I take this action now
and then keep playing well, how much total reward should I expect?"* If those
estimates are good, playing is trivial — **take the action with the highest
Q-value.** That's the whole strategy.

The agent doesn't know the true Q-values; it *learns* them. That's what DQN (Deep
Q-Network) does.

## The three ideas that make DQN work

Open `src/ai/learning/trainer.py`. The training loop has three standard ingredients.

### 1. Exploration vs. exploitation (epsilon-greedy)

If the agent only ever does what it currently thinks is best, it never discovers
anything better. So early in training it acts **randomly** a lot; over time it
shifts to acting on what it has learned. The dial is `epsilon` (probability of a
random action), which starts near 1.0 and decays toward ~0.05:

```python
def select_action(network, observation, epsilon):
    if random.random() < epsilon:
        return random.randrange(NUM_ACTIONS)   # explore
    ...
    return int(q_values.argmax(dim=1).item())  # exploit best guess
```

### 2. Memory (experience replay)

Instead of learning only from its latest move, the agent stores every experience
and learns from **random batches** of past ones. See `replay_buffer.py`. This
reuses data and breaks the strong correlation between consecutive moves, which
makes learning far more stable.

### 3. A stable target (target network)

To improve its Q-value guesses, the network compares them against a target — but if
that target is computed by the *same* network that's constantly changing, training
chases its own tail and can spiral. DQN keeps a **slow-moving copy** of the network
to compute targets, refreshed only occasionally. Look at `learn_step`:

```python
predicted_q = online(observations).gather(1, actions).squeeze(1)
with torch.no_grad():
    best_next_q = target(next_observations).max(dim=1).values
    td_target = rewards + gamma * best_next_q * (1.0 - dones)
loss = nn.functional.mse_loss(predicted_q, td_target)
```

In words: "What did I predict for the action I took? What *should* it have been —
the reward plus the best value available next (from the stable target network)?
Nudge the weights to close that gap." `gamma` (0.99) is how much future reward
counts; `(1 - dones)` zeroes out the future when the game ended. That nudge,
repeated millions of times, is learning.

## Saving the brain

A trained brain is just its weights, and we don't want to lose them when the
program closes. `storage.py` writes them to `models/cave_in_dqn.pt` along with
enough state to *resume* training later, plus metadata (board size, etc.) so a
brain is never loaded against a mismatched game. Training checkpoints periodically,
so quitting never loses more than the last save.

## Train one yourself

```bash
make install-ml
make train ARGS="--episodes 2000"
```

Watch the printed `avg reward` and `avg sticks` climb as it learns. Then play it:
run the game and choose **Neural Net**. The brain you trained now drives the player
through the same `AIInterface` door from Lesson 8.

## Try it yourself

1. Do a short run: `make train ARGS="--episodes 50 --min-replay 200"`. You won't get
   a master, but you'll see the numbers move. That motion *is* learning.
2. In `network.py`, change `hidden_size` to `256`. Bigger brain — does it learn
   better, slower, the same? (Now you're doing real experiments — Lesson 11.)
3. Re-read `select_action`. Why must `epsilon` start high? What would happen if it
   were `0.0` from the very first episode? (Hint: it would only ever repeat its
   first random guesses.)

## Takeaways

- A **neural network** is an adjustable number-machine; **weights** are what get
  tuned; **training** = tuning them.
- The network outputs a **Q-value** per action; play = pick the highest.
- **DQN** = epsilon-greedy exploration + experience replay + a target network.
- The **brain is just weights**, saved to disk so progress persists.

Next: [Lesson 11 — Running experiments](11_RUNNING_EXPERIMENTS_LESSON.md).
