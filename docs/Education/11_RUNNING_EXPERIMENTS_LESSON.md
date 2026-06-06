# Lesson 11 — Running experiments

## Goal

Tie everything together by learning to *measure* instead of guess: how to train,
evaluate, and benchmark agents, and how to think like a scientist about a system
that's too complex to reason about purely in your head.

## Where it lives

- `tools/train_dqn.py` — train a brain.
- `tools/evaluate_agents.py` — neural agent vs. path finder, head to head.
- `tools/benchmark_pathfinder.py` — measure step counts (and sweep settings).

## The big idea: you can't just *think* your way through ML

In the early lessons, you could often reason out what code would do. Once learning,
randomness, and 302-number observations are involved, intuition gets unreliable
fast. The professional habit is to **form a hypothesis, run a measurement, and let
the data decide** — exactly like a science experiment.

This project was actually *built* that way, and the tools are the evidence.

## Reproducibility: the foundation of measurement

A measurement you can't repeat isn't a measurement. The benchmark tools use a
**seed** — a number that makes the "random" board come out identically every run.
Same seed → same board → same result. That's what lets you compare two agents
*fairly*: put them on the very same boards.

```bash
python tools/evaluate_agents.py --seeds 50
```

This runs both the path finder and your trained neural agent across 50 identical
boards and prints how often each finished, its median step count, and how many
sticks it collected. Now "is the neural net any good?" has a number, not an
opinion.

## A worked example from this project's own history

When the team added a `STICK_VALUE` knob (how many steps the path finder treats a
rock-removal as worth), the obvious assumption was "tuning this will change how
well it plays." Instead of guessing, they swept it:

```bash
python tools/benchmark_pathfinder.py 25 --sweep 1,5,10,20
```

The result was a surprise: changing the value barely moved the step count at all.
Digging into *why* revealed something deeper about the game's mechanics that no
amount of staring at code would have shown. **The experiment overturned the
intuition** — which is the entire point of running one. (The benchmark also later
exposed that a different rule change made the AI deadlock itself — again, found by
measuring, not by guessing.)

That is the mindset this whole course is really trying to teach: code is how you
*build* the thing; experiments are how you *understand* it.

## The training → evaluation → tuning loop

Putting the ML lessons into practice is a cycle:

1. **Train** a brain: `make train ARGS="--episodes 2000"`.
2. **Evaluate** it against the path finder: `python tools/evaluate_agents.py --seeds 50`.
3. **Observe** how it actually behaves — does it dither? refuse to remove rocks?
   wander away from sticks?
4. **Adjust** one thing (a reward weight in `environment.py`, a hyperparameter in
   `trainer.py`), retrain, and re-evaluate.
5. Repeat. Change **one variable at a time** so you can attribute any difference to
   that change — the most important rule of experimenting.

## Capstone exercises

You now understand every layer of this project. Here are projects that exercise the
whole stack:

1. **Write a `RandomController`** (from Lesson 8) that implements `AIInterface` and
   moves randomly. Add it to the menu. Then add it to `evaluate_agents.py` as a
   third agent and confirm with numbers that it's worse than both others. *(Touches
   interfaces, the game wiring, and measurement.)*

2. **Reward experiment.** Form a hypothesis — e.g. "raising the per-step penalty
   will lower the trained agent's step count." Change only that weight, retrain a
   short run, evaluate, and see if the data supports your hypothesis. Write down
   what you predicted and what happened.

3. **Bigger brain.** Change `hidden_size` in `network.py` and/or add a layer. Does a
   larger network learn better, or just slower? Measure, don't assume.

4. **Change the game, then re-measure.** Bump `STICK_COUNT` to 5 and `GRID_SIZE` to
   15 in `config.py`. Re-run the benchmark and retrain. How does difficulty affect
   both the path finder and a learned agent?

## Where to go next

You've gone from "I know what a list is" to reading and modifying a complete
reinforcement-learning system. Natural next steps beyond this project:

- A short, reputable RL course or book to formalize the ideas you've met (Markov
  decision processes, Q-learning, policy gradients).
- Try a standard RL environment library (e.g. Gymnasium) — its `reset()`/`step()`
  shape will look immediately familiar, because you've already built one.
- Improve this agent: better observations, a convolutional network, or a different
  algorithm (PPO). You have the harness to measure whether your changes help.

## Takeaways

- Treat a complex system like a **science experiment**: hypothesize, measure,
  conclude.
- **Reproducible seeds** make fair comparisons possible.
- **Change one variable at a time** so results are interpretable.
- Real understanding comes from *measuring* the system, not just reading it — and
  you now have both the system and the tools to do it.

That's the course. Go break things and measure what happens.
