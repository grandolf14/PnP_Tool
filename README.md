# PnP Tool 

A versatile desktop tool to manage Pen & Paper (PnP) RPG campaigns, currently designed for *Das Schwarze Auge (DSA)*. Built with PyQt5 and backed by SQLite, this tool offers deep customization for sessions, NPCs and events and offers a session screen to optimize the data access for gamemasters.

## Features

- **Session Data Access**: Create new characters, generate current wheather and surrounding and access the prepared character- event- or sessiondata.
- **NPC Management**: Create, edit and randomize characters with dynamic name and family generation.
- **Event & Session Tracking**: Keep your game world organized by linking NPCs to events and sessions.
- **Dynamic Weather System**: Season-aware weather changes with probabilistic logic.
- **In-Game Custom Calendar**: Manage time progression with the DSA-specific calendar system.
- **Draftboard Mode**: Visually connect events, notes, and characters in an interactive editor.
- **Full-Text Search**: Easily locate data using smart filters and full-text matching.
- **Auto Save/Load**: Persists session data automatically between uses.

## Installation

1. **Install Requirements**:
   Make sure Python 3, SQLite3 and PyQt5 are installed.

   ```bash
   pip install PyQt5
   ```

2. **Download/Clone the Repository**:
   ```bash
   git clone https://github.com/grandolf14/PnP_Tool
   ```
   
3. **Move to the directory and rename the "Libraries_default" folder into "Libraries"**:
   ```bash
   ren Libraries_default Libraries
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```
## Usage
- Switch between managment mode and session mode with the "start session"/"leave session" button
- In management mode search for the dataset you want to manage and update the datasets
- Use the draftbooks to display and outline plot or family tree content
- In session mode automaticly generate random NPC's, add notes with ingame wheather-, location and timestamps or generate the following day's wheather season appropriate

## Project Structure

```
- main.py               Main app execution
- AppVar.py             Centrally stored application data (i.e. paths to databases)
- DB_Access.py          Functions to access databases
- Models.py             Central save and load structure, custom dataclasses
- UI_MainWindow.py      UI for the main-window, handels main-window signals and slots
- UI_Browser.py         UI for handling data set accesses
- UI_DataViews.py       UI to view and navigate the content of datasets
- UI_DataEdits.py       UI to edit selected datasets content
- UI_Utility.py         Widgets to layout views and edits
- Libraries/            SQLite databases (Campaign, Settings, etc.)
```


## Notes

- Weather generation uses DSA-specific tables stored in the settings database.
- The custom calendar system maps DSA months to real-world equivalents.
- The session marked active will be displayed in session window.

## Known bugs
- The automatic update system fails to update from db Version 0.1 to 0.2 and from and from earlier versions to 0.3, if the sessions have stream annotations.

## Author

Created by Fiete Jantsch

## License

Apache License
