# Anycubic-ACE-RFID-Tool
Anycubic ACE Pro RFID Editor. Customize third-party filaments by modifying NTAG215 tags (Material ID &amp; RGB/D4 protocol). Supports acr122u readers.  纵维立方 Anycubic ACE Pro RFID 编辑器。通过修改 NTAG215 标签（材质 ID 与 RGB/D4 协议）自定义第三方耗材。支持 acr122u 读卡器。

---


## 1. Project Introduction | 项目简介
This project is a Python-based GUI desktop application designed specifically for the **Anycubic ACE Pro** filament box. By modifying specific address data on NXP NTAG215 chips, it allows users to customize filament material IDs and colors, enabling the system to recognize third-party filaments.
本项目是一个基于 Python 开发的 GUI 桌面程序，专为 **Anycubic ACE Pro** 耗材盒设计。通过修改 NXP NTAG215 芯片特定地址的数据，允许用户自定义耗材材质 ID 和颜色，从而让系统识别第三方耗材。

## 2. RFID Memory Map | RFID 存储映射表
The tool modifies the following **Page (Addr)** addresses on the physical chip. Each page contains 4 bytes.
本工具修改物理芯片的以下**页 (Addr)** 地址。每页包含 4 字节数据。

| Address (Addr) | Hex Data Example | Function Description | Modification Logic |
| :--- | :--- | :--- | :--- |
| **00 - 01** | `04:EF:9D...` | **UID** | **Read-Only**. Fixed at factory. |
| **地址 (Addr)** | **十六进制示例** | **功能描述** | **修改逻辑** |
| **00 - 01** | `04:EF:9D...` | **UID (唯一标识)** | **只读**。出厂固定。 |
| **04 - 06** | `41:48:50...` | **Filament SKU ID** | Written based on selected material. |
| **04 - 06** | `41:48:50...` | **耗材 SKU ID** | 根据所选材质写入。 |
| **0F (0E)** | `50:4C:41:00` | **Material Type (ASCII)** | Core ID, e.g., `PLA\0`. |
| **0F (0E)** | `50:4C:41:00` | **材质类型 (ASCII)** | 核心标识，例如 `PLA\0`。 |
| **14 (13)** | `FF:96:B8:D4` | **Color & Protocol Bit** | RGB + Fixed `D4` suffix. |
| **14 (13)** | `FF:96:B8:D4` | **颜色与协议位** | RGB 颜色 + 固定 `D4` 后缀。 |
| **18 (17)** | `C8:00:D2:00` | **Nozzle Temp** | Preset printing temperatures. |
| **18 (17)** | `C8:00:D2:00` | **喷头温度** | 预设打印温度参数。 |
| **1D (1C)** | `32:00:3C:00` | **Bed Temp** | Preset heated bed temperatures. |
| **1D (1C)** | `32:00:3C:00` | **热床温度** | 预设热床温度参数。 |

---

## 3. UI Operation Guide | UI 使用说明

### 3.1 Status Monitor | 状态监测
* **Status LED**: 
    * **NO READER**: Reader not connected.
    * **NO TAG**: Reader ready, no tag detected.
    * **TAG READY**: Tag detected and ready for R/W.
* **状态指示灯**:
    * **NO READER**: 未连接读卡器。
    * **NO TAG**: 读卡器就绪，未检测到标签。
    * **TAG READY**: 已检测到标签，可以进行读写。

### 3.2 Workflow | 操作流程
1.  * **Configure Material**: Select the material type (e.g., PLA) from the dropdown.
    * **配置材质**: 从下拉框选择材质类型（如 PLA）。
3.  * **Select Color**: Click a color block from the official palette.
    * **选择颜色**: 从官方调色板中点击选择颜色色块。
4.  * **Read/Write**: Use "Read Tag" to pull data or "Write Tag" to sync your selection to the chip.
    * **读写操作**: 使用“读取标签”拉取数据，或“同步写入”将选择的信息同步至芯片。

---

## 4. Compilation & Deployment | 编译与发布
Use the following command to compile the script into a standalone executable:
使用以下命令将脚本编译为独立的可执行文件：

```bash
python -m PyInstaller --noconsole --onefile --name "Anycubic_ACE_Tool" ace2pro.py
```

* **`--noconsole`**: Hide the terminal window during execution.
  **`--noconsole`**: 运行时隐藏终端窗口。
* **`--onefile`**: Package everything into a single `.exe`.
  **`--onefile`**: 将所有内容打包进单个 `.exe` 文件。
* **`--name`**: Specify the output filename.
  **`--name`**: 指定输出的文件名。

---

**Note**: Ensure the **Smart Card** service is running in Windows before use.
**注意**: 使用前请确保 Windows 的 **Smart Card** 服务正在运行。

thanks: https://github.com/DnG-Crafts/ACE-RFID
