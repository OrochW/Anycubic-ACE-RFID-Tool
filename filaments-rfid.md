---

# 🚀 Anycubic ACE Pro RFID Wiki

## 1. 核心协议标志位 (Protocol Flag)
* [cite_start]**标志位地址**: Addr 14 (物理地址 0x13) [cite: 13, 14]。
* [cite_start]**标志位数值**: **`0xD4`** [cite: 9, 14]。
* [cite_start]**写入规则**: 颜色数据的 4 个字节必须遵循 `[R] [G] [B] [D4]` 格式 [cite: 9, 14]。
    * [cite_start]*示例 (米色)*: `F7 E6 DE D4` [cite: 14]。

---

## 2. 耗材主数据映射 (Filament Master Data)
[cite_start]这些数据对应芯片中的 **Addr 04 - 07**（SKU ID）以及 **Addr 0F / 0E**（材质名称） [cite: 4, 7, 8]。

| 材质名称 (Name) | 官方 SKU ID (Addr 04-07) | 材质缩写 (Addr 0F) | ASCII Hex |
| :--- | :--- | :--- | :--- |
| **PLA** | `AHPLBK-101` | `PLA\0` | `50 4C 41 00` |
| **PLA+** | `AHPLPBK-102` | `PLA+` | `50 4C 41 2B` |
| **PETG** | (待补充) | `PETG` | `50 45 54 47` |
| **ABS** | `SHABBK-102` | `ABS\0` | `41 42 53 00` |
| **TPU** | `STPBK-101` | `TPU\0` | `54 50 55 00` |
| **ASA** | (待补充) | `ASA\0` | `41 53 41 00` |
| **PLA Glow** | (待补充) | `PLA\0` | `50 4C 41 00` |
| **PLA High Speed** | `AHHSBK-103` | `PLA\0` | `50 4C 41 00` |
| **PLA Marble** | (待补充) | `PLA\0` | `50 4C 41 00` |
| **PLA Matte** | `HYGBK-102` | `PLA\0` | `50 4C 41 00` |
| **PLA SE** | (待补充) | `PLA\0` | `50 4C 41 00` |
| **PLA Silk** | `AHSCWH-102` | `Silk` | `53 69 6C 6B` |

---

## 3. 官方颜色识别库 (Official Color DB)
[cite_start]颜色数据存储在 **Addr 14**。写入时必须包含 **`D4`** 标志位 [cite: 9, 14]。

### 颜色配置表

| 颜色名称 (CN) | Color Name (EN) | 十六进制 (RGB) | 芯片最终写入值 (Addr 14 / 0x13) |
| :--- | :--- | :--- | :--- |
| 柔和桃 | Peach Fuzz | #FFC196 | FF C1 96 D4 |
| 星际紫 | Interstellar Violet | #5B618F | 5B 61 8F D4 |
| 青金石蓝 | Tropical Turquoise | #009CBD | 00 9C BD D4 |
| 春叶绿 | Spring Leaf | #89A84F | 89 A8 4F D4 |
| 鲜红 | Bright Red | #F40031 | F4 00 31 D4 |
| 橙色 | Orange | #FF6A14 | FF 6A 14 D4 |
| 暖橙 | Bright Orange | #FFA761 | FF A7 61 D4 |
| 黄色 | Yellow | #FED141 | FE D1 41 D4 |
| 柠檬黄 | Lemon Yellow | #FFEC3D | FF EC 3D D4 |
| 草绿 | Grass Green | #5CE003 | 5C E0 03 D4 |
| 绿色 | Green | #00BB31 | 00 BB 31 D4 |
| 深绿 | Dark Green | #008080 | 00 80 80 D4 |
| 天蓝 | Sky Blue | #87CEEB | 87 CE EB D4 |
| 青色 | Cyan | #0086D6 | 00 86 D6 D4 |
| 蓝色 | Blue | #0047BB | 00 47 BB D4 |
| 紫色 | Purple | #6558B1 | 65 58 B1 D4 |
| 粉色 | Pink | #EF60A3 | EF 60 A3 D4 |
| 紫红 | Fuchsia | #EE00EE | EE 00 EE D4 |
| 洋红 | Magenta | #EC008C | EC 00 8C D4 |
| 红色 | Red | #BA0C2F | BA 0C 2F D4 |
| 米色 | Beige | #F7E6DE | F7 E6 DE D4 |
| 木色 | Wood | #C0A392 | C0 A3 92 D4 |
| 焦橙 | Burnt Orange | #8C3400 | 8C 34 00 D4 |
| 金色 | Gold | #E4BC67 | E4 BC 67 D4 |
| 白色 | White | #FFFFFF | FF FF FF D4 |
| 银色 | Silver | #9EA6B4 | 9E A6 B4 D4 |
| 灰色 | Grey | #75787B | 75 78 7B D4 |
| 黑色 | Black | #212721 | 21 27 21 D4 |


---

## 4. 物理地址定义 (Memory Map Summary)
[cite_start]基于 NTAG213 芯片的 Page 分布逻辑 [cite: 1, 14]：

* [cite_start]**Addr 00 - 02**: 芯片 UID、BCC 与只读锁定位 [cite: 2, 3][cite_start]。**请勿修改，否则导致芯片报废** [cite: 3]。
* [cite_start]**Addr 04 - 07**: **耗材 SKU ID**（如 `AHPLBK-101`） [cite: 4, 5]。
* [cite_start]**Addr 0F (0E)**: **材质类型名称**（如 `PLA\0`） [cite: 7, 8]。
* [cite_start]**Addr 14 (13)**: **颜色与特征位**（RGB + `D4`） [cite: 9, 14]。
* [cite_start]**Addr 18 (17)**: **打印温度参数**（如 `C8 00 D2 00`） [cite: 10]。
* [cite_start]**Addr 1D (1C)**: **热床温度参数**（如 `32 00 3C 00`） [cite: 12]。

---

## 5. 同步与限制 (Sync Notes)
* [cite_start]**App 匹配**: 在 App 中手动添加耗材时，信息（Name）必须与切片软件 Anycubic Slicer Next 的用户预设完全一致 [cite: 13]。
* [cite_start]**显示异常**: 自定义耗材在 Slicer 工作台 (Workbench) 可能显示为 **“?”**，但在准备 (Prepare) 选项卡中可正常同步 [cite: 13]。
