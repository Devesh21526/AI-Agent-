
#!/usr/bin/env python3
"""
JARVIS Gaming Desktop Interface - PredatorSense Style
A modern gaming-style desktop application with system monitoring and voice assistant integration.
"""

import sys
import os
import threading
import time
import json
import psutil
import math
from datetime import datetime
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Import JARVIS components
try:
    from jarvis_assistant_fixed import Jarvis
    from ollama_optimizer_corrected import OllamaOptimizer
    from performance_monitor_corrected import PerformanceMonitor
    from sentence_detector_corrected import SentenceDetector
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    print("Warning: JARVIS components not found. Running in demo mode.")

class CircularGauge(QWidget):
    """Custom circular gauge widget for gaming-style metrics display"""

    def __init__(self, parent=None, min_value=0, max_value=100, value=0):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.gauge_color = QColor(0, 212, 255)  # Cyan color
        self.bg_color = QColor(30, 30, 30)
        self.text_color = QColor(255, 255, 255)
        self.setMinimumSize(200, 200)

    def set_value(self, value):
        """Set the gauge value"""
        self.value = max(self.min_value, min(self.max_value, value))
        self.update()

    def set_colors(self, gauge_color, bg_color, text_color):
        """Set custom colors for the gauge"""
        self.gauge_color = gauge_color
        self.bg_color = bg_color
        self.text_color = text_color
        self.update()

    def paintEvent(self, event):
        """Custom paint event for the circular gauge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate dimensions
        side = min(self.width(), self.height())
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        # Draw outer circle
        painter.setPen(QPen(self.bg_color, 8))
        painter.drawEllipse(-90, -90, 180, 180)

        # Draw progress arc
        painter.setPen(QPen(self.gauge_color, 8))
        span_angle = int(360 * (self.value - self.min_value) / (self.max_value - self.min_value))
        painter.drawArc(-90, -90, 180, 180, 90 * 16, -span_angle * 16)

        # Draw center value
        painter.setPen(QPen(self.text_color, 1))
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        painter.drawText(QRectF(-50, -10, 100, 20), Qt.AlignCenter, f"{int(self.value)}")

        # Draw percentage symbol
        painter.setFont(QFont("Arial", 12))
        painter.drawText(QRectF(-50, 10, 100, 20), Qt.AlignCenter, "%")

class GlowButton(QPushButton):
    """Custom button with glow effect"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 212, 255, 0.1);
                border: 2px solid #00D4FF;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: rgba(0, 212, 255, 0.2);
                border: 2px solid #00F0FF;
            }
            QPushButton:pressed {
                background-color: rgba(0, 212, 255, 0.3);
                border: 2px solid #0080FF;
            }
        """)

class SystemMonitor(QObject):
    """System monitoring with real-time updates"""

    # Signals for updating UI
    stats_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start system monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get system stats
                stats = {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent,
                    'cpu_temp': self._get_cpu_temperature(),
                    'timestamp': datetime.now().isoformat()
                }

                # Add GPU stats if available
                try:
                    stats['gpu_percent'] = self._get_gpu_usage()
                    stats['gpu_temp'] = self._get_gpu_temperature()
                except:
                    stats['gpu_percent'] = 0
                    stats['gpu_temp'] = 0

                self.stats_updated.emit(stats)
                time.sleep(1)

            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)

    def _get_cpu_temperature(self):
        """Get CPU temperature (Windows implementation)"""
        try:
            # This is a simplified version - in production you'd use WMI or other methods
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            temperature_infos = w.Sensor()
            for sensor in temperature_infos:
                if sensor.SensorType == u'Temperature' and 'CPU' in sensor.Name:
                    return int(sensor.Value) if sensor.Value else 45
        except:
            pass
        return 45  # Default temperature

    def _get_gpu_usage(self):
        """Get GPU usage percentage"""
        try:
            # This would require nvidia-ml-py or similar
            # For now, return simulated value
            return 29
        except:
            return 0

    def _get_gpu_temperature(self):
        """Get GPU temperature"""
        try:
            # This would require nvidia-ml-py or similar
            # For now, return simulated value
            return 52
        except:
            return 0

class JarvisController(QObject):
    """Controller for JARVIS integration"""

    # Signals
    status_changed = pyqtSignal(str)
    conversation_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.jarvis = None
        self.is_running = False

    def initialize_jarvis(self):
        """Initialize JARVIS if available"""
        if not JARVIS_AVAILABLE:
            self.status_changed.emit("JARVIS components not available")
            return False

        try:
            # Initialize JARVIS components
            self.jarvis = Jarvis(wake_word="jarvis", speech_rate=4)
            self.status_changed.emit("JARVIS initialized successfully")
            return True
        except Exception as e:
            self.status_changed.emit(f"JARVIS initialization failed: {str(e)}")
            return False

    def start_jarvis(self):
        """Start JARVIS"""
        if self.jarvis and not self.is_running:
            self.is_running = True
            self.jarvis_thread = threading.Thread(target=self._run_jarvis, daemon=True)
            self.jarvis_thread.start()
            self.status_changed.emit("JARVIS is active")

    def stop_jarvis(self):
        """Stop JARVIS"""
        if self.is_running:
            self.is_running = False
            if self.jarvis:
                self.jarvis.stop_event.set()
            self.status_changed.emit("JARVIS stopped")

    def _run_jarvis(self):
        """Run JARVIS in background"""
        try:
            if self.jarvis:
                self.jarvis.run()
        except Exception as e:
            self.status_changed.emit(f"JARVIS error: {str(e)}")

class MainDashboard(QMainWindow):
    """Main dashboard window with PredatorSense-style interface"""

    def __init__(self):
        super().__init__()
        self.system_monitor = SystemMonitor()
        self.jarvis_controller = JarvisController()
        self.init_ui()
        self.setup_connections()
        self.setup_system_tray()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("JARVIS - Gaming Performance Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A1A;
                color: #FFFFFF;
            }
            QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                color: #FFFFFF;
            }
            QGroupBox {
                border: 2px solid #00D4FF;
                border-radius: 10px;
                margin-top: 1ex;
                padding-top: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #00D4FF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)

        # Left panel - Performance gauges
        left_panel = self.create_performance_panel()
        main_layout.addWidget(left_panel, 2)

        # Right panel - JARVIS controls and info
        right_panel = self.create_control_panel()
        main_layout.addWidget(right_panel, 1)

        # Create status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("background-color: #2A2A2A; color: #FFFFFF;")

    def create_performance_panel(self):
        """Create the performance monitoring panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("SYSTEM PERFORMANCE")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00D4FF; margin: 10px;")
        layout.addWidget(title)

        # Gauges layout
        gauges_layout = QGridLayout()

        # Create gauges
        self.cpu_gauge = CircularGauge(min_value=0, max_value=100, value=0)
        self.gpu_gauge = CircularGauge(min_value=0, max_value=100, value=0)
        self.memory_gauge = CircularGauge(min_value=0, max_value=100, value=0)
        self.temp_gauge = CircularGauge(min_value=0, max_value=100, value=0)

        # Set different colors for each gauge
        self.cpu_gauge.set_colors(QColor(0, 212, 255), QColor(30, 30, 30), QColor(255, 255, 255))
        self.gpu_gauge.set_colors(QColor(255, 107, 107), QColor(30, 30, 30), QColor(255, 255, 255))
        self.memory_gauge.set_colors(QColor(78, 205, 196), QColor(30, 30, 30), QColor(255, 255, 255))
        self.temp_gauge.set_colors(QColor(255, 165, 0), QColor(30, 30, 30), QColor(255, 255, 255))

        # Add gauges to layout
        gauges_layout.addWidget(self.create_gauge_group("CPU", self.cpu_gauge), 0, 0)
        gauges_layout.addWidget(self.create_gauge_group("GPU", self.gpu_gauge), 0, 1)
        gauges_layout.addWidget(self.create_gauge_group("MEMORY", self.memory_gauge), 1, 0)
        gauges_layout.addWidget(self.create_gauge_group("TEMP", self.temp_gauge), 1, 1)

        layout.addLayout(gauges_layout)

        # System info
        self.system_info = QLabel()
        self.system_info.setStyleSheet("color: #CCCCCC; font-size: 12px; margin: 10px;")
        self.system_info.setAlignment(Qt.AlignCenter)
        self.update_system_info()
        layout.addWidget(self.system_info)

        return panel

    def create_gauge_group(self, title, gauge):
        """Create a grouped gauge with title"""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(gauge)
        return group

    def create_control_panel(self):
        """Create the control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # JARVIS Section
        jarvis_group = QGroupBox("JARVIS VOICE ASSISTANT")
        jarvis_layout = QVBoxLayout(jarvis_group)

        # Status indicator
        self.jarvis_status = QLabel("Initializing...")
        self.jarvis_status.setStyleSheet("color: #FFFF00; font-size: 14px; margin: 5px;")
        jarvis_layout.addWidget(self.jarvis_status)

        # Control buttons
        self.start_jarvis_btn = GlowButton("START JARVIS")
        self.start_jarvis_btn.clicked.connect(self.start_jarvis)
        jarvis_layout.addWidget(self.start_jarvis_btn)

        self.stop_jarvis_btn = GlowButton("STOP JARVIS")
        self.stop_jarvis_btn.clicked.connect(self.stop_jarvis)
        self.stop_jarvis_btn.setEnabled(False)
        jarvis_layout.addWidget(self.stop_jarvis_btn)

        # Conversation history
        self.conversation_history = QTextEdit()
        self.conversation_history.setStyleSheet("""
            QTextEdit {
                background-color: #2A2A2A;
                border: 1px solid #00D4FF;
                border-radius: 5px;
                padding: 5px;
                color: #FFFFFF;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        self.conversation_history.setMaximumHeight(150)
        jarvis_layout.addWidget(QLabel("Conversation History:"))
        jarvis_layout.addWidget(self.conversation_history)

        layout.addWidget(jarvis_group)

        # Monitoring Section
        monitoring_group = QGroupBox("SYSTEM MONITORING")
        monitoring_layout = QVBoxLayout(monitoring_group)

        self.start_monitoring_btn = GlowButton("START MONITORING")
        self.start_monitoring_btn.clicked.connect(self.start_monitoring)
        monitoring_layout.addWidget(self.start_monitoring_btn)

        self.stop_monitoring_btn = GlowButton("STOP MONITORING")
        self.stop_monitoring_btn.clicked.connect(self.stop_monitoring)
        self.stop_monitoring_btn.setEnabled(False)
        monitoring_layout.addWidget(self.stop_monitoring_btn)

        # Live stats
        self.live_stats = QLabel("Monitoring stopped")
        self.live_stats.setStyleSheet("color: #CCCCCC; font-size: 11px; margin: 5px;")
        self.live_stats.setWordWrap(True)
        monitoring_layout.addWidget(self.live_stats)

        layout.addWidget(monitoring_group)

        # App shortcuts
        shortcuts_group = QGroupBox("QUICK ACTIONS")
        shortcuts_layout = QVBoxLayout(shortcuts_group)

        minimize_btn = GlowButton("MINIMIZE TO TRAY")
        minimize_btn.clicked.connect(self.hide)
        shortcuts_layout.addWidget(minimize_btn)

        settings_btn = GlowButton("SETTINGS")
        settings_btn.clicked.connect(self.show_settings)
        shortcuts_layout.addWidget(settings_btn)

        layout.addWidget(shortcuts_group)

        layout.addStretch()

        return panel

    def setup_connections(self):
        """Setup signal connections"""
        self.system_monitor.stats_updated.connect(self.update_performance_gauges)
        self.jarvis_controller.status_changed.connect(self.update_jarvis_status)
        self.jarvis_controller.conversation_updated.connect(self.update_conversation)

    def setup_system_tray(self):
        """Setup system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(self, "System Tray", "System tray not available")
            return

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setToolTip("JARVIS Gaming Dashboard")

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show Dashboard", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        start_jarvis_action = QAction("Start JARVIS", self)
        start_jarvis_action.triggered.connect(self.start_jarvis)
        tray_menu.addAction(start_jarvis_action)

        tray_menu.addSeparator()

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()

    def update_system_info(self):
        """Update system information display"""
        info = f"System: {psutil.cpu_count()} CPU cores | "
        info += f"RAM: {psutil.virtual_memory().total // (1024**3)}GB | "
        info += f"Python: {sys.version.split()[0]}"
        self.system_info.setText(info)

    def update_performance_gauges(self, stats):
        """Update performance gauge values"""
        self.cpu_gauge.set_value(stats['cpu_percent'])
        self.gpu_gauge.set_value(stats['gpu_percent'])
        self.memory_gauge.set_value(stats['memory_percent'])
        self.temp_gauge.set_value(stats['cpu_temp'])

        # Update live stats
        stats_text = f"CPU: {stats['cpu_percent']:.1f}% | "
        stats_text += f"GPU: {stats['gpu_percent']:.1f}% | "
        stats_text += f"Memory: {stats['memory_percent']:.1f}% | "
        stats_text += f"Temp: {stats['cpu_temp']:.1f}°C"
        self.live_stats.setText(stats_text)

    def update_jarvis_status(self, status):
        """Update JARVIS status"""
        self.jarvis_status.setText(status)

        if "active" in status.lower():
            self.jarvis_status.setStyleSheet("color: #00FF00; font-size: 14px; margin: 5px;")
            self.start_jarvis_btn.setEnabled(False)
            self.stop_jarvis_btn.setEnabled(True)
        elif "stopped" in status.lower():
            self.jarvis_status.setStyleSheet("color: #FF0000; font-size: 14px; margin: 5px;")
            self.start_jarvis_btn.setEnabled(True)
            self.stop_jarvis_btn.setEnabled(False)
        else:
            self.jarvis_status.setStyleSheet("color: #FFFF00; font-size: 14px; margin: 5px;")

    def update_conversation(self, text):
        """Update conversation history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_history.append(f"[{timestamp}] {text}")

        # Auto-scroll to bottom
        scrollbar = self.conversation_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_jarvis(self):
        """Start JARVIS"""
        if self.jarvis_controller.initialize_jarvis():
            self.jarvis_controller.start_jarvis()
        else:
            self.update_conversation("JARVIS initialization failed - running in demo mode")

    def stop_jarvis(self):
        """Stop JARVIS"""
        self.jarvis_controller.stop_jarvis()

    def start_monitoring(self):
        """Start system monitoring"""
        self.system_monitor.start_monitoring()
        self.start_monitoring_btn.setEnabled(False)
        self.stop_monitoring_btn.setEnabled(True)
        self.live_stats.setText("Monitoring active...")

    def stop_monitoring(self):
        """Stop system monitoring"""
        self.system_monitor.stop_monitoring()
        self.start_monitoring_btn.setEnabled(True)
        self.stop_monitoring_btn.setEnabled(False)
        self.live_stats.setText("Monitoring stopped")

    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog would open here")

    def quit_application(self):
        """Quit the application"""
        self.system_monitor.stop_monitoring()
        self.jarvis_controller.stop_jarvis()
        QApplication.instance().quit()

    def closeEvent(self, event):
        """Handle close event"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_application()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Set application properties
    app.setApplicationName("JARVIS Gaming Dashboard")
    app.setApplicationVersion("1.0")

    # Create and show main window
    window = MainDashboard()
    window.show()

    # Start monitoring by default
    window.start_monitoring()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
