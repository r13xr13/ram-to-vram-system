# Contributing

Thank you for your interest in contributing to the RAM-to-VRAM System!

## How to Contribute

### Reporting Bugs

- Check existing issues first
- Include system specs (CPU, RAM, GPU, OS)
- Include Ollama version (`ollama --version`)
- Include relevant logs (`journalctl -u ollama -f`)
- Steps to reproduce

### Suggesting Features

- Describe the problem you're solving
- Explain your proposed solution
- Note any hardware requirements

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Test your changes on your system
4. Commit with clear messages
5. Open a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ram-to-vram-system.git
cd ram-to-vram-system

# Install dependencies
pip install psutil

# Test scripts
python3 memory_optimizer.py
bash system-status.sh
python3 conversation_coordinator.py
```

## Code Style

- Python: Follow PEP 8, use type hints where practical
- Shell: Use `set -e`, quote variables, comment complex logic
- Keep scripts self-contained and portable

## Testing

Before submitting a PR, verify:
- [ ] `memory_optimizer.py` runs without errors
- [ ] `system-status.sh` produces output
- [ ] `conversation_coordinator.py` test mode works
- [ ] Model creation scripts generate valid Modelfiles

## License

By contributing, you agree your contributions will be licensed under the MIT License.
