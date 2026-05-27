import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QPushButton, 
                               QMessageBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, Signal
import threading

from sim_utils.connection import connect_to_simulator
from sim_utils.environment import build_physical_maze
from core.maze_generator import generate_maze
from core.pathfinding import find_path_lee
from core.robot_control import navigate_path

class MazeControllerGUI(QMainWindow):
    # Semnalul trimite acum un boolean (True = Succes, False = Oprit manual)
    mission_finished_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Labirint - Pioneer P3-DX")
        self.setFixedSize(480, 520) # Ușor mai lată pentru a încăpea 3 butoane
        
        self.sim = None
        self.client = None
        self.maze_logic = None
        self.path_logic = None
        self.maze_handles = [] 
        
        self.control_flags = {"paused": False, "stopped": False}
        
        self.mission_finished_signal.connect(self.on_mission_finished)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- SECȚIUNEA 1: CONEXIUNE ---
        conn_group = QGroupBox("1. Conexiune CoppeliaSim")
        conn_layout = QVBoxLayout()
        self.btn_connect = QPushButton("Conectare la Simulator")
        self.btn_connect.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        self.btn_connect.clicked.connect(self.connect_sim)
        self.lbl_status = QLabel("Status: Neconectat")
        self.lbl_status.setStyleSheet("color: red;")
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.lbl_status)
        conn_group.setLayout(conn_layout)
        main_layout.addWidget(conn_group)
        
        # --- SECȚIUNEA 2: SETĂRI LABIRINT ---
        maze_group = QGroupBox("2. Control și Parametri Labirint")
        maze_layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.spin_size = QSpinBox()
        self.spin_size.setRange(5, 41)
        self.spin_size.setSingleStep(2) 
        self.spin_size.setValue(11)
        form_layout.addRow("Dimensiune Grilă (Impar):", self.spin_size)
        
        self.spin_path_w = QDoubleSpinBox()
        self.spin_path_w.setRange(0.5, 3.0)
        self.spin_path_w.setSingleStep(0.1)
        self.spin_path_w.setValue(0.90)
        form_layout.addRow("Lățime Culoar (m):", self.spin_path_w)
        
        self.spin_wall_thick = QDoubleSpinBox()
        self.spin_wall_thick.setRange(0.02, 0.5)
        self.spin_wall_thick.setSingleStep(0.02)
        self.spin_wall_thick.setValue(0.10)
        form_layout.addRow("Grosime Perete (m):", self.spin_wall_thick)
        
        self.spin_wall_height = QDoubleSpinBox()
        self.spin_wall_height.setRange(0.1, 1.5)
        self.spin_wall_height.setSingleStep(0.1)
        self.spin_wall_height.setValue(0.40)
        form_layout.addRow("Înălțime Perete (m):", self.spin_wall_height)
        
        maze_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Generează")
        self.btn_generate.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 6px;")
        self.btn_generate.setEnabled(False) 
        self.btn_generate.clicked.connect(self.generate_and_build)
        
        self.btn_clear = QPushButton("Șterge")
        self.btn_clear.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 6px;")
        self.btn_clear.setEnabled(False) 
        self.btn_clear.clicked.connect(self.clear_maze)
        
        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(self.btn_clear)
        maze_layout.addLayout(btn_layout)
        maze_group.setLayout(maze_layout)
        main_layout.addWidget(maze_group)
        
        # --- SECȚIUNEA 3: LANSARE, PAUZĂ ȘI STOP ---
        robot_group = QGroupBox("3. Execuție")
        robot_layout = QHBoxLayout() 
        
        self.btn_launch = QPushButton("Lansează")
        self.btn_launch.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.btn_launch.setEnabled(False) 
        self.btn_launch.clicked.connect(self.launch_robot)
        
        self.btn_pause = QPushButton("Pauză")
        self.btn_pause.setStyleSheet("background-color: #FFC107; color: black; font-weight: bold; padding: 10px;")
        self.btn_pause.setEnabled(False) 
        self.btn_pause.clicked.connect(self.toggle_pause)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setStyleSheet("background-color: #E91E63; color: white; font-weight: bold; padding: 10px;")
        self.btn_stop.setEnabled(False) 
        self.btn_stop.clicked.connect(self.stop_robot)
        
        robot_layout.addWidget(self.btn_launch)
        robot_layout.addWidget(self.btn_pause)
        robot_layout.addWidget(self.btn_stop)
        
        robot_group.setLayout(robot_layout)
        main_layout.addWidget(robot_group)

    def connect_sim(self):
        self.client, self.sim = connect_to_simulator()
        if self.sim:
            self.lbl_status.setText("Status: Conectat cu succes!")
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
            self.btn_generate.setEnabled(True)
            self.btn_clear.setEnabled(True)
            QMessageBox.information(self, "Succes", "Conectat la CoppeliaSim!")
        else:
            QMessageBox.critical(self, "Eroare", "Nu s-a putut conecta.")

    def clear_maze(self):
        if not self.sim: return
        if not self.maze_handles: return
            
        for handle in self.maze_handles:
            try:
                self.sim.removeObject(handle)
            except:
                pass
        self.maze_handles.clear()
        
        self.btn_launch.setEnabled(False)
        self.btn_launch.setText("Lansează")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)

    def generate_and_build(self):
        if not self.sim: return
            
        size = self.spin_size.value()
        p_width = self.spin_path_w.value()
        w_thick = self.spin_wall_thick.value()
        w_height = self.spin_wall_height.value()
        
        self.sim.stopSimulation() 
        self.maze_logic, goal_pos = generate_maze(size, size)
        
        try:
            self.clear_maze()
            robot_handle = self.sim.getObject('/PioneerP3DX') 
            
            handles_noi = build_physical_maze(
                self.sim, self.maze_logic, robot_handle, goal_pos,
                path_width=p_width, wall_thickness=w_thick, wall_height=w_height
            )
            self.maze_handles = handles_noi if handles_noi else []
            
            start_pos = (0, 0)
            self.path_logic = find_path_lee(self.maze_logic, start_pos, goal_pos)
            
            self.btn_launch.setEnabled(True)
            self.btn_launch.setText(f"Lansează ({len(self.path_logic)} pași)")
            
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Eroare la construirea labirintului:\n{str(e)}")

    def toggle_pause(self):
        if self.control_flags["paused"]:
            self.control_flags["paused"] = False
            self.btn_pause.setText("Pauză")
            self.btn_pause.setStyleSheet("background-color: #FFC107; color: black; font-weight: bold; padding: 10px;")
        else:
            self.control_flags["paused"] = True
            self.btn_pause.setText("Continuă")
            self.btn_pause.setStyleSheet("background-color: #03A9F4; color: white; font-weight: bold; padding: 10px;")

    def stop_robot(self):
        """Oprește complet misiunea."""
        self.control_flags["stopped"] = True
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_launch.setText("Se oprește...")

    def launch_robot(self):
        if not self.path_logic: return
            
        self.btn_launch.setEnabled(False)
        self.btn_generate.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.btn_launch.setText("Pe drum...")
        
        # Resetăm ambele steaguri înainte de lansare
        self.control_flags["paused"] = False
        self.control_flags["stopped"] = False
        
        self.btn_pause.setEnabled(True)
        self.btn_pause.setText("Pauză")
        self.btn_pause.setStyleSheet("background-color: #FFC107; color: black; font-weight: bold; padding: 10px;")
        self.btn_stop.setEnabled(True)
        
        self.sim.startSimulation()
        
        w_p = self.spin_path_w.value()
        w_w = self.spin_wall_thick.value()
        
        rows, cols = len(self.maze_logic), len(self.maze_logic[0])
        total_x = (cols // 2 + 1) * w_p + (cols // 2) * w_w
        total_y = (rows // 2 + 1) * w_p + (rows // 2) * w_w
        start_x = -total_x / 2.0 + w_p / 2.0
        start_y = -total_y / 2.0 + w_p / 2.0
        
        driver_thread = threading.Thread(
            target=navigate_path, 
            args=(self.sim, self.path_logic, w_p, w_w, start_x, start_y, self.mission_finished_signal.emit, self.control_flags)
        )
        driver_thread.daemon = True 
        driver_thread.start()

    def on_mission_finished(self, success):
        """Acțiune la final, bazată pe succes sau anulare."""
        self.btn_generate.setEnabled(True)
        self.btn_clear.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        if success:
            self.btn_launch.setText("Misiune Completă")
            QMessageBox.information(self, "Felicitări", "Robotul a ajuns la destinație!\nSimularea a fost oprită.")
        else:
            self.btn_launch.setText("Lansează din nou")
            QMessageBox.warning(self, "Oprit", "Misiunea a fost oprită manual.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MazeControllerGUI()
    window.show()
    sys.exit(app.exec())