# Vocabulary

> A local-first academic vocabulary collector for reading, research, and language learning.  
> 一个面向阅读、科研与英语学习的本地词汇管理工具。

Vocabulary 是一个轻量、跨平台、本地优先的英语词汇收集与管理工具。

它解决的是一个很具体的问题：阅读英文书籍、论文、网页或其他学习材料时，遇到不会的单词、短语和句子，希望可以快速记录、持续补充、搜索、编辑、统计并安全保存，而不是让这些内容散落在截图、聊天记录、纸质笔记和不同软件里。

Vocabulary 将学习记录集中保存在本地 SQLite 数据库中，并支持来源、章节、页码、上下文、重复遇到次数、搜索、编辑、回收站、自动备份和 CSV 导出。

---

## ✨ 核心特性

### 📚 Word / Phrase / Sentence

Vocabulary 支持三种学习内容：

- Word
- Phrase
- Sentence

每条记录可以保存：

- English
- 中文释义
- Type
- Source
- Chapter
- Page
- Context
- Times Asked / 遇到次数
- 创建时间
- 更新时间

适合：

- 英文原著阅读
- 学术论文阅读
- IELTS / TOEFL 学习
- 专业英语积累
- 研究生 / 博士阶段文献阅读
- 日常英语学习

---

## 📋 从剪贴板快速读取

阅读 PDF、网页、电子书或论文时，可以先复制英文内容，再点击：

**从剪贴板读取**

Vocabulary 会自动读取剪贴板内容，并根据文本长度辅助判断类型：

- 单个词 → Word
- 多个词 → Phrase
- 较长文本 → Sentence

这样可以减少重复输入。

---

## 🔁 重复检测与 Times Asked

Vocabulary 不会简单地把同一个词无限重复保存。

例如第一次记录：

```text
scaffolding
Times Asked: 1
```

再次遇到相同类型的 `scaffolding` 时，不会创建第二条相同记录，而是更新：

```text
Times Asked: 2
```

这意味着词库不仅是“收藏夹”，也能逐渐反映：

> 哪些词是你真正反复遇到、值得重点掌握的词。

---

## ✏️ 编辑已有记录

从 v1.1.0 开始，Vocabulary 支持直接编辑已有词条。

在词库列表中双击一条记录，上方表单会自动载入：

- English
- 中文释义
- Type
- Source
- Chapter
- Page
- Context

此时按钮会从：

```text
保存
```

变为：

```text
更新记录
```

编辑已有记录不会增加 `Times Asked`。

例如：

```text
scaffolding
Times Asked: 2
```

修改中文释义后，仍然保持：

```text
Times Asked: 2
```

这样可以避免把“修改资料”误认为“再次遇到”。

---

## 🔎 实时搜索

v1.1.0 支持实时搜索词库。

可以按以下字段进行模糊搜索：

- English
- 中文释义
- Source
- Chapter

例如输入：

```text
scaff
```

可以找到：

```text
scaffolding
```

也可以直接搜索中文释义、书名、论文来源或章节。

点击 **清除** 即可恢复完整词库。

---

## 🗑 回收站

Vocabulary 默认不直接物理删除学习记录。

删除时会先：

```text
移入回收站
```

被移入回收站的记录：

- 不再出现在主词库
- 不参与正常搜索
- 不计入正常词库统计
- 仍然保留在 SQLite 数据库中

你可以打开 **回收站**，选择记录后点击：

```text
恢复选中词条
```

将其恢复到主词库。

这种软删除设计可以降低长期学习过程中误删数据的风险。

---

## 💾 自动数据库备份

v1.1.0 内置 SQLite 数据库备份机制。

程序每天第一次启动时会自动创建一份数据库备份。

备份文件类似：

```text
vocabulary_2026-09-16_204959.db
```

默认最多保留最近 30 份备份，超出后自动清理旧备份，避免长期运行后无限占用磁盘空间。

