# Anycubic-ACE-RFID-Tool

Anycubic ACE Pro RFID Editor. Customize third-party filaments by modifying NTAG215 tags (Material ID & RGB/D4 protocol). Supports acr122u readers.

纵维立方 Anycubic ACE Pro RFID 编辑器。通过修改 NTAG215 标签（材质 ID 与 RGB/D4 协议）自定义第三方耗材。支持 acr122u 读卡器。

---

## 1. 项目简介 | Project Introduction

本项目是一个基于 Python 开发的 GUI 桌面程序，专为 **Anycubic ACE Pro** 耗材盒设计。通过修改 NXP NTAG215 芯片特定地址的数据，允许用户自定义耗材材质 ID 和颜色，从而让系统识别第三方耗材。

This project is a Python-based GUI desktop application designed specifically for the **Anycubic ACE Pro** filament box. By modifying specific address data on NXP NTAG215 chips, it allows users to customize filament material IDs and colors, enabling the system to recognize third-party filaments.

---

## 2. 快速开始 | Quick Start

### 2.1 安装依赖 | Dependencies

```bash
pip install PySide6 pyscard
```

### 2.2 运行程序 | Run

**方式一：直接运行 Python 脚本**

```bash
python ace2pro.py
```

**方式二：编译客户端**

```bash
python -m PyInstaller --noconsole --onefile --name "Anycubic_ACE_Tool" ace2pro.py
```

编译后输出: `dist\Anycubic_ACE_Tool.exe`

* **`--noconsole`**: 运行时隐藏终端窗口 / Hide the terminal window during execution.
* **`--onefile`**: 将所有内容打包进单个 `.exe` 文件 / Package everything into a single `.exe` file.
* **`--name`**: 指定输出的文件名 / Specify the output filename.

---

## 3. 核心协议标志位 | Protocol Flag

* **标志位地址**: Addr 14 (物理地址 0x13)
* **标志位数值**: **`0xD4`**
* **写入规则**: 颜色数据的 4 个字节必须遵循 `[R] [G] [B] [D4]` 格式
* **示例 (米色)**: `F7 E6 DE D4`

---

## 4. RFID 存储映射表 | RFID Memory Map

本工具修改物理芯片的以下**页 (Addr)** 地址。每页包含 4 字节数据。

The tool modifies the following **Page (Addr)** addresses on the physical chip. Each page contains 4 bytes.

### 4.1 地址定义 | Address Definition

| 地址 (Addr) | 十六进制示例 | 功能描述 | 修改逻辑 |
| :--- | :--- | :--- | :--- |
| **00 - 02** | `04:EF:9D...` | **UID (唯一标识)** | **只读**。出厂固定。 |
| **Addr 0 - 2** | `04:EF:9D...` | **UID (Read-Only)** | **Read-Only**. Fixed at factory. |
| **04 - 07** | `41:48:50...` | **耗材 SKU ID** | 根据所选材质写入。 |
| **Addr 4 - 7** | `41:48:50...` | **Filament SKU ID** | Written based on selected material. |
| **14 (0x0E)** | `50:4C:41:00` | **材质类型 (ASCII)** | 核心标识，例如 `PLA\0`。 |
| **Addr 15 (0x0F)** | `50:4C:41:00` | **Material Type (ASCII)** | Core ID, e.g., `PLA\0`. |
| **20 (0x14)** | `FF:BB:GG:RR` | **颜色 (ABGR)** | ABGR 格式 (官方文档)，`[Alpha] [B] [G] [R]` |
| **Addr 20 (0x14)** | `FF:BB:GG:RR` | **Color (ABGR)** | ABGR format (Official), `[Alpha] [B] [G] [R]` |
| **24 (0x18)** | `C8:00:D2:00` | **喷头温度** | 预设打印温度参数。 |
| **Addr 24 (0x18)** | `C8:00:D2:00` | **Nozzle Temp** | Preset printing temperatures. |
| **28 (0x1C)** | `32:00:3C:00` | **热床温度** | 预设热床温度参数。 |
| **Addr 28 (0x1C)** | `32:00:3C:00` | **Bed Temp** | Preset heated bed temperatures. |
| **29 (0x1D)** | `AF:00:4A:01` | **线径/长度** | 1.75mm / 330m (满盘标识)。 |
| **Addr 29 (0x1D)** | `AF:00:4A:01` | **Diameter/Length** | 1.75mm / 330m (Full spool flag). |
| **30 (0x1E)** | `E8:03:00:00` | **重量** | 1000g (满盘标识)。 |
| **Addr 30 (0x1E)** | `E8:03:00:00` | **Weight** | 1000g (Full spool flag). |

