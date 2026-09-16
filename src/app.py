import csv
import os
import platform
import shutil
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


APP_NAME = "Vocabulary"
APP_VERSION = "1.1.0-dev"


def get_app_data_dir():
    system = platform.system()

    if system == "Darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / APP_NAME
        )

    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")

        if local_app_data:
            return Path(local_app_data) / APP_NAME

        return (
            Path.home()
            / "AppData"
            / "Local"
            / APP_NAME
        )

    xdg_data_home = os.environ.get("XDG_DATA_HOME")

    if xdg_data_home:
        return Path(xdg_data_home) / APP_NAME

    return (
        Path.home()
        / ".local"
        / "share"
        / APP_NAME
    )


APP_DIR = get_app_data_dir()
DB_PATH = APP_DIR / "vocabulary.db"
BACKUP_DIR = APP_DIR / "backups"


def get_legacy_databases():
    legacy = []

    if platform.system() == "Darwin":
        legacy.append(
            Path.home()
            / "Library"
            / "Application Support"
            / "CambridgeVocabulary"
            / "vocabulary.db"
        )

        legacy.append(
            Path.home()
            / "Documents"
            / "CambridgeLearningSciences"
            / "vocabulary.db"
        )

    return legacy


def prepare_storage():
    APP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if DB_PATH.exists():
        return

    for legacy_db in get_legacy_databases():
        if legacy_db.exists():
            shutil.copy2(
                legacy_db,
                DB_PATH
            )
            break


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def cleanup_backups(max_backups=30):
    if not BACKUP_DIR.exists():
        return

    backups = sorted(
        BACKUP_DIR.glob("vocabulary_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    for old_backup in backups[max_backups:]:
        try:
            old_backup.unlink()
        except OSError:
            pass


def create_backup(force=False):
    prepare_storage()

    if not DB_PATH.exists():
        return None

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    if not force:
        existing_today = list(
            BACKUP_DIR.glob(
                f"vocabulary_{today}_*.db"
            )
        )

        if existing_today:
            latest = max(
                existing_today,
                key=lambda p: p.stat().st_mtime
            )
            return latest

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H%M%S"
    )

    backup_path = (
        BACKUP_DIR
        / f"vocabulary_{timestamp}.db"
    )

    source_conn = sqlite3.connect(
        DB_PATH
    )

    backup_conn = sqlite3.connect(
        backup_path
    )

    try:
        source_conn.backup(
            backup_conn
        )
    finally:
        backup_conn.close()
        source_conn.close()

    cleanup_backups(
        max_backups=30
    )

    return backup_path


def init_db():
    prepare_storage()

    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            item_type TEXT NOT NULL,
            english TEXT NOT NULL,
            chinese TEXT,
            english_explanation TEXT,
            context TEXT,
            source TEXT,
            chapter TEXT,
            page TEXT,
            status TEXT DEFAULT 'New',
            review_count INTEGER DEFAULT 0,
            times_asked INTEGER DEFAULT 1,
            notes TEXT
        )
        """)

        existing_columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(vocabulary)"
            ).fetchall()
        }

        required_columns = {
            "updated_at": "TEXT",
            "english_explanation": "TEXT",
            "context": "TEXT",
            "source": "TEXT",
            "chapter": "TEXT",
            "page": "TEXT",
            "status": "TEXT DEFAULT 'New'",
            "review_count": "INTEGER DEFAULT 0",
            "times_asked": "INTEGER DEFAULT 1",
            "notes": "TEXT",
            "deleted_at": "TEXT",
        }

        for column, definition in required_columns.items():
            if column not in existing_columns:
                conn.execute(
                    f"""
                    ALTER TABLE vocabulary
                    ADD COLUMN {column} {definition}
                    """
                )


def open_folder(path):
    system = platform.system()

    try:
        if system == "Darwin":
            subprocess.run(
                ["open", str(path)]
            )

        elif system == "Windows":
            os.startfile(str(path))

        else:
            subprocess.run(
                ["xdg-open", str(path)]
            )

    except Exception as exc:
        messagebox.showerror(
            "无法打开目录",
            str(exc)
        )


class VocabularyApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(
            f"{APP_NAME} {APP_VERSION}"
        )

        self.geometry("1000x760")
        self.minsize(850, 650)

        try:
            ttk.Style().theme_use("aqua")
        except tk.TclError:
            pass

        self.editing_id = None

        self.create_widgets()
        self.refresh_all()

        self.english_entry.focus_set()

    def create_widgets(self):
        main = ttk.Frame(
            self,
            padding=22
        )

        main.pack(
            fill="both",
            expand=True
        )

        main.columnconfigure(
            1,
            weight=1
        )

        main.rowconfigure(
            10,
            weight=1
        )

        title = ttk.Label(
            main,
            text="Vocabulary",
            font=(
                "Helvetica",
                24,
                "bold"
            )
        )

        title.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w"
        )

        subtitle = ttk.Label(
            main,
            text=(
                "Local Academic Vocabulary Collector"
                "  ·  本地学术词汇库"
            )
        )

        subtitle.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(4, 20)
        )

        # English
        ttk.Label(
            main,
            text="English"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=5
        )

        self.english_var = tk.StringVar()

        self.english_entry = ttk.Entry(
            main,
            textvariable=self.english_var,
            font=("Helvetica", 14)
        )

        self.english_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(12, 8),
            pady=5
        )

        ttk.Button(
            main,
            text="从剪贴板读取",
            command=self.load_clipboard
        ).grid(
            row=2,
            column=2,
            sticky="ew",
            pady=5
        )

        # Type
        ttk.Label(
            main,
            text="Type"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=5
        )

        self.type_var = tk.StringVar(
            value="Word"
        )

        self.type_combo = ttk.Combobox(
            main,
            textvariable=self.type_var,
            values=[
                "Word",
                "Phrase",
                "Sentence"
            ],
            state="readonly",
            width=18
        )

        self.type_combo.grid(
            row=3,
            column=1,
            sticky="w",
            padx=(12, 8),
            pady=5
        )

        # Chinese
        ttk.Label(
            main,
            text="中文释义"
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=5
        )

        self.chinese_var = tk.StringVar()

        ttk.Entry(
            main,
            textvariable=self.chinese_var
        ).grid(
            row=4,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(12, 0),
            pady=5
        )

        # Source
        ttk.Label(
            main,
            text="来源 Source"
        ).grid(
            row=5,
            column=0,
            sticky="w",
            pady=5
        )

        self.source_var = tk.StringVar()

        ttk.Entry(
            main,
            textvariable=self.source_var
        ).grid(
            row=5,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(12, 0),
            pady=5
        )

        # Chapter and page
        ttk.Label(
            main,
            text="章节"
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=5
        )

        meta_frame = ttk.Frame(main)

        meta_frame.grid(
            row=6,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(12, 0),
            pady=5
        )

        meta_frame.columnconfigure(
            0,
            weight=1
        )

        self.chapter_var = tk.StringVar()
        self.page_var = tk.StringVar()

        ttk.Entry(
            meta_frame,
            textvariable=self.chapter_var
        ).grid(
            row=0,
            column=0,
            sticky="ew"
        )

        ttk.Label(
            meta_frame,
            text="页码"
        ).grid(
            row=0,
            column=1,
            padx=(18, 8)
        )

        ttk.Entry(
            meta_frame,
            textvariable=self.page_var,
            width=12
        ).grid(
            row=0,
            column=2
        )

        # Context
        ttk.Label(
            main,
            text="上下文"
        ).grid(
            row=7,
            column=0,
            sticky="nw",
            pady=5
        )

        self.context_text = tk.Text(
            main,
            height=5,
            wrap="word"
        )

        self.context_text.grid(
            row=7,
            column=1,
            columnspan=2,
            sticky="ew",
            padx=(12, 0),
            pady=5
        )

        # Buttons
        button_frame = ttk.Frame(main)

        button_frame.grid(
            row=8,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(15, 18)
        )

        self.save_button = ttk.Button(
            button_frame,
            text="保存",
            command=self.save_item
        )

        self.save_button.pack(
            side="left"
        )

        self.cancel_edit_button = ttk.Button(
            button_frame,
            text="取消编辑",
            command=self.cancel_edit,
            state="disabled"
        )

        self.cancel_edit_button.pack(
            side="left",
            padx=8
        )

        self.delete_button = ttk.Button(
            button_frame,
            text="移入回收站",
            command=self.move_to_trash,
            state="disabled"
        )

        self.delete_button.pack(
            side="left",
            padx=8
        )

        ttk.Button(
            button_frame,
            text="清空",
            command=self.clear_form
        ).pack(
            side="left",
            padx=8
        )

        ttk.Button(
            button_frame,
            text="打开数据目录",
            command=lambda: open_folder(
                APP_DIR
            )
        ).pack(
            side="left",
            padx=8
        )

        ttk.Button(
            button_frame,
            text="立即备份",
            command=self.manual_backup
        ).pack(
            side="left",
            padx=8
        )

        ttk.Button(
            button_frame,
            text="导出 CSV",
            command=self.export_csv
        ).pack(
            side="right"
        )

        ttk.Button(
            button_frame,
            text="回收站",
            command=self.open_trash
        ).pack(
            side="right",
            padx=8
        )

        # Recent records + search
        history_header = ttk.Frame(main)

        history_header.grid(
            row=9,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(0, 8)
        )

        history_header.columnconfigure(
            1,
            weight=1
        )

        ttk.Label(
            history_header,
            text="最近记录",
            font=(
                "Helvetica",
                13,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        search_frame = ttk.Frame(
            history_header
        )

        search_frame.grid(
            row=0,
            column=1,
            sticky="e"
        )

        ttk.Label(
            search_frame,
            text="搜索"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.search_var = tk.StringVar()

        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=28
        )

        self.search_entry.pack(
            side="left"
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh_history()
        )

        ttk.Button(
            search_frame,
            text="清除",
            command=self.clear_search
        ).pack(
            side="left",
            padx=(8, 0)
        )

        history_frame = ttk.Frame(main)

        history_frame.grid(
            row=10,
            column=0,
            columnspan=3,
            sticky="nsew"
        )

        history_frame.columnconfigure(
            0,
            weight=1
        )

        history_frame.rowconfigure(
            0,
            weight=1
        )

        columns = (
            "english",
            "chinese",
            "type",
            "count",
            "source",
            "chapter"
        )

        self.tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "english": "English",
            "chinese": "中文",
            "type": "Type",
            "count": "遇到次数",
            "source": "Source",
            "chapter": "Chapter"
        }

        widths = {
            "english": 180,
            "chinese": 180,
            "type": 80,
            "count": 80,
            "source": 220,
            "chapter": 130
        }

        for column in columns:
            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=widths[column]
            )

        scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.bind(
            "<Double-1>",
            self.begin_edit
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.status_var = tk.StringVar()

        ttk.Label(
            main,
            textvariable=self.status_var
        ).grid(
            row=11,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(12, 0)
        )

    def manual_backup(self):
        try:
            backup_path = create_backup(
                force=True
            )
        except Exception as exc:
            messagebox.showerror(
                "备份失败",
                str(exc)
            )
            return

        if backup_path is None:
            messagebox.showwarning(
                "没有数据库",
                "当前没有可备份的数据。"
            )
            return

        messagebox.showinfo(
            "备份完成",
            (
                "数据库已经安全备份。\n\n"
                f"{backup_path}"
            )
        )


    def load_clipboard(self):
        try:
            text = self.clipboard_get().strip()
        except tk.TclError:
            return

        if not text:
            return

        if len(text) > 5000:
            messagebox.showwarning(
                "内容过长",
                "剪贴板内容过长，未自动导入。"
            )
            return

        self.english_var.set(text)

        word_count = len(
            text.split()
        )

        if "\n" in text or word_count > 8:
            self.type_var.set(
                "Sentence"
            )
        elif word_count > 1:
            self.type_var.set(
                "Phrase"
            )
        else:
            self.type_var.set(
                "Word"
            )

    def save_item(self):
        english = (
            self.english_var
            .get()
            .strip()
        )

        if not english:
            messagebox.showwarning(
                "缺少内容",
                "请输入英文内容。"
            )
            return

        item_type = {
            "Word": "word",
            "Phrase": "phrase",
            "Sentence": "sentence"
        }[
            self.type_var.get()
        ]

        chinese = (
            self.chinese_var
            .get()
            .strip()
        )

        source = (
            self.source_var
            .get()
            .strip()
        )

        chapter = (
            self.chapter_var
            .get()
            .strip()
        )

        page = (
            self.page_var
            .get()
            .strip()
        )

        context = (
            self.context_text
            .get("1.0", "end")
            .strip()
        )

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        if self.editing_id is not None:
            self.update_item(
                item_type=item_type,
                english=english,
                chinese=chinese,
                source=source,
                chapter=chapter,
                page=page,
                context=context,
                now=now
            )
            return

        with connect() as conn:
            existing = conn.execute("""
                SELECT *
                FROM vocabulary
                WHERE item_type = ?
                  AND LOWER(TRIM(english))
                      = LOWER(TRIM(?))
                LIMIT 1
            """, (
                item_type,
                english
            )).fetchone()

            if existing:
                count = (
                    existing["times_asked"]
                    or 1
                ) + 1

                conn.execute("""
                    UPDATE vocabulary
                    SET
                        times_asked = ?,
                        updated_at = ?,

                        chinese =
                        CASE
                            WHEN ? != ''
                            THEN ?
                            ELSE chinese
                        END,

                        source =
                        CASE
                            WHEN ? != ''
                            THEN ?
                            ELSE source
                        END,

                        chapter =
                        CASE
                            WHEN ? != ''
                            THEN ?
                            ELSE chapter
                        END,

                        page =
                        CASE
                            WHEN ? != ''
                            THEN ?
                            ELSE page
                        END,

                        context =
                        CASE
                            WHEN ? != ''
                            THEN ?
                            ELSE context
                        END

                    WHERE id = ?
                """, (
                    count,
                    now,

                    chinese,
                    chinese,

                    source,
                    source,

                    chapter,
                    chapter,

                    page,
                    page,

                    context,
                    context,

                    existing["id"]
                ))

                messagebox.showinfo(
                    "已经收录过",
                    (
                        f"{english}\n\n"
                        f"这是第 {count} 次"
                        "遇到它。"
                    )
                )

            else:
                conn.execute("""
                    INSERT INTO vocabulary (
                        created_at,
                        updated_at,
                        item_type,
                        english,
                        chinese,
                        source,
                        chapter,
                        page,
                        context,
                        times_asked
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, 1
                    )
                """, (
                    now,
                    now,
                    item_type,
                    english,
                    chinese,
                    source,
                    chapter,
                    page,
                    context
                ))

                messagebox.showinfo(
                    "保存成功",
                    f"{english}\n\n已加入词库。"
                )

        self.refresh_all()

        self.clear_form(
            keep_source=True,
            keep_chapter=True
        )

    def begin_edit(self, event=None):
        selection = self.tree.selection()

        if not selection:
            return

        record_id = int(selection[0])

        with connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM vocabulary
                WHERE id = ?
                """,
                (record_id,)
            ).fetchone()

        if row is None:
            messagebox.showwarning(
                "记录不存在",
                "这条记录可能已经不存在。"
            )
            self.refresh_all()
            return

        type_map = {
            "word": "Word",
            "phrase": "Phrase",
            "sentence": "Sentence"
        }

        self.editing_id = record_id

        self.english_var.set(
            row["english"] or ""
        )

        self.chinese_var.set(
            row["chinese"] or ""
        )

        self.type_var.set(
            type_map.get(
                row["item_type"],
                "Word"
            )
        )

        self.source_var.set(
            row["source"] or ""
        )

        self.chapter_var.set(
            row["chapter"] or ""
        )

        self.page_var.set(
            row["page"] or ""
        )

        self.context_text.delete(
            "1.0",
            "end"
        )

        self.context_text.insert(
            "1.0",
            row["context"] or ""
        )

        self.save_button.configure(
            text="更新记录"
        )

        self.cancel_edit_button.configure(
            state="normal"
        )

        self.delete_button.configure(
            state="normal"
        )

        self.status_var.set(
            f"正在编辑 #{record_id}"
            f"  ·  {row['english']}"
            "  ·  修改不会增加遇到次数"
        )

        self.english_entry.focus_set()


    def update_item(
        self,
        *,
        item_type,
        english,
        chinese,
        source,
        chapter,
        page,
        context,
        now
    ):
        record_id = self.editing_id

        with connect() as conn:

            duplicate = conn.execute(
                """
                SELECT id
                FROM vocabulary

                WHERE id != ?
                  AND item_type = ?
                  AND LOWER(TRIM(english))
                      = LOWER(TRIM(?))

                LIMIT 1
                """,
                (
                    record_id,
                    item_type,
                    english
                )
            ).fetchone()

            if duplicate:
                messagebox.showwarning(
                    "存在重复记录",
                    (
                        f"已经存在另一条相同类型的"
                        f"“{english}”。\n\n"
                        "请修改英文内容，"
                        "或取消本次编辑。"
                    )
                )
                return

            conn.execute(
                """
                UPDATE vocabulary

                SET
                    item_type = ?,
                    english = ?,
                    chinese = ?,
                    source = ?,
                    chapter = ?,
                    page = ?,
                    context = ?,
                    updated_at = ?

                WHERE id = ?
                """,
                (
                    item_type,
                    english,
                    chinese,
                    source,
                    chapter,
                    page,
                    context,
                    now,
                    record_id
                )
            )

        messagebox.showinfo(
            "更新成功",
            (
                f"{english}\n\n"
                "记录已经更新。\n"
                "遇到次数保持不变。"
            )
        )

        self.clear_form()
        self.refresh_all()


    def cancel_edit(self):
        self.clear_form()
        self.refresh_all()


    def move_to_trash(self):
        if self.editing_id is None:
            return

        english = (
            self.english_var
            .get()
            .strip()
        )

        confirmed = messagebox.askyesno(
            "移入回收站",
            (
                f"确定要将“{english}”"
                "移入回收站吗？\n\n"
                "之后可以恢复。"
            )
        )

        if not confirmed:
            return

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        with connect() as conn:
            conn.execute(
                """
                UPDATE vocabulary
                SET
                    deleted_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    now,
                    now,
                    self.editing_id
                )
            )

        self.clear_form()
        self.refresh_all()

        messagebox.showinfo(
            "已移入回收站",
            f"{english}\n\n可以从回收站恢复。"
        )


    def open_trash(self):
        window = tk.Toplevel(self)
        window.title("Vocabulary 回收站")
        window.geometry("760x420")
        window.minsize(650, 350)

        frame = ttk.Frame(
            window,
            padding=16
        )

        frame.pack(
            fill="both",
            expand=True
        )

        frame.columnconfigure(
            0,
            weight=1
        )

        frame.rowconfigure(
            1,
            weight=1
        )

        ttk.Label(
            frame,
            text="回收站",
            font=(
                "Helvetica",
                18,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 12)
        )

        columns = (
            "english",
            "chinese",
            "type",
            "deleted"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        tree.heading(
            "english",
            text="English"
        )

        tree.heading(
            "chinese",
            text="中文"
        )

        tree.heading(
            "type",
            text="Type"
        )

        tree.heading(
            "deleted",
            text="删除时间"
        )

        tree.column(
            "english",
            width=190
        )

        tree.column(
            "chinese",
            width=190
        )

        tree.column(
            "type",
            width=90
        )

        tree.column(
            "deleted",
            width=180
        )

        tree.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )

        scrollbar.grid(
            row=1,
            column=1,
            sticky="ns"
        )

        tree.configure(
            yscrollcommand=scrollbar.set
        )

        def refresh_trash():
            for item in tree.get_children():
                tree.delete(item)

            with connect() as conn:
                rows = conn.execute(
                    """
                    SELECT
                        id,
                        english,
                        chinese,
                        item_type,
                        deleted_at
                    FROM vocabulary
                    WHERE deleted_at IS NOT NULL
                    ORDER BY deleted_at DESC
                    """
                ).fetchall()

            for row in rows:
                tree.insert(
                    "",
                    "end",
                    iid=str(row["id"]),
                    values=(
                        row["english"],
                        row["chinese"] or "",
                        row["item_type"],
                        row["deleted_at"] or ""
                    )
                )

        def restore_selected():
            selection = tree.selection()

            if not selection:
                messagebox.showwarning(
                    "请选择记录",
                    "请先选择要恢复的词条。",
                    parent=window
                )
                return

            record_id = int(selection[0])

            with connect() as conn:
                row = conn.execute(
                    """
                    SELECT *
                    FROM vocabulary
                    WHERE id = ?
                    """,
                    (record_id,)
                ).fetchone()

                if row is None:
                    refresh_trash()
                    return

                duplicate = conn.execute(
                    """
                    SELECT id
                    FROM vocabulary
                    WHERE deleted_at IS NULL
                      AND id != ?
                      AND item_type = ?
                      AND LOWER(TRIM(english))
                          = LOWER(TRIM(?))
                    LIMIT 1
                    """,
                    (
                        record_id,
                        row["item_type"],
                        row["english"]
                    )
                ).fetchone()

                if duplicate:
                    messagebox.showwarning(
                        "无法恢复",
                        (
                            "当前词库中已经存在同名、"
                            "同类型的词条。\n\n"
                            "请先处理现有记录。"
                        ),
                        parent=window
                    )
                    return

                now = datetime.now().isoformat(
                    timespec="seconds"
                )

                conn.execute(
                    """
                    UPDATE vocabulary
                    SET
                        deleted_at = NULL,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        now,
                        record_id
                    )
                )

            refresh_trash()
            self.refresh_all()

            messagebox.showinfo(
                "恢复成功",
                f"{row['english']} 已恢复。",
                parent=window
            )

        controls = ttk.Frame(frame)

        controls.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(12, 0)
        )

        ttk.Button(
            controls,
            text="恢复选中词条",
            command=restore_selected
        ).pack(
            side="left"
        )

        ttk.Button(
            controls,
            text="关闭",
            command=window.destroy
        ).pack(
            side="right"
        )

        refresh_trash()


    def clear_form(
        self,
        keep_source=False,
        keep_chapter=False
    ):
        self.editing_id = None

        if hasattr(
            self,
            "save_button"
        ):
            self.save_button.configure(
                text="保存"
            )

        if hasattr(
            self,
            "cancel_edit_button"
        ):
            self.cancel_edit_button.configure(
                state="disabled"
            )

        if hasattr(
            self,
            "delete_button"
        ):
            self.delete_button.configure(
                state="disabled"
            )

        source = (
            self.source_var.get()
            if keep_source
            else ""
        )

        chapter = (
            self.chapter_var.get()
            if keep_chapter
            else ""
        )

        self.english_var.set("")
        self.chinese_var.set("")
        self.page_var.set("")

        self.context_text.delete(
            "1.0",
            "end"
        )

        self.source_var.set(source)
        self.chapter_var.set(chapter)

        self.english_entry.focus_set()

    def clear_search(self):
        self.search_var.set("")
        self.refresh_history()
        self.search_entry.focus_set()


    def refresh_all(self):
        self.refresh_history()
        self.refresh_stats()

    def refresh_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        keyword = ""

        if hasattr(
            self,
            "search_var"
        ):
            keyword = (
                self.search_var
                .get()
                .strip()
            )

        with connect() as conn:

            if keyword:
                pattern = f"%{keyword}%"

                rows = conn.execute(
                    """
                    SELECT
                        id,
                        english,
                        chinese,
                        item_type,
                        times_asked,
                        source,
                        chapter

                    FROM vocabulary

                    WHERE deleted_at IS NULL
                      AND (
                        COALESCE(
                            english,
                            ''
                        ) LIKE ? COLLATE NOCASE

                        OR COALESCE(
                            chinese,
                            ''
                        ) LIKE ? COLLATE NOCASE

                        OR COALESCE(
                            source,
                            ''
                        ) LIKE ? COLLATE NOCASE

                        OR COALESCE(
                            chapter,
                            ''
                        ) LIKE ? COLLATE NOCASE
                      )

                    ORDER BY id DESC
                    LIMIT 100
                    """,
                    (
                        pattern,
                        pattern,
                        pattern,
                        pattern
                    )
                ).fetchall()

            else:
                rows = conn.execute(
                    """
                    SELECT
                        id,
                        english,
                        chinese,
                        item_type,
                        times_asked,
                        source,
                        chapter

                    FROM vocabulary
                    WHERE deleted_at IS NULL

                    ORDER BY id DESC
                    LIMIT 100
                    """
                ).fetchall()

        for row in rows:
            self.tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["english"],
                    row["chinese"] or "",
                    row["item_type"],
                    row["times_asked"] or 1,
                    row["source"] or "",
                    row["chapter"] or ""
                )
            )


    def refresh_stats(self):
        with connect() as conn:
            total = conn.execute(
                """
                SELECT COUNT(*)
                FROM vocabulary
                WHERE deleted_at IS NULL
                """
            ).fetchone()[0]

            repeated = conn.execute(
                """
                SELECT COUNT(*)
                FROM vocabulary
                WHERE deleted_at IS NULL
                  AND COALESCE(
                    times_asked,
                    1
                ) >= 2
                """
            ).fetchone()[0]

        system = platform.system()

        self.status_var.set(
            (
                f"词库共 {total} 条"
                f"  ·  重复遇到 {repeated} 条"
                f"  ·  {system}"
                f"  ·  {DB_PATH}"
            )
        )

    def export_csv(self):
        filename = (
            "Vocabulary_"
            + datetime.now().strftime(
                "%Y-%m-%d"
            )
            + ".csv"
        )

        path = filedialog.asksaveasfilename(
            title="导出 Vocabulary",
            initialfile=filename,
            defaultextension=".csv",
            filetypes=[
                (
                    "CSV 文件",
                    "*.csv"
                )
            ]
        )

        if not path:
            return

        with connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM vocabulary
                ORDER BY id
                """
            ).fetchall()

        if not rows:
            messagebox.showinfo(
                "没有数据",
                "词库目前还是空的。"
            )
            return

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file)

            writer.writerow(
                rows[0].keys()
            )

            for row in rows:
                writer.writerow(
                    list(row)
                )

        messagebox.showinfo(
            "导出完成",
            path
        )


if __name__ == "__main__":
    init_db()

    try:
        create_backup(
            force=False
        )
    except Exception as exc:
        print(
            f"Automatic backup failed: {exc}"
        )

    app = VocabularyApp()
    app.mainloop()