备份使用 SQLite 自身的备份机制完成，而不是简单复制正在使用中的数据库文件。

---

## 🛡 手动备份

除了自动备份，还可以点击：

```text
立即备份
```

随时创建一个新的数据库快照。

适合在以下操作前使用：

- 大规模整理词库
- 批量修改数据
- 软件升级
- 导入大量内容

---

## 📤 CSV 导出

Vocabulary 支持将完整词库导出为 CSV。

点击：

```text
导出 CSV
```

会生成类似：

```text
Vocabulary_2026-09-16.csv
```

CSV 使用 UTF-8 with BOM，便于兼容：

- Microsoft Excel
- WPS
- Numbers
- Python
- R
- 其他数据分析工具

导出后的数据可以进一步用于：

- Anki 数据整理
- 学习统计
- Python / R 数据分析
- NLP 实验
- 学术研究
- 个人学习档案

---

## 🔒 Local-First

Vocabulary 是一个 **Local-First / 本地优先** 的应用。

核心学习数据默认保存在用户自己的电脑中。

程序不需要把你的词库上传到服务器，也不需要云端账号才能管理数据。

核心数据库：

```text
vocabulary.db
```

数据库格式：

```text
SQLite
```

---

## 📂 数据存储位置

### macOS

```text
~/Library/Application Support/Vocabulary/
```

典型结构：

```text
Vocabulary/
├── vocabulary.db
└── backups/
    ├── vocabulary_2026-09-16_204959.db
    ├── vocabulary_2026-09-16_205017.db
    └── ...
```

### Windows

默认：

```text
%LOCALAPPDATA%\Vocabulary\
```

例如：

```text
C:\Users\YourName\AppData\Local\Vocabulary\
```

### Linux

默认：

```text
~/.local/share/Vocabulary/
```

如果系统配置了 `XDG_DATA_HOME`，Vocabulary 会遵循该路径。

---

## 🔄 旧版本数据迁移

Vocabulary 支持从早期版本自动迁移数据库。

macOS 上会检查旧路径，例如：

```text
~/Library/Application Support/CambridgeVocabulary/vocabulary.db
```

以及：

```text
~/Documents/CambridgeLearningSciences/vocabulary.db
```

如果新数据库尚不存在、旧数据库存在，程序会自动复制旧数据库到新的 Vocabulary 数据目录。

这样升级软件时不需要重新建立词库。

---

## 🚀 从源码运行

### 推荐环境

```text
Python 3.13+
```

Vocabulary 当前主要依赖 Python 标准库：

- tkinter
- sqlite3
- csv
- pathlib
- shutil
- subprocess

一般不需要额外安装运行时依赖。

### macOS

```bash
git clone https://github.com/flyallz/Vocabulary.git
cd Vocabulary
python3 src/app.py
```

### Windows

```powershell
git clone https://github.com/flyallz/Vocabulary.git
cd Vocabulary
python src\app.py
```

如果系统使用 `py` 启动器：

```powershell
py src\app.py
```

---

## 🏗 构建桌面应用

Vocabulary 使用 PyInstaller 生成桌面应用。

构建依赖记录在：

```text
requirements-build.txt
```

当前构建依赖：

```text
pyinstaller==6.22.3
```

安装：

```bash
python3 -m pip install -r requirements-build.txt
```

### macOS

项目已经验证可构建为 Universal 2 应用，同时支持：

```text
x86_64 + arm64
```

因此同一个 `.app` 可以兼容 Intel Mac 和 Apple Silicon Mac。

应用图标：

```text
assets/Vocabulary.icns
```

### Windows

程序代码已经按跨平台数据路径设计。

Windows `.exe` 需要在 Windows 环境中使用 PyInstaller 构建。

PyInstaller 不适合直接在 macOS 上交叉生成 Windows 可执行文件。

未来可以通过 GitHub Actions 自动构建 macOS 和 Windows 版本。

---

## 📁 项目结构