### 4.2 满盘检测 | Full Spool Detection

| 耗材类型 | 线径/长度 (Addr 29) | 重量 (Addr 30) |
|---------|---------------------|----------------|
| **330m 满盘** | `AF 00 4A 01` (1.75mm / 330m) | `E8 03 00 00` (1000g) |
| **247m** | `AF 00 F7 00` (1.75mm / 247m) | - |
| **198m** | `AF 00 C6 00` (1.75mm / 198m) | - |
| **165m** | `AF 00 A5 00` (1.75mm / 165m) | - |

---

## 5. 耗材主数据映射 | Filament Master Data

这些数据对应芯片中的 **Addr 04 - 07**（SKU ID）以及 **Addr 0F / 0E**（材质名称）。

These correspond to **Addr 04 - 07** (SKU ID) and **Addr 0F / 0E** (Material Name) on the chip.

| 材质名称 (Name) | 官方 SKU ID (Addr 04-07) | 材质缩写 (Addr 0F) | ASCII Hex |
| :--- | :--- | :--- | :--- |
| **PLA** | `AHPLBK-101` | `PLA\0` | `50 4C 41 00` |
| **PLA+** | `AHPLPBK-102` | `PLA+` | `50 4C 41 2B` |
| **PETG** | `AHPETG-001` | `PETG` | `50 45 54 47` |
| **ABS** | `SHABBK-102` | `ABS\0` | `41 42 53 00` |
| **TPU** | `STPBK-101` | `TPU\0` | `54 50 55 00` |
| **ASA** | `AHASA-001` | `ASA\0` | `41 53 41 00` |
| **PA** | `AHPA-001` | `PA\0` | `50 41 00 00` |
| **PC** | `AHPC-001` | `PC\0` | `50 43 00 00` |
| **PLA Glow** | `AHPLG-001` | `PLA\0` | `50 4C 41 00` |
| **PLA High Speed** | `AHHSBK-103` | `PLA\0` | `50 4C 41 00` |
| **PLA Marble** | `AHPLM-001` | `PLA\0` | `50 4C 41 00` |
| **PLA Matte** | `HYGBK-102` | `PLA\0` | `50 4C 41 00` |
| **PLA SE** | `AHPLSE-001` | `PLA\0` | `50 4C 41 00` |
| **PLA Silk** | `AHSCWH-102` | `Silk` | `53 69 6C 6B` |

---

## 6. 官方颜色识别库 | Official Color DB

颜色数据存储在 **Addr 20 (0x14)**。写入时必须包含 **`D4`** 标志位。

Color data is stored at **Addr 20 (0x14)**. The **`D4`** flag must be appended.

### 6.1 颜色配置表 | Color Configuration Table

官方文档定义颜色格式为 **ABGR** (Alpha, Blue, Green, Red)。
官方文档示例: `FF00FF00` = 绿色。

