"""font2schematic — CustomTkinter GUI""" 

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

import customtkinter as ctk

from constants import (
    DEFAULT_BACKGROUND,
    DEFAULT_FONT_SIZE,
    DEFAULT_FOREGROUND,
    DEFAULT_PROJECT_NAME,
    DEFAULT_SCALE,
    FONT_EXTENSIONS,
    LITEMATIC_EXTENSIONS,
    MODE_XZ,
    VIEW_MODES,
    get_all_color_names,
)
from renderer import estimate_size, generate_litematic

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class Font2SchematicApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("font2schematic — 文字转 Minecraft 投影")
        self.geometry("640x720")
        self.minsize(560, 680)

        self.font_path: str = ""
        self._after_id: str | None = None

        self._build_ui()
        self._bind_events()

 

    def _build_ui(self):

        scroll_frame = ctk.CTkFrame(self)
        scroll_frame.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(scroll_frame, text="字体文件", font=("", 14, "bold")).pack(
            anchor="w", pady=(0, 4)
        )
        font_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        font_row.pack(fill="x", pady=(0, 12))

        self.font_btn = ctk.CTkButton(
            font_row, text="选择字体...", width=110, command=self._pick_font
        )
        self.font_btn.pack(side="left", padx=(0, 8))

        self.font_label = ctk.CTkLabel(
            font_row,
            text="未选择",
            anchor="w",
            fg_color=("gray85", "gray20"),
            corner_radius=6,
            padx=8,
        )
        self.font_label.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(scroll_frame, text="文本内容", font=("", 14, "bold")).pack(
            anchor="w", pady=(0, 4)
        )
        self.text_box = ctk.CTkTextbox(scroll_frame, height=120, wrap="word")
        self.text_box.pack(fill="x", pady=(0, 12))
        self.text_box.insert("0.0", "")

        params_frame = ctk.CTkFrame(scroll_frame)
        params_frame.pack(fill="x", pady=(0, 12))

        row1 = ctk.CTkFrame(params_frame, fg_color="transparent")
        row1.pack(fill="x", pady=6, padx=8)

        ctk.CTkLabel(row1, text="字号 (pt):").pack(side="left")
        self.font_size_var = ctk.StringVar(value=str(DEFAULT_FONT_SIZE))
        self.font_size_entry = ctk.CTkEntry(
            row1, width=70, textvariable=self.font_size_var
        )
        self.font_size_entry.pack(side="left", padx=(4, 24))

        ctk.CTkLabel(row1, text="缩放倍数:").pack(side="left")
        self.scale_var = ctk.StringVar(value=str(DEFAULT_SCALE))
        self.scale_entry = ctk.CTkEntry(row1, width=60, textvariable=self.scale_var)
        self.scale_entry.pack(side="left", padx=(4, 0))

        row2 = ctk.CTkFrame(params_frame, fg_color="transparent")
        row2.pack(fill="x", pady=6, padx=8)

        ctk.CTkLabel(row2, text="渲染平面:").pack(side="left")
        self.mode_var = ctk.StringVar(value=MODE_XZ)
        self.mode_menu = ctk.CTkOptionMenu(
            row2,
            values=VIEW_MODES,
            variable=self.mode_var,
            width=120,
        )
        self.mode_menu.pack(side="left", padx=(4, 24))

        ctk.CTkLabel(row2, text="投影名称:").pack(side="left")
        self.proj_name_var = ctk.StringVar(value=DEFAULT_PROJECT_NAME)
        self.proj_name_entry = ctk.CTkEntry(
            row2, width=160, textvariable=self.proj_name_var
        )
        self.proj_name_entry.pack(side="left", padx=(4, 0))

        row3 = ctk.CTkFrame(params_frame, fg_color="transparent")
        row3.pack(fill="x", pady=6, padx=8)

        all_colors = get_all_color_names()

        ctk.CTkLabel(row3, text="字体颜色:").pack(side="left")
        self.fg_color_var = ctk.StringVar(value=DEFAULT_FOREGROUND)
        self.fg_color_menu = ctk.CTkOptionMenu(
            row3, values=all_colors, variable=self.fg_color_var, width=120
        )
        self.fg_color_menu.pack(side="left", padx=(4, 24))

        ctk.CTkLabel(row3, text="背景颜色:").pack(side="left")
        self.bg_color_var = ctk.StringVar(value=DEFAULT_BACKGROUND)
        self.bg_color_menu = ctk.CTkOptionMenu(
            row3, values=all_colors, variable=self.bg_color_var, width=120
        )
        self.bg_color_menu.pack(side="left", padx=(4, 0))

        row4 = ctk.CTkFrame(params_frame, fg_color="transparent")
        row4.pack(fill="x", pady=(0, 0), padx=8)

        self.size_label = ctk.CTkLabel(
            row4,
            text="预计尺寸: 请先选择字体并输入文本",
            anchor="w",
            font=("", 13),
        )
        self.size_label.pack(side="left", fill="x", expand=True)

        self.generate_btn = ctk.CTkButton(
            scroll_frame,
            text="生成投影",
            height=40,
            font=("", 15, "bold"),
            command=self._generate,
        )
        self.generate_btn.pack(fill="x", pady=(0, 8))

    def _bind_events(self):
        self.font_size_var.trace_add("write", lambda *_: self._schedule_preview)
        self.scale_var.trace_add("write", lambda *_: self._schedule_preview)
        self.mode_var.trace_add("write", lambda *_: self._schedule_preview)
        self.fg_color_var.trace_add("write", lambda *_: self._schedule_preview)
        self.bg_color_var.trace_add("write", lambda *_: self._schedule_preview)
        self.font_size_entry.bind("<KeyRelease>", lambda *_: self._schedule_preview())
        self.scale_entry.bind("<KeyRelease>", lambda *_: self._schedule_preview())
        self.proj_name_entry.bind("<KeyRelease>", lambda *_: self._schedule_preview())
        self.text_box.bind("<KeyRelease>", lambda *_: self._schedule_preview())

    def _schedule_preview(self):
        """延迟"""
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(300, self._update_preview)

    def _pick_font(self):
        path = filedialog.askopenfilename(
            title="选择字体文件",
            filetypes=FONT_EXTENSIONS,
        )
        if path:
            self.font_path = path
            name = Path(path).name
            self.font_label.configure(text=name)
            self._update_preview()

    def _validate_int(self, val: str, default: int) -> int:
        try:
            return max(1, int(val))
        except (ValueError, TypeError):
            return default

    def _update_preview(self):
        """更新预计尺寸显示。"""
        text = self.text_box.get("0.0", "end").strip()
        if not text or not self.font_path:
            self.size_label.configure(text="预计尺寸: 请先选择字体并输入文本")
            return

        font_size = self._validate_int(self.font_size_var.get(), DEFAULT_FONT_SIZE)
        scale = self._validate_int(self.scale_var.get(), DEFAULT_SCALE)

        w, h, d = estimate_size(text, self.font_path, font_size, scale, self.mode_var.get())

        if w > 0:
            self.size_label.configure(text=f"预计投影尺寸: {w} × {h} × {d}  方块")
        else:
            self.size_label.configure(text="预计尺寸: 计算失败，请检查输入")

    def _generate(self):
        """生成 .litematic 文件。"""
        text = self.text_box.get("0.0", "end").strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本内容")
            return
        if not self.font_path:
            messagebox.showwarning("提示", "请选择字体文件")
            return
        if not Path(self.font_path).exists():
            messagebox.showwarning("提示", "字体文件不存在，请重新选择")
            return

        font_size = self._validate_int(self.font_size_var.get(), DEFAULT_FONT_SIZE)
        scale = self._validate_int(self.scale_var.get(), DEFAULT_SCALE)
        mode = self.mode_var.get()
        fg = self.fg_color_var.get()
        bg = self.bg_color_var.get()
        proj_name = self.proj_name_var.get().strip() or DEFAULT_PROJECT_NAME

        default_name = f"{proj_name}.litematic"

        save_path = filedialog.asksaveasfilename(
            title="保存投影文件",
            defaultextension=".litematic",
            filetypes=LITEMATIC_EXTENSIONS,
            initialfile=default_name,
        )
        if not save_path:
            return

        try:
            self.generate_btn.configure(text="生成中...", state="disabled")
            self.update()

            generate_litematic(
                text=text,
                font_path=self.font_path,
                font_size=font_size,
                scale=scale,
                mode=mode,
                foreground=fg,
                background=bg,
                project_name=proj_name,
                save_path=save_path,
            )

            messagebox.showinfo("完成", f"投影文件已保存:\n{save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败:\n{e}")
        finally:
            self.generate_btn.configure(text="生成投影", state="normal")


def run():
    app = Font2SchematicApp()
    app.mainloop()


if __name__ == "__main__":
    run()
