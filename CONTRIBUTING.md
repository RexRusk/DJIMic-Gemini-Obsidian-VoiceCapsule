# Contributing to Voice Capsule

Thank you for your interest in contributing to Voice Capsule!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone repository
git clone https://github.com/bluehawana/DjiMic3-Gemini-Obsidian-VoiceCapsule.git
cd DjiMic3-Gemini-Obsidian-VoiceCapsule

# Install dependencies
pip install -r scripts/python/requirements.txt
pip install -r web-app/requirements.txt

# Setup environment
cp configs/.env.template configs/.env
# Edit configs/.env with your credentials

# Run tests
python -m pytest tests/
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

## Reporting Issues

- Use GitHub Issues
- Provide clear description
- Include steps to reproduce
- Add relevant logs/screenshots

## Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Describe the use case
- Explain why it's valuable

## Questions?

Open a discussion on GitHub or reach out to the maintainers.