| 颜色名称 (CN) | Color Name (EN) | 十六进制 (RGB) | 芯片最终写入值 (Addr 20 / 0x14) |
| :--- | :--- | :--- | :--- |
| 柔和桃 | Peach Fuzz | #FFC196 | FF 96 C1 FF |
| 星际紫 | Interstellar Violet | #5B618F | FF 8F 61 5B |
| 青金石蓝 | Tropical Turquoise | #009CBD | FF BD 9C 00 |
| 春叶绿 | Spring Leaf | #89A84F | FF 4F A8 89 |
| 鲜红 | Bright Red | #F40031 | FF 31 00 F4 |
| 橙色 | Orange | #FF6A14 | FF 14 6A FF |
| 暖橙 | Bright Orange | #FFA761 | FF 61 A7 FF |
| 黄色 | Yellow | #FED141 | FF 41 D1 FE |
| 柠檬黄 | Lemon Yellow | #FFEC3D | FF 3D EC FF |
| 草绿 | Grass Green | #5CE003 | FF 03 E0 5C |
| 绿色 | Green | #00BB31 | FF 31 BB 00 |
| 深绿 | Dark Green | #008080 | FF 80 80 00 |
| 天蓝 | Sky Blue | #87CEEB | FF EB CE 87 |
| 青色 | Cyan | #0086D6 | FF D6 86 00 |
| 蓝色 | Blue | #0047BB | FF BB 47 00 |
| 紫色 | Purple | #6558B1 | FF B1 58 65 |
| 粉色 | Pink | #EF60A3 | FF A3 60 EF |
| 紫红 | Fuchsia | #EE00EE | FF EE 00 EE |
| 洋红 | Magenta | #EC008C | FF 8C 00 EC |
| 红色 | Red | #BA0C2F | FF 2F 0C BA |
| 米色 | Beige | #F7E6DE | FF DE E6 F7 |
| 木色 | Wood | #C0A392 | FF 92 A3 C0 |
| 焦橙 | Burnt Orange | #8C3400 | FF 00 34 8C |
| 金色 | Gold | #E4BC67 | FF 67 BC E4 |
| 白色 | White | #FFFFFF | FF FF FF FF |
| 银色 | Silver | #9EA6B4 | FF B4 A6 9E |
| 灰色 | Grey | #75787B | FF 7B 78 75 |
| 黑色 | Black | #212721 | FF 21 27 21 |

---

## 7. UI 使用说明 | UI Operation Guide

### 7.1 状态监测 | Status Monitor

* **状态指示灯 (Status LED)**:
    * **NO READER**: 未连接读卡器 / Reader not connected.
    * **NO TAG**: 读卡器就绪，未检测到标签 / Reader ready, no tag detected.
    * **TAG READY**: 已检测到标签，可以进行读写 / Tag detected and ready for R/W.

### 7.2 操作流程 | Workflow

1. **配置材质 (Configure Material)**: 从下拉框选择材质类型（如 PLA）/ Select the material type from the dropdown.
2. **选择颜色 (Select Color)**: 从官方调色板中点击选择颜色色块 / Click a color block from the official palette.
3. **读写操作 (Read/Write)**: 使用"读取标签"拉取数据，或"同步写入"将选择的信息同步至芯片 / Use "Read Tag" to pull data or "Write Tag" to sync your selection to the chip.

---

## 8. 写入/读取命令示例 | APDU Command Examples

### 8.1 写入命令 (Write Commands)

```
# 1. 协议激活 (Addr 4)
FF D6 00 04 04 7B 00 65 00

# 2. 写入 SKU (Addr 5-9, 20字节)
FF D6 00 05 04 [R0 R1 R2 R3]  # Addr 5
FF D6 00 06 04 [R4 R5 R6 R7]  # Addr 6
FF D6 00 07 04 [R8 R9 R10 R11] # Addr 7
FF D6 00 08 04 [R12 R13 R14 R15] # Addr 8
FF D6 00 09 04 [R16 R17 R18 R19] # Addr 9

# 3. 写入品牌 (Addr 10-13, 16字节)
FF D6 00 0A 04 [R0 R1 R2 R3]  # Addr 10
FF D6 00 0B 04 [R4 R5 R6 R7]  # Addr 11
FF D6 00 0C 04 [R8 R9 R10 R11] # Addr 12
FF D6 00 0D 04 [R12 R13 R14 R15] # Addr 13

# 4. 写入材质名称 (Addr 15-18, 16字节)
FF D6 00 0F 04 [R0 R1 R2 R3]  # Addr 15
FF D6 00 10 04 [R4 R5 R6 R7]  # Addr 16
FF D6 00 11 04 [R8 R9 R10 R11] # Addr 17
FF D6 00 12 04 [R12 R13 R14 R15] # Addr 18

# 5. 写入颜色 (Addr 20, ABGR 格式)
FF D6 00 14 04 [Alpha] [B] [G] [R]

# 6. 写入挤出温度 (Addr 24, 小端)
FF D6 00 18 04 [min_low] [min_high] [max_low] [max_high]

# 7. 写入热床温度 (Addr 28, 小端)
FF D6 00 1C 04 [min_low] [min_high] [max_low] [max_high]

# 8. 写入线径/长度 (Addr 29, 小端)
FF D6 00 1D 04 [diam_low] [diam_high] [len_low] [len_high]

# 9. 写入重量 (Addr 30, 小端)
FF D6 00 1E 04 [weight_low] [weight_high] 00 00
```

