# Adaptive Cognitive Framework

The Adaptive Cognitive Framework is a lightweight Python package that showcases
an experimental self-monitoring agent. It demonstrates how separate
introspection, adaptation, and reflection loops can collaborate to process
arbitrary context and report on internal state.

## Why this project?

The original version offered a minimal skeleton. This revision expands the
simulation to provide richer metrics, structured adaptation results, and more
practical documentation. The framework now:

- Tracks detailed meta-context information (recent context types, sizes, and
  adaptation history).
- Produces structured adaptation results with type-specific insights.
- Generates reflective summaries that surface recent behaviour and emotional
  valence trends.
- Includes a CLI-friendly simulation runner and automated tests to validate the
  basic contract of the agent.

## Project layout

```
.
├── adaptation.py      # Adaptive loop producing structured results
├── core.py            # High-level `AdaptiveAgent` orchestrating modules
├── introspection.py   # Introspective state tracking history and metrics
├── reflection.py      # Reflective processor producing narrative summaries
├── simulation.py      # Demo runner for the adaptive agent
├── tests/             # Lightweight pytest-based test suite
└── requirements.txt   # Python dependencies
```

## Getting started

### 1. Set up a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\\Scripts\\activate`
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the demo simulation

```bash
python -m simulation
```

The script prints each step processed by the agent, including the adaptation
summary, the transformed context, and the introspection report for that moment
in time.

### 4. Execute the tests

```bash
pytest
```

## Extending the framework

- Add new adaptation strategies by extending `AdaptiveLoop._adapt_context` and
  logging human-readable summaries via `IntrospectiveState.record_adaptation`.
- Experiment with alternative reflection styles by modifying
  `ReflectiveProcessor.reflect`.
- Integrate external data sources by feeding structured inputs to
  `AdaptiveAgent.process` or by creating new entry points that leverage the
  `run_demo` utility in `simulation.py`.

## License

This project is released under the MIT License. See [`LICENSE`](LICENSE) for
more information.
