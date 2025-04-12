# PnP Tool 🎲

A versatile desktop tool to manage Pen & Paper (PnP) RPG campaigns—designed especially for *Das Schwarze Auge (DSA)*. Built with PyQt5 and backed by SQLite, this tool offers deep customization and automation for sessions, NPCs, events, and much more.

## 🔧 Features

- 🧙‍♂️ **NPC Management**: Create, edit, and randomize characters with dynamic name and family generation.
- 🗓️ **Event & Session Tracking**: Keep your game world organized by linking NPCs to events and sessions.
- 🌤️ **Dynamic Weather System**: Season-aware weather changes with probabilistic logic.
- 📆 **In-Game Custom Calendar**: Manage time progression with the DSA-specific calendar system.
- 🧠 **Draftboard Mode**: Visually connect events, notes, and characters in an interactive scene editor.
- 🔍 **Full-Text Search**: Easily locate data using smart filters and full-text matching.
- 💾 **Auto Save/Load**: Persists session data automatically between uses.

## 📁 Project Structure

```
PnP_Tool/
├── main.py               # Main GUI and app logic
├── DataHandler.py        # Load/save state functionality
├── Executable.py         # Backend: data models, factories, DB interaction
├── Libraries/            # SQLite databases (Campaign, Settings, etc.)
└── README.md             # This file
```

## 🚀 Getting Started

### Requirements

- Python 3.8+
- PyQt5
- SQLite3 (comes with Python)

### Installation

```bash
git clone https://github.com/grandolf14/PnP_Tool.git
cd PnP_Tool
pip install -r requirements.txt
```

### Running the Tool

```bash
python main.py
```

## 📸 Screenshots

_Coming soon..._

## 📝 Notes

- Weather generation uses DSA-specific tables stored in the settings database.
- The custom calendar system maps fantasy months to real-world equivalents.
- A session can be marked as "active" and will persist across launches.

## ⚒️ To-Do

- [ ] Finalize in-text hyperlink handling inside custom `QTextEdit`
- [ ] Add gender-based logic to NPC generation
- [ ] Enhance Draftboard UI interactions

## 🧑‍💻 Author

Developed by [grandolf14](https://github.com/grandolf14)

## 📜 License

MIT License — feel free to fork, contribute, and adapt!
