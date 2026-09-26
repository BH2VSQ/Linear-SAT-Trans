# WSJT-X FT4 Satellite Log Converter

用于将 **WSJT-X 导出的 FT4 通联日志**转换为包含线性卫星信息的 **Satellite FT4 ADIF 日志**。

当前支持以下卫星：

| 参数     | 卫星名称  | 卫星转发模式 |
| ------ | ----- | ------ |
| `JO97` | JO-97 | U/V    |
| `AO73` | AO-73 | U/V    |
| `RS44` | RS-44 | V/U    |

脚本不依赖第三方 Python 库，仅需要 Python 3 标准库。

---

## 1. 功能

脚本主要用于将普通的 WSJT-X FT4 日志转换为卫星日志。

转换时会自动为每条 QSO 添加或覆盖以下 ADIF 字段：

```text
PROP_MODE = SAT
SAT_NAME  = JO-97 / AO-73 / RS-44
SAT_MODE  = U/V / V/U
MODE      = MFSK
SUBMODE   = FT4
```

输入日志中的其他信息会尽可能保留，例如：

```text
QSO_DATE
TIME_ON
QSO_DATE_OFF
TIME_OFF
CALL
GRIDSQUARE
FREQ
RST_SENT
RST_RCVD
TX_PWR
NAME
COMMENT
```

脚本不会根据卫星轨道数据自动计算 Doppler，也不会修改输入日志中的频率。

---

# 2. 环境要求

需要：

- Python 3.8 或更高版本
- Windows / Linux / macOS 均可
- 不需要安装第三方 Python 模块

检查 Python：

```bash
python --version
```

或者：

```bash
python3 --version
```

---

# 3. 文件结构

最简单的目录结构：

```text
SatelliteLog/
├── wsjtx_to_satlog.py
└── wsjtx_log.adi
```

运行后：

```text
SatelliteLog/
├── wsjtx_to_satlog.py
├── wsjtx_log.adi
└── wsjtx_log-output.adi
```

---

# 4. 基本用法

命令格式：

```bash
python wsjtx_to_satlog.py --sat <卫星> --input <输入文件> [--output <输出文件>]
```

其中：

- `--sat`：指定卫星
- `--input`：指定 WSJT-X 日志文件
- `--output`：指定输出文件路径和文件名，可选

---

# 5. `--sat` 参数

支持：

```text
JO97
AO73
RS44
```

例如：

```bash
python wsjtx_to_satlog.py --sat JO97 --input wsjtx_log.adi
或者
wsjtx_to_satlog.exe --sat JO97 --input wsjtx_log.adi
```

表示把日志转换为 **JO-97** 卫星日志。

---

# 6. `--input` 参数

`--input` 用于指定输入日志文件。

例如：

```bash
python wsjtx_to_satlog.py --sat AO73 --input wsjtx_log.adi
或者
wsjtx_to_satlog.exe --sat AO73 --input wsjtx_log.adi
```

支持的输入文件类型：

```text
.adi
.adif
```

脚本会根据扩展名以及文件内容自动判断输入格式。

---

## 6.1 WSJT-X ADIF 日志

例如：

```bash
python wsjtx_to_satlog.py \
    --sat RS44 \
    --input "C:\Users\User\AppData\Local\WSJT-X\wsjtx_log.adi"
或者
wsjtx_to_satlog.exe \
    --sat RS44 \
    --input "C:\Users\User\AppData\Local\WSJT-X\wsjtx_log.adi"
```

Windows PowerShell / CMD 中也可以直接写成一行：

```bash
python wsjtx_to_satlog.py --sat RS44 --input "C:\Users\User\AppData\Local\WSJT-X\wsjtx_log.adi"
或者
wsjtx_to_satlog.exe --sat RS44 --input "C:\Users\User\AppData\Local\WSJT-X\wsjtx_log.adi"
```

---

# 7. `--output` 参数

使用 `--output` 可以完全指定输出文件。

例如：

```bash
python wsjtx_to_satlog.py --sat AO73 --input wsjtx_log.adi --output AO73-FT4.adi
或者
wsjtx_to_satlog.exe --sat AO73 --input wsjtx_log.adi --output AO73-FT4.adi
```

指定绝对路径：

```bash
python wsjtx_to_satlog.py --sat AO73 --input wsjtx_log.adi --output "D:\SatelliteLog\AO73-FT4.adi"
或者
wsjtx_to_satlog.exe --sat AO73 --input wsjtx_log.adi --output "D:\SatelliteLog\AO73-FT4.adi"
```

如果输出目录不存在，脚本会自动创建。

---

# 8. 不使用 `--output`

`--output` 是可选参数。

如果不指定，脚本会自动在输入文件所在目录生成输出文件。

### 输入为 `.adi` / `.adif`

例如：

```text
C:\Log\wsjtx_log.adi
```

自动生成：

```text
C:\Log\wsjtx_log-output.adi
```

如果输入文件为：

```text
C:\Log\satellite-2026.adi
```

则输出：

```text
C:\Log\satellite-2026-output.adi
```

# 9. 完整示例

## 示例 1：JO-97

```bash
python wsjtx_to_satlog.py --sat JO97 --input wsjtx_log.adi
或者
wsjtx_to_satlog.exe --sat JO97 --input wsjtx_log.adi
```

输出：

