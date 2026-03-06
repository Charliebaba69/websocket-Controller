
🚀 Scoutbot Automation Dashboard
Scoutbot is a high-performance, WebSocket-based control center designed to manage and broadcast automation scripts to multiple robotic or software "bots" simultaneously. Built with Python and PyQt6, it offers a professional "Postman-style" experience for industrial and testing environments.
✨ Key Features
Parallel Broadcasting: Send complex JSON payloads to multiple IP addresses concurrently using asyncio and websockets.
Postman-Style Collections: Organize your automation scripts into folders and sub-folders. Save, edit, and export them easily.
Dynamic Device Management: Add, edit, or delete devices (Name/IP/Port) via the UI—no hardcoded configurations.
Execution History: A persistent log of every command sent, including timestamps and device-specific responses.
Auto-Format JSON: Integrated "Beautify" engine to validate and indent complex nested JSON structures.
Zero-Install Portable: Can be compiled into a single .exe that runs without Python or Admin rights.

🛠️ Installation & Setup
Prerequisites
Python 3.8 or higher
Pip (Python package manager)
Quick Start
Clone the repository:
Bash
git clone https://github.com/yourusername/scoutbot-ui.git
cd scoutbot-ui




Create and activate a virtual environment:
Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate




Install dependencies:
Bash
pip install PyQt6 qasync websockets




Run the application:
Bash
python scoutbot_main.py





📦 Portable EXE Build
To generate a standalone .exe for Windows that does not require Python to be installed:
Install PyInstaller: pip install pyinstaller
Run the build command:
Bash
pyinstaller --noconsole --onefile --clean scoutbot_main.py




Find your portable app in the dist/ folder.

🖥️ Usage Guide
1. Registering Devices
Navigate to the User Input tab. Enter a unique name and the IP/Port of your WebSocket-enabled bot. Click "Add Device."
2. Organizing Scripts
In the Collections tab, right-click a folder to save your current editor script. You can import existing JSON collections to quickly populate your library.
3. Broadcasting
Check the boxes for the devices you wish to target in the Devices table. Hit "BROADCAST JOURNEY" to fire the script to all selected targets at once.

🛡️ Security
Local Traffic Only: No data is sent to external servers or the cloud.
No Admin Required: Does not modify system registry or protected files.
Plaintext Configs: Saved data is stored in scoutbot_data.json for easy auditing.



