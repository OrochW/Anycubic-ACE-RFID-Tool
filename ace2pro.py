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
    {"Name": "PLA", "Id": "AHPLBK-101"},
    {"Name": "PLA+", "Id": "AHPLPBK-102"},
    {"Name": "PETG", "Id": "AHPETG-001"},
    {"Name": "ABS", "Id": "SHABBK-102"},
    {"Name": "TPU", "Id": "STPBK-101"},
    {"Name": "ASA", "Id": "AHASA-001"},
    {"Name": "PA", "Id": "AHPA-001"},
    {"Name": "PC", "Id": "AHPC-001"},
    {"Name": "PLA Glow", "Id": "AHPLG-001"},
    {"Name": "PLA High Speed", "Id": "AHHSBK-103"},
    {"Name": "PLA Marble", "Id": "AHPLM-001"},
    {"Name": "PLA Matte", "Id": "HYGBK-102"},
    {"Name": "PLA SE", "Id": "AHPLSE-001"},
    {"Name": "PLA Silk", "Id": "AHSCWH-102"},
]

COLOR_DB = [
    {"name_cn": "柔和桃", "value": "#FFC196", "color":[255,193,150]},
    {"name_cn": "星际紫", "value": "#5B618F", "color":[91,97,143]},
    {"name_cn": "青金石蓝", "value": "#009CBD", "color":[0,156,189]},
    {"name_cn": "春叶绿", "value": "#89A84F", "color":[137,168,79]},
    {"name_cn": "鲜红", "value": "#F40031", "color":[244,0,49]},
    {"name_cn": "橙色", "value": "#FF6A14", "color":[255,106,20]},
    {"name_cn": "暖橙", "value": "#FFA761", "color":[255,167,97]},
    {"name_cn": "黄色", "value": "#FED141", "color":[254,209,65]},
    {"name_cn": "柠檬黄", "value": "#FFEC3D", "color":[255,236,61]},
    {"name_cn": "草绿", "value": "#5CE003", "color":[92,224,3]},
    {"name_cn": "绿色", "value": "#00BB31", "color":[0,187,49]},
    {"name_cn": "深绿", "value": "#008080", "color":[0,128,128]},
    {"name_cn": "天蓝", "value": "#87CEEB", "color":[135,206,235]},
    {"name_cn": "青色", "value": "#0086D6", "color":[0,134,214]},
    {"name_cn": "蓝色", "value": "#0047BB", "color":[0,71,187]},
    {"name_cn": "紫色", "value": "#6558B1", "color":[101,88,177]},
    {"name_cn": "粉色", "value": "#EF60A3", "color":[239,96,163]},
    {"name_cn": "紫红", "value": "#EE00EE", "color":[238,0,238]},
    {"name_cn": "洋红", "value": "#EC008C", "color":[236,0,140]},
    {"name_cn": "红色", "value": "#BA0C2F", "color":[186,12,47]},
    {"name_cn": "米色", "value": "#F7E6DE", "color":[247,230,222]},
    {"name_cn": "木色", "value": "#C0A392", "color":[192,163,146]},
    {"name_cn": "焦橙", "value": "#8C3400", "color":[140,52,0]},
    {"name_cn": "金色", "value": "#E4BC67", "color":[228,188,103]},
    {"name_cn": "白色", "value": "#FFFFFF", "color":[255,255,255]},
    {"name_cn": "银色", "value": "#9EA6B4", "color":[158,166,180]},
    {"name_cn": "灰色", "value": "#75787B", "color":[117,120,123]},
    {"name_cn": "黑色", "value": "#212721", "color":[33,39,33]},
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
        self.setFixedSize(500, 920) # 稍微调高一点 UI 高度
        self.setStyleSheet("background-color: #FFFFFF;")
        self.is_auto_reading = False 
        self.selected_color_info = {"name_cn": "未选择", "value": "#FFFFFF"}
        self.debug_mode = False # 默认不开启
        self.current_tag_ready = False
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
        self.combo_mat.setView(QListView())
        self.combo_mat.setFixedHeight(50)
        self.combo_mat.setStyleSheet("""
            QComboBox { 
                border: 2px solid #EEE; border-radius: 10px; padding-left: 15px; 
                font-size: 16px; font-weight: 500; background: white; combobox-popup: 0;
            }
            QComboBox:hover { border-color: #0078D4; }
            QComboBox::drop-down { 
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 30px; border-left: 1px solid #EEE; border-top-right-radius: 10px; border-bottom-right-radius: 10px;
            }
            QComboBox::down-arrow { 
                image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #999; margin-top: 2px;
            }
            QComboBox QAbstractItemView { border: 1px solid #DDD; background: white; outline: none; selection-background-color: #0078D4; }
            QComboBox QAbstractItemView::item { height: 40px; padding-left: 10px; color: #333; }
        """)

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
        
        self.btn_read.setStyleSheet("background-color: white; color: #0078D4; border: 2px solid #0078D4; font-weight: 800; font-size: 16px; border-radius: 12px;")
        self.btn_write.setStyleSheet("background-color: #0078D4; color: white; border: none; font-weight: 800; font-size: 16px; border-radius: 12px;")
        self.btn_read.clicked.connect(lambda: self.read_tag_logic(manual=True))
        self.btn_write.clicked.connect(self.write_tag_logic)
        action_lay.addWidget(self.btn_read)
        action_lay.addWidget(self.btn_write)
        main_lay.addLayout(action_lay)

        # 日志头部栏（含 Debug 开关）
        log_h = QHBoxLayout()
        log_h.addWidget(QLabel("操作实时反馈", styleSheet=label_style))
        log_h.addStretch()
        
        self.btn_debug_toggle = QPushButton("DEBUGLOG OFF")
        self.btn_debug_toggle.setCheckable(True)
        self.btn_debug_toggle.setFixedSize(90, 24)
        self.btn_debug_toggle.setStyleSheet("QPushButton { font-size: 10px; color: #999; border: 1px solid #EEE; border-radius: 4px; font-weight: bold; }")
        self.btn_debug_toggle.clicked.connect(self.toggle_debug_mode)
        
        btn_clear = QPushButton("清空记录")
        btn_clear.setFixedSize(65, 24)
        btn_clear.setStyleSheet("font-size: 11px; color: #999; border: 1px solid #EEE; border-radius: 4px;")
        btn_clear.clicked.connect(lambda: self.log_box.clear())
        
        log_h.addWidget(self.btn_debug_toggle)
        log_h.addWidget(btn_clear)
        main_lay.addLayout(log_h)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("QTextEdit { background-color: #FAFAFA; border: 1px solid #EEE; border-radius: 10px; color: #444; font-family: 'Consolas', 'Microsoft YaHei'; font-size: 12px; padding: 12px; }")
        main_lay.addWidget(self.log_box)

    def log(self, type_str, message, color="#333"):
        time_str = datetime.now().strftime("%H:%M:%S")
        type_colors = {
            'INFO': ('#0078D4', '#EBF5FF'), 
            'SUCCESS': ('#28CD41', '#E8F9EC'), 
            'WARN': ('#FF3B30', '#FFF0F0'), 
            'HARDWARE': ('#5856D6', '#F2F2F7'),
            'DEBUG': ('#666', '#EEE')
        }
        fg, bg = type_colors.get(type_str, ('#666', '#EEE'))
        html = f"""<div style="margin-bottom: 6px;"><span style="color: #BBB; font-size: 10px;">[{time_str}]</span>
            <span style="background-color: {bg}; color: {fg}; padding: 2px 5px; border-radius: 3px; font-weight: bold; font-size: 10px;">{type_str}</span>
            <span style="color: {color}; margin-left: 6px; font-family: 'Microsoft YaHei';">{message}</span></div>"""
        self.log_box.append(html); self.log_box.moveCursor(QTextCursor.End)

    def toggle_debug_mode(self, checked):
        self.debug_mode = checked
        if checked:
            self.btn_debug_toggle.setText("DEBUGLOG ON")
            self.btn_debug_toggle.setStyleSheet("QPushButton { font-size: 10px; color: white; background: #555; border-radius: 4px; font-weight: bold; }")
            self.log("INFO", "调试模式已开启：将显示详细寄存器数据")
        else:
            self.btn_debug_toggle.setText("DEBUGLOG OFF")
            self.btn_debug_toggle.setStyleSheet("QPushButton { font-size: 10px; color: #999; border: 1px solid #EEE; border-radius: 4px; font-weight: bold; }")

    def toggle_auto_read(self, checked):
        self.is_auto_reading = checked
        if checked:
            self.btn_auto.setText("自动模式 ON")
            self.btn_auto.setStyleSheet("QPushButton { background-color: #00C853; color: white; border-radius: 10px; font-weight: bold; border: none; }")
            self.log("INFO", "自动读取开启")
        else:
            self.btn_auto.setText("自动读取 OFF")
            self.btn_auto.setStyleSheet("QPushButton { background-color: #F9F9F9; color: #999; border-radius: 10px; font-weight: bold; border: 1px solid #EEE; }")

    def handle_tag_change(self, has_tag):
        self.current_tag_ready = has_tag
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
        if not self.current_tag_ready: return
        conn = self.get_conn()
        if not conn: return
        data_map = {} # 定义
        try:
            conn.connect()
            if manual or self.debug_mode:
                self.log("SYSTEM", ">>> 启动全寄存器协议扫描 <<<", "#569CD6")
            
            for p in range(4, 32): # 循环读取
                QApplication.processEvents()
                res, sw1, _ = conn.transmit([0xFF, 0xB0, 0x00, p, 0x04])
                if sw1 == 0x90:
                    data_map[p] = res
                    # --- 修改点 2：加上判断，只有开启 Debug 才打印 PAGE 数据 ---
                    if self.debug_mode:
                        h = " ".join([f"{b:02X}" for b in res])
                        a = "".join([chr(b) if 32<=b<=126 else "." for b in res])
                        self.log(f"PAGE {p:02d}", f"{h}  |  {a}", "#CE9178")

            # --- 关键功能：检测空白标签 ---
            if 4 not in data_map or data_map[4] != [0x7B, 0x00, 0x65, 0x00]:
                self.log("STATUS", "检测到空白标签或格式未激活，请点击 [同步写入]", "#E06C75")
                return

            # --- 正常解析逻辑 (对齐官方 Dump 地址) ---
            # 1. 解析 SKU (官方在 Page 05, 06, 07)
            sku = "".join([chr(b) for p in [5,6,7] for b in data_map.get(p, []) if 32<=b<=126]).strip()
            
            # 2. 解析颜色 (官方在 Page 13，Page 20 可能为空)
            color_name = "未知"
            # 官方 Dump 显示颜色校验在 Page 19 (0x13)
            if 19 in data_map:
                c = data_map[19]
                tag_hex = f"#{c[3]:02X}{c[2]:02X}{c[1]:02X}".upper() # RGB 顺序
                for item in COLOR_DB:
                    if item['value'].upper() == tag_hex:
                        color_name = item['name_cn']; break
                self.log("SUCCESS", f"已识别: {sku} | 颜色: {color_name} ({tag_hex})", "#98C379")

            # 3. 解析物理参数 (对齐官方数据)
            # 喷嘴温度在 Page 23 (0x17) [cite: 10, 28]
            if 23 in data_map:
                t = data_map[23]
                self.log("PARAMS", f"喷嘴温度: {t[0]}°C - {t[2]}°C", "#61AFEF")

            # 长度与线径在 Page 29 (0x1D) [cite: 12, 30]
            # 满盘百分比在 Page 30 (0x1E) [cite: 12, 30]
            is_full = False
            if 29 in data_map and data_map[29][2:4] == [0x4A, 0x01]:
                if 30 in data_map and data_map[30][0:2] == [0xE8, 0x03]:
                    is_full = True
            
            if is_full:
                self.log("STATUS", "检测结果: 330m (官方满盘格式)", "#98C379")
            else:
                self.log("WARN", "检测结果: 非满盘或长度校验不匹配", "#E06C75")

        except Exception as e:
            self.log("ERROR", f"读取失败: {str(e)}", "#F44747")

    def write_tag_logic(self):
        if not self.current_tag_ready: return
        conn = self.get_conn()
        if not conn: return
        mat = self.combo_mat.currentData()
        col = self.selected_color_info
        try:
            conn.connect()
            
            # 1. 协议激活 (Page 04) [cite: 4, 22]
            conn.transmit([0xFF, 0xD6, 0x00, 0x04, 0x04, 0x7B, 0x00, 0x65, 0x00])
            
            # 2. 写入 SKU (Page 05-07) [cite: 22]
            sku_b = list(mat["Id"].ljust(12, '\x00').encode("ascii"))
            for i in range(3):
                conn.transmit([0xFF, 0xD6, 0x00, 0x05 + i, 0x04] + sku_b[i*4:(i+1)*4])
            
            # 3. 写入品牌 (Page 0A) 与 材质名称 (Page 0E) [cite: 23, 25]
            conn.transmit([0xFF, 0xD6, 0x00, 0x0A, 0x04, 0x41, 0x6E, 0x79, 0x63]) # "Anyc"
            conn.transmit([0xFF, 0xD6, 0x00, 0x0E, 0x04] + list(mat["Name"].ljust(4, '\x00').encode("ascii"))[:4])

            # 4. 写入颜色数据 (官方 Dump 显示在 Page 13 [0x13]) [cite: 9, 27]
            r, g, b = int(col['value'][1:3], 16), int(col['value'][3:5], 16), int(col['value'][5:7], 16)
            conn.transmit([0xFF, 0xD6, 0x00, 0x13, 0x04, 0xFF, b, g, r]) 

            # 5. 写入喷嘴温度 (官方在 Page 17 [0x17]) [cite: 10, 28]
            # 数据: C8 00 D2 00 代表 200-210°C
            conn.transmit([0xFF, 0xD6, 0x00, 0x17, 0x04, 0xC8, 0x00, 0xD2, 0x00])

            # 6. 写入热床温度 (官方在 Page 1C [0x1C]) 
            # 数据: 32 00 3C 00 代表 50-60°C
            conn.transmit([0xFF, 0xD6, 0x00, 0x1C, 0x04, 0x32, 0x00, 0x3C, 0x00])

            # 7. 核心修正：线径与满盘长度 (官方在 Page 1D [0x1D]) 
            # 数据: AF 00 4A 01 代表 1.75mm / 330m
            conn.transmit([0xFF, 0xD6, 0x00, 0x1D, 0x04, 0xAF, 0x00, 0x4A, 0x01]) 

            # 8. 核心修正：剩余百分比校验 (官方在 Page 1E [0x1E]) 
            # 数据: E8 03 00 00 代表 1000 (即 100.0%)
            conn.transmit([0xFF, 0xD6, 0x00, 0x1E, 0x04, 0xE8, 0x03, 0x00, 0x00])

            self.log("SUCCESS", "已按照原厂 Dump 修正地址偏移，满盘参数注入成功", "#98C379")
        except Exception as e:
            self.log("ERROR", f"写入失败: {e}", "#F44747")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = AnycubicRFIDTool()
    win.show()
    sys.exit(app.exec())
