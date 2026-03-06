import sys
import asyncio
import json
import time
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QCheckBox, QLabel, QTabWidget,
                             QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox, QMenu, QFileDialog, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction
from qasync import QEventLoop, asyncSlot
import websockets

class ScoutbotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scoutbot Automation Dashboard Pro")
        self.resize(1300, 900)
        
        self.active_connections = {}  
        self.devices_list = []        
        self.collections = {"Automation Journeys": {}} 
        
        self.setup_ui()
        self.load_all_data()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # --- LEFT PANEL: DEVICES ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("## Device Management"))
        
        self.btn_send_all = QPushButton("🚀 BROADCAST JOURNEY")
        self.btn_send_all.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 15px;")
        self.btn_send_all.clicked.connect(self.on_send_all_clicked)
        left_layout.addWidget(self.btn_send_all)

        self.device_table = QTableWidget(0, 4)
        self.device_table.setHorizontalHeaderLabels(["Select", "Name", "Address", "Actions"])
        self.device_table.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.device_table)
        main_layout.addLayout(left_layout, 2)

        # --- RIGHT PANEL: TABS ---
        right_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        # Tab 1: User Input (Add/Edit Devices)
        input_tab = QWidget()
        input_lyt = QVBoxLayout(input_tab)
        self.edit_name = QLineEdit(); self.edit_name.setPlaceholderText("Device Name")
        self.edit_ip = QLineEdit(); self.edit_ip.setPlaceholderText("IP Address")
        self.edit_port = QLineEdit(); self.edit_port.setPlaceholderText("Port (Default 8888)")
        btn_add = QPushButton("➕ Add Device")
        btn_add.clicked.connect(self.add_new_device)
        input_lyt.addWidget(QLabel("### Register New Bot"))
        input_lyt.addWidget(self.edit_name); input_lyt.addWidget(self.edit_ip); input_lyt.addWidget(self.edit_port)
        input_lyt.addWidget(btn_add)
        input_lyt.addStretch()
        self.tab_widget.addTab(input_tab, "User Input")

        # Tab 2: Script Editor (With Auto-Format)
        script_tab = QWidget()
        script_lyt = QVBoxLayout(script_tab)
        self.script_editor = QTextEdit()
        self.script_editor.setFont(QFont("Courier New", 10))
        self.script_editor.setPlaceholderText("Paste ScoutBot_StartJourneyWithData JSON here...")
        
        btn_format = QPushButton("✨ Auto-Format & Validate")
        btn_format.clicked.connect(self.format_json_editor)
        
        script_lyt.addWidget(QLabel("Journey Script:"))
        script_lyt.addWidget(self.script_editor)
        script_lyt.addWidget(btn_format)
        self.tab_widget.addTab(script_tab, "Script")

        # Tab 3: Collections
        coll_tab = QWidget()
        coll_lyt = QVBoxLayout(coll_tab)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Journey Collections")
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_menu)
        self.tree.itemDoubleClicked.connect(self.load_from_collection)
        coll_lyt.addWidget(self.tree)
        self.tab_widget.addTab(coll_tab, "Collections")

        # Tab 4: History
        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(["Time", "Device", "Journey Name", "Status"])
        self.tab_widget.addTab(self.history_table, "History")

        right_layout.addWidget(self.tab_widget, 3)

        # Log Window
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background-color: #1e1e1e; color: #00ff00;")
        right_layout.addWidget(QLabel("### System Logs"))
        right_layout.addWidget(self.log_box, 1)

        main_layout.addLayout(right_layout, 3)

    # --- LOGIC: JSON FORMATTING ---
    def format_json_editor(self):
        try:
            raw = self.script_editor.toPlainText().strip()
            # Handle the ScoutBot header if present
            header = ""
            if raw.startswith("ScoutBot_StartJourneyWithData"):
                header = "ScoutBot_StartJourneyWithData "
                raw = raw.replace("ScoutBot_StartJourneyWithData", "").strip()
            
            data = json.loads(raw)
            self.script_editor.setText(f"{header}{json.dumps(data, indent=4)}")
            self.write_log("Journey data formatted.")
        except Exception as e:
            QMessageBox.warning(self, "JSON Error", f"Could not format: {e}")

    # --- LOGIC: DEVICE MGMT ---
    def add_new_device(self):
        if self.edit_name.text() and self.edit_ip.text():
            self.devices_list.append({
                "name": self.edit_name.text(), 
                "ip": self.edit_ip.text(), 
                "port": self.edit_port.text() or "8888"
            })
            self.refresh_device_table(); self.save_all_data()
            self.edit_name.clear(); self.edit_ip.clear(); self.edit_port.clear()

    def refresh_device_table(self):
        self.device_table.setRowCount(0)
        for i, dev in enumerate(self.devices_list):
            self.device_table.insertRow(i)
            addr = f"{dev['ip']}:{dev['port']}"
            chk = QCheckBox("Offline"); self.device_table.setCellWidget(i, 0, chk)
            self.device_table.setItem(i, 1, QTableWidgetItem(dev['name']))
            self.device_table.setItem(i, 2, QTableWidgetItem(addr))
            
            btn_box = QWidget(); lyt = QHBoxLayout(btn_box); lyt.setContentsMargins(0,0,0,0)
            c_btn = QPushButton("Conn"); c_btn.clicked.connect(lambda _, a=addr, r=i: self.connect_device(a, r))
            d_btn = QPushButton("Disc"); d_btn.clicked.connect(lambda _, a=addr, r=i: self.disconnect_device(a, r))
            del_btn = QPushButton("X"); del_btn.setStyleSheet("color:red"); del_btn.clicked.connect(lambda _, idx=i: self.delete_device(idx))
            for b in [c_btn, d_btn, del_btn]: lyt.addWidget(b)
            self.device_table.setCellWidget(i, 3, btn_box)

    def delete_device(self, idx):
        self.devices_list.pop(idx)
        self.refresh_device_table(); self.save_all_data()

    @asyncSlot()
    async def connect_device(self, addr, row):
        try:
            ws = await asyncio.wait_for(websockets.connect(f"ws://{addr}"), timeout=3.0)
            self.active_connections[addr] = ws
            self.device_table.cellWidget(row, 0).setText("Online")
            self.device_table.cellWidget(row, 0).setChecked(True)
            self.write_log(f"Connected to {addr}")
        except Exception as e: self.write_log(f"Fail {addr}: {e}")

    def disconnect_device(self, addr, row):
        if addr in self.active_connections:
            asyncio.create_task(self.active_connections[addr].close())
            del self.active_connections[addr]
        self.device_table.cellWidget(row, 0).setText("Offline")
        self.device_table.cellWidget(row, 0).setChecked(False)

    @asyncSlot()
    async def on_send_all_clicked(self):
        raw_script = self.script_editor.toPlainText().strip()
        tasks = []
        for i in range(self.device_table.rowCount()):
            if self.device_table.cellWidget(i, 0).isChecked():
                tasks.append(self.send_to_device(self.device_table.item(i, 1).text(), self.device_table.item(i, 2).text(), raw_script))
        await asyncio.gather(*tasks)

    async def send_to_device(self, name, addr, script):
        if addr in self.active_connections:
            try:
                await self.active_connections[addr].send(script)
                res = await asyncio.wait_for(self.active_connections[addr].recv(), timeout=10.0)
                self.write_log(f"[{name}] Journey Sent.")
                self.add_history(name, script, res)
            except Exception as e: self.write_log(f"[{name}] Journey Error: {e}")

    # --- LOGIC: COLLECTIONS & HISTORY ---
    def add_history(self, dev, script, res):
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        self.history_table.setItem(row, 0, QTableWidgetItem(time.strftime("%H:%M:%S")))
        self.history_table.setItem(row, 1, QTableWidgetItem(dev))
        # Extract testName from script for history display
        try:
            clean_json = script.replace("ScoutBot_StartJourneyWithData", "").strip()
            data = json.loads(clean_json)
            self.history_table.setItem(row, 2, QTableWidgetItem(data.get("testName", "Unknown")))
        except: self.history_table.setItem(row, 2, QTableWidgetItem("Manual Script"))
        self.history_table.setItem(row, 3, QTableWidgetItem(str(res)))

    def show_tree_menu(self, pos):
        item = self.tree.itemAt(pos)
        if item and not item.parent():
            menu = QMenu()
            act = QAction("💾 Save Journey to this Folder", self)
            act.triggered.connect(lambda: self.save_to_folder(item.text(0)))
            menu.addAction(act); menu.exec(self.tree.viewport().mapToGlobal(pos))

    def save_to_folder(self, folder):
        name, ok = QInputDialog.getText(self, "Save", "Journey Name:")
        if ok and name:
            self.collections[folder][name] = self.script_editor.toPlainText()
            self.refresh_tree(); self.save_all_data()

    def load_from_collection(self, item):
        if item.parent():
            data = self.collections[item.parent().text(0)][item.text(0)]
            self.script_editor.setText(data)
            self.tab_widget.setCurrentIndex(1)

    def refresh_tree(self):
        self.tree.clear()
        for f, s in self.collections.items():
            node = QTreeWidgetItem(self.tree, [f])
            for name in s: QTreeWidgetItem(node, [name])
            node.setExpanded(True)

    def write_log(self, t): self.log_box.append(f"[{time.strftime('%H:%M:%S')}] {t}")

    def save_all_data(self):
        data = {"devices": self.devices_list, "collections": self.collections}
        with open("scoutbot_data.json", "w") as f: json.dump(data, f)

    def load_all_data(self):
        if os.path.exists("scoutbot_data.json"):
            with open("scoutbot_data.json", "r") as f:
                d = json.load(f); self.devices_list = d.get("devices", []); self.collections = d.get("collections", {})
            self.refresh_device_table(); self.refresh_tree()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    win = ScoutbotApp(); win.show()
    with loop: loop.run_forever()