### 8.2 读取命令 (Read Command)

```
# 读取单个 Page (以 Page 20 为例)
FF B0 00 14 04

# 返回: [Alpha] [B] [G] [R] (ABGR 格式)
# 例如: FF BB 47 00 = 蓝色 (#0047BB)
```

### 8.3 完整写入示例 (Full Write Example - PETG Lemon Yellow 330m)

```
# 输入: SKU="AHPETG-001", Brand="AC", Type="PETG", Color="#FFEC3D"
#       ExtTemp="200-230", BedTemp="50-60", Diameter=1.75, Length=330, Weight=1000g

# 1. 协议激活
FF D6 00 04 04 7B 00 65 00

# 2. SKU (AHPETG-001 + 填充)
FF D6 00 05 04 41 48 50 45  # "AHPE"
FF D6 00 06 04 54 47 2D 30  # "TG-0"
FF D6 00 07 04 30 31 00 00  # "01.."
FF D6 00 08 04 00 00 00 00  # "...."
FF D6 00 09 04 00 00 00 00  # "...."

# 3. 品牌 (AC + 填充)
FF D6 00 0A 04 41 43 00 00  # "AC.."
FF D6 00 0B 04 00 00 00 00  # "...."
FF D6 00 0C 04 00 00 00 00  # "...."
FF D6 00 0D 04 00 00 00 00  # "...."

# 4. 材质 (PETG + 填充)
FF D6 00 0F 04 50 45 54 47  # "PETG"
FF D6 00 10 04 00 00 00 00  # "...."
FF D6 00 11 04 00 00 00 00  # "...."
FF D6 00 12 04 00 00 00 00  # "...."

# 5. 颜色 (FF EC 3D D4)
FF D6 00 14 04 FF EC 3D D4

# 6. 挤出温度 (200-230°C, 小端)
FF D6 00 18 04 C8 00 E6 00

# 7. 热床温度 (50-60°C, 小端)
FF D6 00 1C 04 32 00 3C 00

# 8. 线径/长度 (1.75mm/330m, 小端)
FF D6 00 1D 04 AF 00 4A 01

# 9. 重量 (1000g, 小端)
FF D6 00 1E 04 E8 03 00 00
```

---

## 9. 同步与限制 | Sync Notes & Limitations

* **App 匹配**: 在 App 中手动添加耗材时，信息（Name）必须与切片软件 Anycubic Slicer Next 的用户预设完全一致。
* **App Match**: When manually adding filament in the App, the Name must match exactly with Anycubic Slicer Next.
* **显示异常**: 自定义耗材在 Slicer 工作台 (Workbench) 可能显示为 **"?"**，但在准备 (Prepare) 选项卡中可正常同步。
* **Display Issue**: Custom filament may show as **"?"** in the Workbench, but syncs normally in the Prepare tab.

---

## 10. 注意事项 | Notes

1. **UID 标签**: Page 0-1 为 UID，不可写入 / **UID is Read-Only**. Do not modify.
2. **密码保护**: 如果标签有密码保护，需要先认证 / If password protected, authenticate first.
3. **默认密码**: `FF FF FF FF` 或 `00 00 00 00` / Default password: `FF FF FF FF` or `00 00 00 00`.
4. **颜色格式**: 官方使用 **ABGR** 格式 (`[Alpha] [B] [G] [R]`) / Official uses **ABGR** format (`[Alpha] [B] [G] [R]`).
5. **满盘检测**: Addr 29 (`4A 01`) + Addr 30 (`E8 03`) / Full spool: Addr 29 (`4A 01`) + Addr 30 (`E8 03`)
6. **服务要求**: 使用前请确保 Windows 的 **Smart Card** 服务正在运行 / Ensure the **Smart Card** service is running.

---

## 11. 致谢 | Credits

thanks: https://github.com/DnG-Crafts/ACE-RFID
