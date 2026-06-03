# Contributing

Thanks for your interest in improving the AI Research Assistant Pipeline! 🎉

## Getting set up

```bash
git clone https://github.com/AyushDas4890/AI-Research-Assistant-Pipeline.git
cd AI-Research-Assistant-Pipeline
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then add your keys
```

## Development workflow

1. **Fork** the repo and create a feature branch: `git checkout -b feature/my-change`
2. Make your change. Keep it focused — one logical change per PR.
3. Make sure everything still imports and compiles:
   ```bash
   python -m py_compile $(git ls-files '*.py')
   python -c "from graph.graph_builder import build_graph; build_graph()"
   ```
4. **Commit** with a clear message (see below) and open a **pull request**.

## Project layout

| Area | Where |
|---|---|
| Agents | `agents/` |
| Graph wiring | `graph/` |
| Tools (search/fetch/memory) | `tools/` |
| Memory layer | `memory/` |
| Web backend | `server.py` |
| Frontend | `web/` |

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` a new feature
- `fix:` a bug fix
- `docs:` documentation only
- `refactor:` code change that neither fixes a bug nor adds a feature
- `chore:` tooling / maintenance

## Code style

- Python: follow PEP 8, keep functions small and documented with docstrings.
- Every agent must degrade gracefully — never crash the graph on a bad URL or API error.
- Never commit secrets. `.env` is gitignored; keep it that way.

## Reporting bugs

Open an issue using the **Bug report** template and include steps to reproduce,
expected vs. actual behaviour, and your environment.
