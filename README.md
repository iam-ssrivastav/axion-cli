<div align="center">

# ⚛️ Axion CLI

### **The Free, Open-Source AI Coding Assistant for your Terminal**

[![GitHub Stars](https://img.shields.io/github/stars/iam-ssrivastav/axion-cli?style=for-the-badge&color=purple)](https://github.com/iam-ssrivastav/axion-cli/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-green.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg?style=for-the-badge)](CONTRIBUTING.md)

**Stop paying for AI coding assistants. Run them for free, locally, on your own hardware.**

[Installation](#-installation) • [Quick Start](#-quick-start) • [Features](#-features) • [Configuration](#-configuration) • [Contributing](#-contributing)

---

</div>

## ⚛️ What is Axion?

Axion is a powerful, terminal-based AI coding assistant designed to give individuals and teams the power of **Claude Code** without the subscription fees. It connects natively to local LLMs (via **Ollama**) or free-tier APIs (like **Google Gemini** or **Groq**) to help you write, edit, and understand code in real-time.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Local-First** | Pull and run any model from Ollama (Llama 3, Qwen, DeepSeek) for 100% free, private usage. |
| 🛠️ **Tool-Equipped** | Can read, write, and surgically edit files (`edit_file` with search-and-replace). |
| 🐚 **Terminal Power** | Execute shell commands directly and capture their output for debugging. |
| 🎨 **Rich UI** | Beautiful markdown rendering, syntax highlighting, and progress indicators. |
| 🔒 **Safety Built-in** | Every destructive operation requires explicit user permission. |
| ⚡ **Blazing Fast** | Optimized for zero-latency streaming on your local GPU. |

## 🛠️ Tools at your Command

Axion isn't just a chat bot; it's an **agent** that can:
- 📖 **Read File**: Analyzes existing code to provide context-aware help.
- ✍️ **Write File**: Generates entire new modules or files from scratch.
- ✂️ **Edit File**: Performs surgical edits using a specialized search-and-replace algorithm to minimize mistakes.
- 💻 **Run Command**: Compiles code, runs tests, or manages your environment.
- 🔍 **Search Code**: Uses lightning-fast search to find exactly what you're looking for.
- 📁 **List Directory**: Explores your codebase structure automatically.

## 🚀 Installation

### 1. Requirements
- Python 3.9 or higher
- [Ollama](https://ollama.ai/) installed and running (for local usage)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/iam-ssrivastav/axion-cli.git
cd axion-cli

# Install locally
pip install -e .
```

## ⌨️ Quick Start

### Start Chatting
Just type `axion` anywhere in your terminal to start a session in your current directory.

```bash
axion
```

### Configure your Engine
Don't worry about editing YAML files. Use the built-in config commands:

```bash
# Set your engine to Ollama
axion config set provider ollama

# Set your model (e.g., Llama 3.1)
axion config set model llama3.1:8b

# Using Gemini? Set your key
export GEMINI_API_KEY="your-key-here"
axion config set provider gemini
```

## 📜 Commands

| Command | Action |
|---------|--------|
| `/help` | List all available slash commands |
| `/config` | View or change your AI settings |
| `/clear` | Start a fresh conversation context |
| `/model <name>`| Hot-swap the model mid-conversation |
| `/exit` | Safely end the session |

## 🤝 Contributing

We love forks! 🍴 Whether it's adding a new provider like Anthropic or building a tool to deploy to AWS, we welcome all PRs. 

Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

## ⭐ Support the Project

If Axion helps you code faster and save money, please **star the repo** and share it with your friends!

---

<div align="center">
Built with ❤️ for the Open Source Community.
</div>
