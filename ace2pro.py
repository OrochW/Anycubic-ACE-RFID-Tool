# -*- coding: utf-8 -*-
import sys
import time
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# 核心硬件库
try:
    from smartcard.System import readers
    from smartcard.util import toHexString, toBytes
    SCARD_AVAILABLE = True
except ImportError:
    SCARD_AVAILABLE = False

# --- 耗材主数据 ---
FILAMENT_MASTER_DATA = [
    {"Name": "PLA", "Id": "AHPLBK-101"}, {"Name": "PLA+", "Id": "AHPLPBK-102"},
    {"Name": "PETG", "Id": ""}, {"Name": "ABS", "Id": "SHABBK-102"},
    {"Name": "TPU", "Id": "STPBK-101"}, {"Name": "ASA", "Id": ""},
    {"Name": "PLA Glow", "Id": ""}, {"Name": "PLA High Speed", "Id": "AHHSBK-103"},
    {"Name": "PLA Marble", "Id": ""}, {"Name": "PLA Matte", "Id": "HYGBK-102"},
    {"Name": "PLA SE", "Id": ""}, {"Name": "PLA Silk", "Id": "AHSCWH-102"},
]

COLOR_DB = [
    {"name_cn": "柔和桃", "value": "#FFC196"}, {"name_cn": "星际紫", "value": "#5B618F"},
    {"name_cn": "青金石蓝", "value": "#009CBD"}, {"name_cn": "春叶绿", "value": "#89A84F"},
    {"name_cn": "鲜红", "value": "#F40031"}, {"name_cn": "橙色", "value": "#FF6A14"},
    {"name_cn": "暖橙", "value": "#FFA761"}, {"name_cn": "黄色", "value": "#FED141"},
    {"name_cn": "柠檬黄", "value": "#FFEC3D"}, {"name_cn": "草绿", "value": "#5CE003"},
    {"name_cn": "绿色", "value": "#00BB31"}, {"name_cn": "深绿", "value": "#008080"},
    {"name_cn": "天蓝", "value": "#87CEEB"}, {"name_cn": "青色", "value": "#0086D6"},
    {"name_cn": "蓝色", "value": "#0047BB"}, {"name_cn": "紫色", "value": "#6558B1"},
    {"name_cn": "粉色", "value": "#EF60A3"}, {"name_cn": "紫红", "value": "#EE00EE"},
    {"name_cn": "洋红", "value": "#EC008C"}, {"name_cn": "红色", "value": "#BA0C2F"},
    {"name_cn": "米色", "value": "#F7E6DE"}, {"name_cn": "木色", "value": "#C0A392"},
    {"name_cn": "焦橙", "value": "#8C3400"}, {"name_cn": "金色", "value": "#E4BC67"},
    {"name_cn": "白色", "value": "#FFFFFF"}, {"name_cn": "银色", "value": "#9EA6B4"},
    {"name_cn": "灰色", "value": "#75787B"}, {"name_cn": "黑色", "value": "#212721"},
]

class RFIDWorker(QThread):
    tag_status = Signal(bool)
    def run(self):
        last_state = False
        if not SCARD_AVAILABLE: return
        while True:
            try:
                r = readers()
                current_state = len(r) > 0
                if current_state:
                    conn = r[0].createConnection()
                    conn.connect()
                    _, sw1, _ = conn.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
                    current_state = (sw1 == 0x90)
                if current_state != last_state:
                    self.tag_status.emit(current_state)
                    last_state = current_state
            except:
                if last_state: self.tag_status.emit(False)
                last_state = False
            time.sleep(0.5)

class AnycubicRFIDTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anycubic ACE RFID Manager")
        self.setFixedSize(500, 880)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.is_auto_reading = False 
        self.selected_color_info = {"name_cn": "未选择", "value": "#FFFFFF"}
        self.setup_ui()
        self.worker = RFIDWorker()
        self.worker.tag_status.connect(self.handle_tag_change)
        self.worker.start()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(30, 25, 30, 30)
        main_lay.setSpacing(18)

        header = QHBoxLayout()
        title = QLabel("ACE RFID TOOL")
        title.setStyleSheet("font-family: 'Segoe UI', 'Microsoft YaHei'; font-size: 26px; font-weight: 800; color: #1A1A1A; letter-spacing: 1px;")
        self.status_led = QLabel("NO READER")
        self.status_led.setMinimumWidth(110)
        self.status_led.setFixedHeight(30)
        self.status_led.setAlignment(Qt.AlignCenter)
        self.status_led.setStyleSheet("color: #777; font-weight: 900; font-size: 11px; background: #F2F2F2; border-radius: 4px; padding-top: 2px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_led)
        main_lay.addLayout(header)

        label_style = "font-family: 'Microsoft YaHei UI'; font-size: 17px; font-weight: 700; color: #333;"

        main_lay.addWidget(QLabel("1. 配置材质类型", styleSheet=label_style))
        self.combo_mat = QComboBox()
        self.combo_mat.setMaxVisibleItems(12)
        self.combo_mat.setFixedHeight(50)
        # --- 针对选中遮挡问题的终极 CSS 修复 ---
        self.combo_mat.setStyleSheet("""
            QComboBox { 
                border: 2px solid #EEE; border-radius: 10px; padding-left: 15px; 
                font-size: 16px; font-weight: 500; background: white; 
            }
            QComboBox:hover { border-color: #0078D4; }
            QComboBox::drop-down { border: none; width: 35px; }
            QComboBox QAbstractItemView {
                border: 1px solid #DDD; background: white; outline: none;
            }
            QComboBox QAbstractItemView::item {
                height: 40px; padding-left: 10px; color: #333;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078D4; color: #FFFFFF; /* 强制白字蓝底 */
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #0078D4; color: #FFFFFF;
            }
        """)
        # 强制设置代理以确保 CSS 生效
        self.combo_mat.setItemDelegate(QStyledItemDelegate())
        for item in FILAMENT_MASTER_DATA:
            self.combo_mat.addItem(item["Name"], item) 
        main_lay.addWidget(self.combo_mat)

        main_lay.addWidget(QLabel("2. 官方颜色选择", styleSheet=label_style))
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)
        for i, color in enumerate(COLOR_DB):
            btn = QPushButton()
            btn.setFixedSize(48, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"background-color: {color['value']}; border: 1px solid #E5E5E5; border-radius: 5px;")
            btn.clicked.connect(lambda ch, c=color: self.on_color_selected(c))
            grid.addWidget(btn, i // 7, i % 7)
        main_lay.addWidget(grid_widget)

        prev_lay = QHBoxLayout()
        self.preview_bar = QLabel("请选择颜色...")
        self.preview_bar.setAlignment(Qt.AlignCenter)
        self.preview_bar.setFixedHeight(55)
        self.preview_bar.setStyleSheet("border: 2px dashed #EEE; border-radius: 10px; color: #999; font-weight: bold; font-size: 15px;")
        
        self.btn_auto = QPushButton("自动读取 OFF")
        self.btn_auto.setCheckable(True)
        self.btn_auto.setFixedSize(140, 55)
        self.btn_auto.setStyleSheet("QPushButton { background-color: #F9F9F9; color: #999; border-radius: 10px; font-weight: bold; border: 1px solid #EEE; }")
        self.btn_auto.clicked.connect(self.toggle_auto_read)
        
        prev_lay.addWidget(self.preview_bar, 3)
        prev_lay.addWidget(self.btn_auto, 2)
        main_lay.addLayout(prev_lay)

        action_lay = QHBoxLayout()
        self.btn_read = QPushButton("读取物理标签")
        self.btn_write = QPushButton("写入物理标签")
        for b in [self.btn_write, self.btn_read]:
            b.setFixedHeight(60)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("font-weight: 800; font-size: 16px; border-radius: 12px;")
        
        self.btn_read.setStyleSheet(self.btn_read.styleSheet() + "background-color: white; color: #0078D4; border: 2px solid #0078D4;")
        self.btn_write.setStyleSheet(self.btn_write.styleSheet() + "background-color: #0078D4; color: white; border: none;")
        self.btn_read.clicked.connect(lambda: self.read_tag_logic(manual=True))
        self.btn_write.clicked.connect(self.write_tag_logic)
        action_lay.addWidget(self.btn_read)
        action_lay.addWidget(self.btn_write)
        main_lay.addLayout(action_lay)

        l3 = QLabel("操作实时反馈", styleSheet=label_style)
        btn_clear = QPushButton("清空记录")
        btn_clear.setFixedSize(65, 24)
        btn_clear.setStyleSheet("font-size: 11px; color: #999; border: 1px solid #EEE; border-radius: 4px;")
        btn_clear.clicked.connect(lambda: self.log_box.clear())
        log_h = QHBoxLayout(); log_h.addWidget(l3); log_h.addStretch(); log_h.addWidget(btn_clear)
        main_lay.addLayout(log_h)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("QTextEdit { background-color: #FAFAFA; border: 1px solid #EEE; border-radius: 10px; color: #444; font-family: 'Consolas', 'Microsoft YaHei'; font-size: 12px; padding: 12px; }")
        main_lay.setStretch(11, 10) 
        main_lay.addWidget(self.log_box)

    def log(self, type_str, message, color="#333"):
        time_str = datetime.now().strftime("%H:%M:%S")
        type_colors = {'INFO': ('#0078D4', '#EBF5FF'), 'SUCCESS': ('#28CD41', '#E8F9EC'), 'WARN': ('#FF3B30', '#FFF0F0'), 'HARDWARE': ('#5856D6', '#F2F2F7')}
        fg, bg = type_colors.get(type_str, ('#666', '#EEE'))
        html = f"""<div style="margin-bottom: 6px;"><span style="color: #BBB; font-size: 10px;">[{time_str}]</span>
            <span style="background-color: {bg}; color: {fg}; padding: 2px 5px; border-radius: 3px; font-weight: bold; font-size: 10px;">{type_str}</span>
            <span style="color: {color}; margin-left: 6px; font-family: 'Microsoft YaHei';">{message}</span></div>"""
        self.log_box.append(html); self.log_box.moveCursor(QTextCursor.End)

    def toggle_auto_read(self, checked):
        self.is_auto_reading = checked
        if checked:
            self.btn_auto.setText("自动模式 ON")
            self.btn_auto.setStyleSheet("QPushButton { background-color: #00C853; color: white; border-radius: 10px; font-weight: bold; border: none; }")
            self.log("INFO", "自动检测已开启")
        else:
            self.btn_auto.setText("自动读取 OFF")
            self.btn_auto.setStyleSheet("QPushButton { background-color: #F9F9F9; color: #999; border-radius: 10px; font-weight: bold; border: 1px solid #EEE; }")
            self.log("INFO", "自动检测已关闭")

    def handle_tag_change(self, has_tag):
        if has_tag:
            self.status_led.setText("TAG READY")
            self.status_led.setStyleSheet("color: white; font-weight: 900; font-size: 11px; background: #28CD41; border-radius: 4px; padding-top: 2px;")
            self.log("HARDWARE", "NTAG215 标签已就绪")
            if self.is_auto_reading: self.read_tag_logic(manual=False)
        else:
            self.status_led.setText("NO TAG")
            self.status_led.setStyleSheet("color: #FF3B30; font-weight: 900; font-size: 11px; background: #FFF0F0; border-radius: 4px; border: 1px solid #FFCCCC; padding-top: 2px;")
            self.log("HARDWARE", "标签已移出感应区")

    def on_color_selected(self, color_info):
        self.selected_color_info = color_info
        self.preview_bar.setText(f"{color_info['name_cn']}")
        r, g, b = int(color_info['value'][1:3], 16), int(color_info['value'][3:5], 16), int(color_info['value'][5:7], 16)
        text_color = "white" if (r * 0.299 + g * 0.587 + b * 0.114) < 150 else "#333"
        self.preview_bar.setStyleSheet(f"background-color: {color_info['value']}; color: {text_color}; border-radius: 10px; font-weight: 800; font-size: 16px; border: none;")

    def get_conn(self):
        try:
            r = readers(); return r[0].createConnection() if r else None
        except: return None

    def read_tag_logic(self, manual=False):
        conn = self.get_conn()
        if not conn: return
        try:
            conn.connect()
            r_m, s1, _ = conn.transmit([0xFF, 0xB0, 0x00, 0x0E, 0x04])
            mat = "".join([chr(b) for b in r_m if 32 <= b <= 126]).strip()
            r_c, s1, _ = conn.transmit([0xFF, 0xB0, 0x00, 0x13, 0x04])
            color_name = "未知颜色"
            if s1 == 0x90:
                hex_v = f"#{r_c[0]:02X}{r_c[1]:02X}{r_c[2]:02X}".upper()
                for c in COLOR_DB:
                    if c['value'].upper() == hex_v: self.on_color_selected(c); color_name = c['name_cn']; break
            self.log("SUCCESS", f"读取完成：{mat} / {color_name}")
        except: self.log("WARN", "通讯异常")

    def write_tag_logic(self):
        conn = self.get_conn()
        if not conn: return
        mat_info = self.combo_mat.currentData(); col_info = self.selected_color_info
        if col_info['name_cn'] == "未选择": return
        try:
            conn.connect()
            m_b = list(mat_info['Name'].encode('ascii'))
            conn.transmit([0xFF, 0xD6, 0x00, 0x0E, 0x04] + (m_b + [0]*4)[:4])
            r, g, b = int(col_info['value'][1:3], 16), int(col_info['value'][3:5], 16), int(col_info['value'][5:7], 16)
            conn.transmit([0xFF, 0xD6, 0x00, 0x13, 0x04, r, g, b, 0xD4])
            self.log("SUCCESS", f"写入完成：{mat_info['Name']} - {col_info['name_cn']}")
        except: self.log("WARN", "写入失败")

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion"); win = AnycubicRFIDTool(); win.show(); sys.exit(app.exec())