```text
Satellite : JO-97
Sat mode  : U/V
Input     : C:\Log\wsjtx_log.adi
Output    : C:\Log\wsjtx_log-output.adi
QSOs      : 128
```

---

## 示例 2：RS-44 并指定输出文件

```bash
python wsjtx_to_satlog.py --sat RS44 --input wsjtx_log.adi --output "D:\SatelliteLog\RS44-2026-09.adi"
或者
wsjtx_to_satlog.exe --sat RS44 --input wsjtx_log.adi --output "D:\SatelliteLog\RS44-2026-09.adi"
```

---

# 10. 输出 ADIF 示例

假设输入日志中存在：

```text
CALL      = JA1ABC
QSO_DATE  = 20260925
TIME_ON   = 123400
FREQ      = 145.857500
RST_SENT  = -10
RST_RCVD  = -08
```

转换后会包含类似：

```text
<QSO_DATE:8>20260925
<TIME_ON:6>123400
<CALL:6>JA1ABC
<FREQ:10>145.857500
<MODE:4>MFSK
<SUBMODE:3>FT4
<RST_SENT:3>-10
<RST_RCVD:3>-08
<PROP_MODE:3>SAT
<SAT_NAME:5>JO-97
<SAT_MODE:3>U/V
<EOR>
```

实际输出还会保留输入文件中的其他字段。

---

# 11. 卫星字段

## JO-97

```text
SAT_NAME = JO-97
SAT_MODE = U/V
```

## AO-73

```text
SAT_NAME = AO-73
SAT_MODE = U/V
```

## RS-44

```text
SAT_NAME = RS-44
SAT_MODE = V/U
```

所有记录：

```text
PROP_MODE = SAT
```

模式：

```text
MODE    = MFSK
SUBMODE = FT4
```

---

# 12. 错误处理

### 输入文件不存在

例如：

```text
Error: Input file not found: C:\Log\test.adi
```

请检查 `--input` 路径。

---

### 没有找到 QSO

例如：

```text
Error: No QSO records were found in the input file.
```

表示文件存在，但是没有找到可识别的 ADIF 或 CSV QSO 记录。

---

### 卫星参数错误

例如：

```bash
python wsjtx_to_satlog.py --sat FO99 --input wsjtx_log.adi
```

会提示：

```text
invalid choice
```

正确参数只能使用：

```text
JO97
AO73
RS44
```

或对应带连字符的名称。

---

# 14. Windows 使用建议

在 Windows 下推荐将：

```text
wsjtx_to_satlog.py
```

放在一个固定目录，例如：

```text
D:\RadioTools\SatelliteLog\
```

然后：

```powershell
cd D:\RadioTools\SatelliteLog
```

执行：

```powershell
python wsjtx_to_satlog.py --sat JO97 --input "D:\WSJT-X\wsjtx_log.adi"
```

路径包含空格时请使用双引号：

```powershell
python wsjtx_to_satlog.py --sat AO73 --input "D:\My Logs\wsjtx_log.adi"
```

---

# 15. 使用 Python 直接运行

完整命令：

```bash
python wsjtx_to_satlog.py --sat JO97 --input "C:\Log\wsjtx_log.adi" --output "C:\Log\JO97-FT4.adi"
```

也可以使用：

```bash
python3 wsjtx_to_satlog.py --sat JO97 --input wsjtx_log.adi
```

---

# 16. 直接运行EXE文件(推荐)

完整命令：

```bash
wsjtx_to_satlog.exe --sat JO97 --input "C:\Log\wsjtx_log.adi" --output "C:\Log\JO97-FT4.adi"
```

也可以使用：

```bash
wsjtx_to_satlog.exe --sat JO97 --input wsjtx_log.adi
```

---

# 17. 查看帮助

执行：

```bash
python wsjtx_to_satlog.py --help
或者
wsjtx_to_satlog.exe --help
```

会显示：

```text
usage: wsjtx_to_satlog.py [-h] --sat {JO97,AO73,RS44,JO-97,AO-73,RS-44}
                          --input INPUT [--output OUTPUT]

Convert WSJT-X FT4 logs to satellite FT4 ADIF logs.
```

---

# 17. 注意事项

本脚本主要用于**日志格式转换**，不会判断某条 QSO 是否真的发生在对应卫星过境时间内。

例如：

```bash
python wsjtx_to_satlog.py --sat RS44 --input wsjtx_log.adi
```

脚本会把输入记录标记为：

```text
SAT_NAME = RS-44
```

因此在实际使用时，请确认输入日志本身就是对应卫星的 FT4 通联记录。

另外，如果你的目标日志软件使用的是某一种**特定的卫星 ADIF 扩展格式**，建议用该软件导出一份正确的 sat log 作为模板，再针对该模板调整字段顺序或增加专用字段。

---

# 18. 常用命令速查

```bash
# JO-97
python wsjtx_to_satlog.py --sat JO97 --input wsjtx_log.adi

# AO-73
python wsjtx_to_satlog.py --sat AO73 --input wsjtx_log.adi

# RS-44
python wsjtx_to_satlog.py --sat RS44 --input wsjtx_log.adi

# 指定输出
python wsjtx_to_satlog.py --sat JO97 --input wsjtx_log.adi --output JO97.adi

# 直接转换 wsjtx.log
python wsjtx_to_satlog.py --sat AO73 --input wsjtx.log

# 查看帮助
python wsjtx_to_satlog.py --help
```

