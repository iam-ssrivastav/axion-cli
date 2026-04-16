<div align="center">

# ⚛ Axion CLI

### Free, Open-Source AI Coding Assistant for Your Terminal

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

*Like Claude Code, but free for everyone.*

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Provider** | Ollama (local/free), Google Gemini (free tier), Groq (free tier), OpenAI |
| 🛠️ **Tool Calling** | Read/write/edit files, run commands, search code |
| 🎨 **Beautiful UI** | Rich terminal output with syntax highlighting & markdown |
| 🔒 **Safety First** | Permission prompts before any destructive operation |
| 💬 **Interactive** | Multi-turn conversations with context memory |
| ⚡ **Fast** | Streaming responses for real-time output |
| 🌍 **100% Free** | Run with Ollama for completely local, free usage |

## 🚀 Quick Start

### 1. Install Axion

```bash
# Clone the repo
git clone https://github.com/your-username/axion-cli.git
cd axion-cli

# Install with pip
pip install -e .
```

### 2. Choose Your LLM Provider

#### Option A: Ollama (100% Free, Local) ⭐ Recommended

```bash
# Install Ollama
brew install ollama    # macOS
# or: curl -fsSL https://ollama.ai/install.sh | sh  (Linux)

# Start Ollama & pull a model
ollama serve
ollama pull llama3.1

# Run Axion
axion
```

#### Option B: Google Gemini (Free Tier)

```bash
# Get your free API key at https://ai.google.dev/
export GEMINI_API_KEY="your-key-here"

# Run with Gemini
axion -p gemini
```

#### Option C: Groq (Free Tier, Super Fast)

```bash
# Get your free API key at https://console.groq.com/
export GROQ_API_KEY="your-key-here"

# Run with Groq
axion -p groq
```

## 📖 Usage

### Interactive Mode

```bash
# Start an interactive session
axion

# With specific provider and model
axion -p gemini -m gemini-2.0-flash
axion -p ollama -m qwen2.5-coder
axion -p groq -m llama-3.1-70b-versatile
```

### One-Shot Mode

```bash
# Ask a quick question
axion "explain what this project does"

# Fix a specific file
axion "fix the bug in src/main.py"
```

### Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/config` | View current configuration |
| `/clear` | Clear conversation history |
| `/model <name>` | Switch AI model |
| `/provider <name>` | Switch LLM provider |
| `/theme <dark\|light>` | Change color theme |
| `/exit` | Exit Axion |

## 🛠️ Available Tools

Axion has built-in tools that the AI can use:

| Tool | Description | Needs Permission? |
|------|-------------|:-:|
| `read_file` | Read file contents | ❌ |
| `write_file` | Create/overwrite files | ✅ |
| `edit_file` | Surgical search-and-replace edits | ✅ |
| `run_command` | Execute shell commands | ✅ |
| `search_files` | Grep/ripgrep code search | ❌ |
| `list_directory` | List directory contents | ❌ |

## ⚙️ Configuration

Config is stored at `~/.axion/config.yaml`:

```yaml
provider: ollama
model: llama3.1
temperature: 0.1
max_tokens: 8192
theme: dark
auto_approve_reads: true
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `AXION_API_KEY` | Universal API key (works for any provider) |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GROQ_API_KEY` | Groq API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `AXION_DEBUG` | Set to `1` for debug output |

## 🗂️ Project Structure

```
axion-cli/
├── axion/
│   ├── __init__.py          # Package info
│   ├── __main__.py          # CLI entry point (click)
│   ├── cli.py               # Interactive session & conversation loop
│   ├── config.py            # Configuration management
│   ├── providers/
│   │   ├── base.py          # Abstract LLM provider
│   │   ├── ollama.py        # Ollama (local, free)
│   │   ├── gemini.py        # Google Gemini
│   │   └── openai_compat.py # OpenAI/Groq/Together/etc.
│   ├── tools/
│   │   ├── base.py          # Tool interface & registry
│   │   ├── file_read.py     # Read files
│   │   ├── file_write.py    # Write/create files
│   │   ├── file_edit.py     # Edit files (search & replace)
│   │   ├── command.py       # Execute shell commands
│   │   ├── search.py        # Grep/ripgrep search
│   │   └── list_dir.py      # Directory listing
│   └── ui/
│       ├── terminal.py      # Rich terminal rendering
│       └── themes.py        # Color themes
├── pyproject.toml           # Project config & dependencies
├── requirements.txt
├── LICENSE                  # MIT License
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/awesome-feature`
3. Commit your changes: `git commit -m "Add awesome feature"`
4. Push to the branch: `git push origin feature/awesome-feature`
5. Open a Pull Request

### Ideas for Contributions

- 🔌 New LLM providers (Anthropic, Mistral, etc.)
- 🛠️ New tools (git integration, web search, image generation)
- 🎨 New themes
- 📝 Better documentation
- 🧪 Tests
- 🌐 Web UI companion

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Free for personal, commercial, and open-source use.

---

<div align="center">

**Built with ❤️ by the open source community**

⭐ Star this repo if you find it useful!

</div>