```text
Vocabulary/
├── assets/
│   ├── icon.png
│   └── Vocabulary.icns
├── src/
│   └── app.py
├── VERSION
├── requirements-build.txt
├── .gitignore
└── README.md
```

当前主要应用入口：

```text
src/app.py
```

---

## 🗄 数据库结构

Vocabulary 使用 SQLite 作为本地数据库。

核心表：

```text
vocabulary
```

主要字段包括：

```text
id
created_at
updated_at
item_type
english
chinese
english_explanation
context
source
chapter
page
status
review_count
times_asked
notes
deleted_at
```

其中：

```text
deleted_at
```

用于实现软删除和回收站。

---

## 📊 推荐使用工作流

```text
阅读书籍 / 论文
        ↓
遇到不会的词或表达
        ↓
复制英文
        ↓
Vocabulary
        ↓
从剪贴板读取
        ↓
填写中文 / 来源 / 章节 / 页码 / 上下文
        ↓
保存
        ↓
再次遇到
        ↓
Times Asked +1
        ↓
形成个人高频学术词库
```

Vocabulary 的目标并不是建立一个巨大的通用英语词典。

它更关注：

> 建立一个属于你自己的、由真实阅读行为产生的词汇数据库。

---

## 🧠 为什么做 Vocabulary？

传统单词软件通常从别人准备好的词表开始学习。

Vocabulary 的思路相反：

```text
你真正阅读的内容
        ↓
你真正不认识的表达
        ↓
你真正反复遇到的词
        ↓
形成自己的词汇库
```

因此它更适合：

- 深度阅读
- 学术英语
- 研究生学习
- 博士阶段文献阅读
- 专业领域术语积累
- 长期语言学习

---

## 🧪 Version History

### v1.1.0

目标版本：将 Vocabulary 从简单的词汇采集器升级为基础词汇管理系统。

新增：

- 编辑已有记录
- 实时搜索
- 回收站
- 恢复删除记录
- 自动数据库备份
- 手动数据库备份
- 自动清理旧备份

继续保留：

- Word / Phrase / Sentence
- Clipboard Capture
- Duplicate Detection
- Times Asked
- Source
- Chapter
- Page
- Context
- CSV Export
- Local SQLite Storage
- Cross-platform Data Paths

### v1.0.0

第一个正式版本。

核心功能：

- 本地 SQLite 词库
- Word / Phrase / Sentence
- 中文释义
- Source / Chapter / Page
- Context
- 剪贴板读取
- 重复检测
- Times Asked
- CSV 导出
- macOS / Windows 数据路径支持
- macOS Universal 2 构建验证

---

## 🗺 Roadmap

未来可能继续探索：

- 学习状态管理
- 熟练度
- 收藏 / Star
- 标签系统
- 按 Source 分类浏览
- 按书籍建立词库
- 高频词分析
- 学习统计
- 每日复习
- 间隔重复
- Anki 导出
- Markdown 导出
- JSON 导出
- 数据可视化
- AI 辅助释义
- AI 自动生成例句
- AI 自动解释学术语境
- PDF / EPUB 阅读工作流整合

Vocabulary 会继续坚持一个原则：

> 核心学习数据应该属于用户自己。

---

## 🔐 Privacy

**Your vocabulary belongs to you.**

词汇、阅读来源、章节、页码和上下文默认保存在本地数据库中。

Vocabulary 不要求用户创建云端账号，也不依赖远程服务器才能管理自己的词库。

---

## 🤝 Contributing

Vocabulary 目前仍处于持续开发阶段。

如果你发现：

- Bug
- UI 问题
- 数据库问题
- macOS / Windows 兼容问题

欢迎通过 GitHub Issues 提交反馈。

开发新功能时建议保持 `main` 为稳定分支，在独立 feature 分支开发并测试完成后再合并。

---

## 📌 Current Development Target

```text
Vocabulary v1.1.0
```

Local Academic Vocabulary Collector  
本地学术词汇库

---

Made for reading, research, and lifelong language learning.
