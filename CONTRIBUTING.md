# Contributing to Axion CLI ⚛️

Thank you for considering contributing to Axion! It's people like you that make Axion such a great tool.

We welcome contributions of all kinds, from bug reports and documentation to new features and providers.

## 🚀 How to Get Started

### 1. Build From Source

```bash
# Clone the repository
git clone https://github.com/iam-ssrivastav/axion-cli.git
cd axion-cli

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e .
```

### 2. Make Your Changes

* Follow the existing code style (we use [Black](https://github.com/psf/black) and [isort](https://github.com/PyCQA/isort)).
* Add type hints to all new functions.
* Use `rich` for any new terminal UI components.

## 🛠️ Project Architecture

Axion is built with a modular design:

* **`axion/cli.py`**: The heart of the app — manages the conversation loop.
* **`axion/providers/`**: Where LLM logic lives. Want to add Anthropic? Add `anthropic.py` here!
* **`axion/tools/`**: Where the AI's capabilities live. Every tool is a simple class inheriting from `BaseTool`.
* **`axion/ui/`**: All the beautiful terminal rendering logic.

## ✅ Contribution Guidelines

1. **Keep it Free**: Axion's mission is to be a free alternative. Prioritize local LLMs (Ollama) and free-tier APIs.
2. **Safety First**: Never add a tool that modifies the filesystem without using the `ask_permission` UI method.
3. **Be Respectful**: Follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📬 Submitting Changes

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/my-new-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/my-new-feature`).
5. Open a Pull Request on GitHub.

## 💡 Ideas for Contribution

* 🔌 **New Providers**: Anthropic, Mistral, Perplexity.
* 🛠️ **New Tools**: Git status/commit, Web searching, System health checks.
* 🎨 **UI Themes**: Add more vibrant color palettes to `themes.py`.
* 🧪 **Testing**: Help us reach 100% test coverage!

---

**Happy Coding!** 🚀
