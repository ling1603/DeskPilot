# DeskPilot

> A lightweight desktop file organizer for Windows.  
> 一个基于 Python 的轻量级文件整理工具，帮助你按规则自动归类文件夹中的杂乱文件。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Version](https://img.shields.io/badge/Version-v1.0-brightgreen)
![License](https://img.shields.io/badge/License-Unspecified-orange)

DeskPilot 是一个本地运行的桌面文件整理工具。它可以扫描指定文件夹中的文件，根据扩展名规则将文件移动到对应分类目录，并提供撤销、整理记录、运行统计、系统托盘等辅助功能。

> 注意：当前项目以本地文件整理为核心，不会上传、同步或分析你的文件内容。

---

## 界面预览

> 建议后续在 `docs/images/` 目录中放入以下截图：

| 截图位置 | 建议内容 |
| --- | --- |
| `docs/images/main-window.png` | 主窗口整体界面：整理按钮、运行状态、统计信息、日志区域 |
| `docs/images/rules-editor.png` | 分类规则编辑器界面 |
| `docs/images/tray-menu.png` | 系统托盘菜单：显示窗口 / 退出程序 |
| `docs/images/organize-result.png` | 整理完成后的文件夹分类效果 |

示例写法：

```md
<p align="center">
  <img src="docs/images/main-window.png" width="720" alt="DeskPilot 主窗口">
</p>
```

---

## Features / 项目亮点

- 📁 **按规则整理文件**：根据扩展名将文件归类到图片、文档、表格、视频、压缩包、代码等文件夹。
- ↩️ **支持撤销上一次整理**：最近一次整理操作可以回退，降低误操作风险。
- 📊 **本地统计信息**：记录累计整理文件数、手动整理次数、监控触发次数。
- 🧾 **整理日志与记录**：在界面中显示整理过程、跳过文件、最近操作记录。
- 🧩 **JSON 规则配置**：通过 `rules.json` 配置分类规则，支持扩展名和关键词字段。
- 🖥️ **系统托盘支持**：关闭窗口时可隐藏到托盘，并通过托盘菜单恢复或退出。
- 👀 **文件夹监控能力**：Pro 模式下可监控指定文件夹中新建文件，并自动触发整理。
- 🔐 **Free / Pro 功能门禁**：代码中内置 Free / Pro 功能控制逻辑，便于后续扩展商业版或高级版。

---

## 适用场景

DeskPilot 适合这些场景：

- 下载文件夹长期堆积，想快速按类型分类；
- 桌面文件杂乱，需要定期清理；
- 学习、办公中经常产生 PDF、Word、Excel、图片、压缩包等混合文件；
- 想做一个轻量级 Python 桌面应用项目作为练习或开源展示；
- 希望基于 Tkinter、watchdog、pystray 学习桌面工具开发。

---

## 功能说明

| 功能 | 说明 |
| --- | --- |
| 手动整理文件夹 | 点击“整理文件”，选择目标文件夹，程序会扫描该文件夹根目录下的文件并分类 |
| 分类规则匹配 | 根据文件扩展名匹配 `rules.json` 中的分类规则 |
| 关键词匹配 | Pro 模式下可根据文件名关键词进一步匹配分类 |
| 自动处理重名 | 若目标文件夹中已有同名文件，会自动生成 `文件名(1).扩展名` |
| 撤销上一次整理 | 将最近一次移动的文件批量移回原位置 |
| 运行统计 | 显示累计整理文件数、手动整理次数、监控触发次数 |
| 整理记录 | 在界面中展示最近整理批次和示例文件 |
| 日志输出 | 显示整理过程、跳过文件、错误信息等 |
| 系统托盘 | 支持最小化到托盘、显示窗口、退出程序 |
| 文件夹监控 | Pro 模式下监听指定文件夹中新建文件，并自动整理 |

---

## 技术栈

| 类型 | 技术 |
| --- | --- |
| 编程语言 | Python |
| GUI 框架 | Tkinter |
| 文件监听 | watchdog |
| 系统托盘 | pystray |
| 图标处理 | Pillow |
| 配置格式 | JSON |
| 文件操作 | os / shutil |
| 并发与防抖 | threading |
| 数据模型 | dataclasses |

---

## 安装方法

### 1. 克隆项目

```bash
git clone https://github.com/ling1603/DeskPilot.git
cd DeskPilot
```

### 2. 创建虚拟环境

Windows PowerShell：

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

依赖主要包括：

```txt
pystray
Pillow
watchdog
```

Tkinter 通常随 Python 一起安装。若你的系统缺少 Tkinter，需要根据系统环境单独安装。

---

## 运行方法

### 源码运行

```bash
python main.py
```

如果你遇到类似错误：

```txt
ModuleNotFoundError: No module named 'ui'
ModuleNotFoundError: No module named 'config'
ModuleNotFoundError: No module named 'services'
```

说明当前仓库文件结构可能还没有整理成代码中 import 所期望的包结构。请参考下方“项目结构”部分，将文件放入对应目录后再运行。

---

## 使用步骤

1. 启动程序：

   ```bash
   python main.py
   ```

2. 点击主界面的 **“整理文件”**。

3. 选择需要整理的文件夹，例如桌面、下载目录或某个临时文件夹。

4. DeskPilot 会扫描该文件夹根目录下的文件，并根据规则创建分类子文件夹。

5. 查看界面中的整理记录、日志、统计信息。

6. 如果整理结果不符合预期，可以点击 **“撤销”** 回退最近一次整理。

7. Pro 模式下，可以点击 **“自动整理”**，选择需要监控的文件夹。之后当该文件夹中新建文件时，程序会自动整理。

---

## 项目结构

代码中的 import 路径更适合下面这种模块化结构：

```txt
DeskPilot/
├── main.py                    # 程序入口
├── requirements.txt           # Python 依赖
├── README.md                  # 项目说明文档
│
├── config/
│   ├── settings.py            # 应用配置、默认规则、窗口参数
│   ├── rules.json             # 默认分类规则
│   ├── license.py             # Free / Pro 版本配置加载
│   └── license.json           # 当前版本配置
│
├── models/
│   └── operation.py           # 文件移动记录与批次模型
│
├── services/
│   ├── organizer.py           # 文件整理核心逻辑
│   ├── monitor_service.py     # 文件夹监控服务
│   ├── undo_manager.py        # 撤销管理
│   ├── stats_service.py       # 本地统计服务
│   └── feature_gate.py        # Free / Pro 功能门禁
│
├── ui/
│   ├── main_window.py         # Tkinter 主窗口
│   └── rule_editor.py         # 分类规则编辑器
│
├── utils/
│   ├── helpers.py             # 路径与资源工具函数
│   ├── tray_manager.py        # 系统托盘管理
│   └── autostart.py           # Windows 开机自启动管理
│
└── assets/
    ├── app.png                # 应用图标
    └── app.ico                # Windows 图标
```

---

## 配置规则说明

DeskPilot 使用 JSON 文件配置分类规则。规则文件示例：

```json
{
  "_说明": "文件分类规则，支持 extensions 和 keywords",
  "图片": {
    "extensions": ["jpg", "png", "jpeg"],
    "keywords": ["screenshot", "截图", "photo", "照片"]
  },
  "文档": {
    "extensions": ["pdf", "docx", "txt"],
    "keywords": ["report", "报告", "doc", "文档"]
  },
  "表格": {
    "extensions": ["xlsx", "csv"],
    "keywords": ["data", "数据", "统计"]
  },
  "视频": {
    "extensions": ["mp4", "mov"],
    "keywords": ["video", "视频", "record"]
  },
  "压缩包": {
    "extensions": ["zip", "rar", "7z"],
    "keywords": ["backup", "备份"]
  },
  "代码": {
    "extensions": ["py", "js", "html", "css"],
    "keywords": ["script", "脚本", "code"]
  }
}
```

### 字段说明

| 字段 | 说明 |
| --- | --- |
| 分类名 | 最终创建的文件夹名称，例如“图片”“文档”“代码” |
| `extensions` | 按扩展名匹配，扩展名不需要写点号 |
| `keywords` | 按文件名关键词匹配，当前属于 Pro 功能 |
| `_说明` | 辅助说明字段，程序会自动忽略以下划线开头的键 |

### 匹配优先级

当前逻辑优先按扩展名匹配；如果扩展名未匹配，并且当前版本支持关键词匹配，再尝试按文件名关键词匹配。

---

## Free / Pro 功能说明

当前代码中已经存在 Free / Pro 版本控制逻辑，默认版本为 Free。

| 功能 | Free | Pro |
| --- | --- | --- |
| 手动整理文件夹 | ✅ | ✅ |
| 按扩展名分类 | ✅ | ✅ |
| 自动处理重名文件 | ✅ | ✅ |
| 撤销上一次整理 | ✅ | ✅ |
| 整理日志 | ✅ | ✅ |
| 本地统计 | ✅ | ✅ |
| 系统托盘 | ✅ | ✅ |
| 文件夹自动监控 | ❌ | ✅ |
| 文件名关键词匹配 | ❌ | ✅ |
| 图形化规则编辑器 | ❌ | ✅ |

开发测试时，版本由 `license.json` 中的字段控制：

```json
{
  "version": "free"
}
```

可选值：

```json
{
  "version": "pro"
}
```

> 注意：当前授权逻辑更适合开发演示或功能分层测试。若用于正式发布，建议补充更完整的授权、签名或账号体系。

---

## Roadmap

后续可以考虑改进：

- [ ] 规范仓库目录结构，使源码可以直接运行；
- [ ] 补充正式 `LICENSE` 文件；
- [ ] 增加项目截图和 GIF 演示；
- [ ] 提供 Windows 可执行文件下载说明；
- [ ] 增加 PyInstaller 打包脚本；
- [ ] 支持默认监控桌面和下载文件夹；
- [ ] 支持递归整理子目录；
- [ ] 增加规则导入、导出、恢复默认规则；
- [ ] 增加整理前预览模式；
- [ ] 增加单元测试和 GitHub Actions；
- [ ] 优化撤销逻辑，支持跨会话撤销记录；
- [ ] 增加多语言界面或英文 README。

---

## FAQ

### 1. DeskPilot 会删除我的文件吗？

不会。当前核心逻辑是移动文件到分类子文件夹，而不是删除文件。仍然建议先在测试文件夹中试用，确认规则符合预期后再整理重要目录。

### 2. 为什么运行 `python main.py` 报 `ModuleNotFoundError`？

当前代码使用了 `ui`、`config`、`services`、`models`、`utils` 等包路径。如果仓库中的文件仍然全部放在根目录，需要先按“项目结构”部分整理目录。

### 3. 为什么“自动整理”点不了或提示需要 Pro？

代码中将自动监控设置为 Pro 功能。默认 `license.json` 是 Free，因此会被功能门禁拦截。

### 4. 规则修改后为什么没有生效？

如果直接编辑 `rules.json`，建议重启程序后再试。Pro 模式下通过“分类设置”保存规则后，程序会重新加载规则。

### 5. 会整理子文件夹里的文件吗？

当前逻辑主要处理目标文件夹根目录下的文件，不会递归整理子文件夹中的内容。

### 6. 为什么没有托盘图标？

系统托盘依赖 `pystray`、`Pillow` 和应用图标文件。如果缺少 `app.png` 或当前系统不支持托盘，程序会跳过托盘功能，不影响手动整理。

### 7. 撤销记录会在重启后保留吗？

当前撤销历史由内存中的 `UndoManager` 管理，重启程序后不会保留历史记录。

---

## 许可证说明

当前仓库暂未明确开源协议。

仓库中的 `license.py` 和 `license.json` 是 Free / Pro 版本控制相关文件，不等同于开源协议文件。建议作者后续补充正式的 `LICENSE` 文件，例如 MIT、Apache-2.0、GPL 等，并在 README 中同步说明。

在未添加明确开源协议前，其他人不应默认认为该项目可以自由商用、修改或分发。

---

## 致谢 / Author

作者：[@ling1603](https://github.com/ling1603)

感谢以下 Python 生态工具：

- Tkinter
- watchdog
- pystray
- Pillow

如果这个项目对你有帮助，欢迎 Star、Fork 或提出 Issue。
