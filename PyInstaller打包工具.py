import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import threading

# 尝试导入tkinterdnd2库用于支持拖放功能
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND_SUPPORT = True
except ImportError:
    HAS_DND_SUPPORT = False

class PyInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyInstaller 打包工具")
        self.root.geometry("715x580")
        
        # 配置文件路径
        self.config_file = "打包配置.json"
        
        # 资源文件列表
        self.resource_files = []
        
        # 隐藏导入库列表
        self.hidden_imports = []
        
        # 线程控制变量
        self.is_installing = False
        self.is_packing = False
        self.is_busy = False  # 全局忙碌状态
        self.current_thread = None

        # 自签名证书信息配置
        self.self_sign_cn = tk.StringVar(value="SelfSignedCert")  # 通用名称
        self.self_sign_o = tk.StringVar(value="MyCompany")  # 组织名称
        self.self_sign_ou = tk.StringVar(value="Development")  # 组织单位
        self.self_sign_l = tk.StringVar(value="Beijing")  # 城市
        self.self_sign_s = tk.StringVar(value="Beijing")  # 省/州
        self.self_sign_c = tk.StringVar(value="CN")  # 国家代码
        self.self_sign_friendly = tk.StringVar(value="SelfSigned Code Signing Certificate")  # 友好名称
        self.self_sign_validity = tk.IntVar(value=10)  # 有效期（年）

        # 创建界面
        self.create_widgets()
        
        # 读取保存的配置（只在文件已存在时加载，否则不创建文件）
        self.load_config()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="8")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="PyInstaller 打包工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 创建笔记本（选项卡）
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 基本设置选项卡
        basic_frame = ttk.Frame(notebook, padding="5")
        notebook.add(basic_frame, text="基本设置")

        # 资源文件选项卡
        resource_frame = ttk.Frame(notebook, padding="5")
        notebook.add(resource_frame, text="资源文件")

        # 库设置选项卡
        library_frame = ttk.Frame(notebook, padding="5")
        notebook.add(library_frame, text="库设置")

        # 数字签名选项卡
        sign_frame = ttk.Frame(notebook, padding="5")
        notebook.add(sign_frame, text="数字签名")

        # 日志选项卡
        log_frame = ttk.Frame(notebook, padding="5")
        notebook.add(log_frame, text="打包日志")

        # 基本设置框架内容
        self.create_basic_settings(basic_frame)

        # 资源文件框架内容
        self.create_resource_settings(resource_frame)

        # 库设置框架内容
        self.create_library_settings(library_frame)

        # 数字签名框架内容
        self.create_sign_settings(sign_frame)

        # 日志框架内容
        self.create_log_settings(log_frame)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=5)

        ttk.Button(button_frame, text="开始打包", command=self.start_pack, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="安装PyInstaller", command=self.install_pyinstaller).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="安装pywin32", command=self.install_pywin32).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空配置", command=self.clear_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.safe_quit).pack(side=tk.LEFT, padx=5)

        # 进度条框架
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var, font=("Arial", 9))
        status_label.pack(side=tk.LEFT, padx=(0, 10))

        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)  # notebook占据主要空间
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 资源文件框架的网格配置
        resource_frame.columnconfigure(1, weight=1)
        resource_frame.rowconfigure(1, weight=1)
        
        # 库设置框架的网格配置
        library_frame.columnconfigure(1, weight=1)
        library_frame.rowconfigure(1, weight=1)
    
    def create_basic_settings(self, parent):
        """创建基本设置界面"""
        # 当前路径显示
        ttk.Label(parent, text="当前工作路径:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(parent, textvariable=self.path_var, width=60)
        path_entry.grid(row=0, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))

        # 浏览按钮
        ttk.Button(parent, text="浏览", command=self.browse_path).grid(row=0, column=2, pady=3, padx=(5, 0))

        # 选择Python文件
        ttk.Label(parent, text="选择要打包的Python文件（支持拖放）:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(parent, textvariable=self.file_var, width=60)
        file_entry.grid(row=1, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # 为文件选择框启用拖放功能
        if HAS_DND_SUPPORT:
            file_entry.drop_target_register(DND_FILES)
            file_entry.dnd_bind('<<Drop>>', self.on_python_file_drop)

        ttk.Button(parent, text="选择文件", command=self.browse_file).grid(row=1, column=2, pady=3, padx=(5, 0))

        # 选项框架
        options_frame = ttk.LabelFrame(parent, text="打包选项", padding="8")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.onefile_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="打包为单个exe文件", variable=self.onefile_var).grid(row=0, column=0, sticky=tk.W)

        self.console_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="显示控制台窗口", variable=self.console_var).grid(row=0, column=1, sticky=tk.W)

        self.icon_var = tk.StringVar()
        ttk.Label(options_frame, text="图标文件(可选，支持拖放):").grid(row=1, column=0, sticky=tk.W, pady=3)
        icon_entry = ttk.Entry(options_frame, textvariable=self.icon_var, width=40)
        icon_entry.grid(row=1, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # 为图标文件输入框启用拖放功能
        if HAS_DND_SUPPORT:
            icon_entry.drop_target_register(DND_FILES)
            icon_entry.dnd_bind('<<Drop>>', self.on_icon_drop)
        
        # 使用frame包含两个按钮，让它们紧挨着
        icon_button_frame = ttk.Frame(options_frame)
        icon_button_frame.grid(row=1, column=2, pady=3, padx=(5, 0))
        ttk.Button(icon_button_frame, text="选择图标", command=self.browse_icon).pack(side=tk.LEFT, padx=0)
        ttk.Button(icon_button_frame, text="转换为ICO", command=self.open_icon_converter).pack(side=tk.LEFT, padx=(5, 0))

        # 桌面快捷方式图标
        self.desktop_icon_var = tk.StringVar()
        ttk.Label(options_frame, text="桌面快捷方式图标(可选，支持拖放):").grid(row=2, column=0, sticky=tk.W, pady=3)
        desktop_icon_entry = ttk.Entry(options_frame, textvariable=self.desktop_icon_var, width=40)
        desktop_icon_entry.grid(row=2, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # 为桌面快捷方式图标输入框启用拖放功能
        if HAS_DND_SUPPORT:
            desktop_icon_entry.drop_target_register(DND_FILES)
            desktop_icon_entry.dnd_bind('<<Drop>>', self.on_desktop_icon_drop)
        
        ttk.Button(options_frame, text="选择图标", command=self.browse_desktop_icon).grid(row=2, column=2, pady=3, padx=(5, 0))

        # 创建桌面快捷方式
        self.create_shortcut_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="打包后创建桌面快捷方式", variable=self.create_shortcut_var).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=3)

        # UAC管理员权限
        self.uac_admin_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="需要管理员权限运行(UAC)", variable=self.uac_admin_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=3)

        # 版本号
        self.version_var = tk.StringVar()
        ttk.Label(options_frame, text="版本号(可选):").grid(row=5, column=0, sticky=tk.W, pady=3)
        version_entry = ttk.Entry(options_frame, textvariable=self.version_var, width=40)
        version_entry.grid(row=5, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        ttk.Label(options_frame, text="格式: 1.0.0.0").grid(row=5, column=2, pady=3, padx=(5, 0), sticky=tk.W)

        # 文件说明
        self.file_description_var = tk.StringVar()
        ttk.Label(options_frame, text="文件说明(可选):").grid(row=6, column=0, sticky=tk.W, pady=3)
        file_description_entry = ttk.Entry(options_frame, textvariable=self.file_description_var, width=40)
        file_description_entry.grid(row=6, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        ttk.Label(options_frame, text="exe属性中显示").grid(row=6, column=2, pady=3, padx=(5, 0), sticky=tk.W)

        # 版权信息
        self.copyright_var = tk.StringVar()
        ttk.Label(options_frame, text="版权信息(可选):").grid(row=7, column=0, sticky=tk.W, pady=3)
        copyright_entry = ttk.Entry(options_frame, textvariable=self.copyright_var, width=40)
        copyright_entry.grid(row=7, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        ttk.Label(options_frame, text="例如: Copyright © 2025").grid(row=7, column=2, pady=3, padx=(5, 0), sticky=tk.W)

        # 语言
        self.language_var = tk.StringVar(value="中文（简体）")
        ttk.Label(options_frame, text="语言(可选):").grid(row=9, column=0, sticky=tk.W, pady=3)
        language_combo = ttk.Combobox(options_frame, textvariable=self.language_var, width=37, state="readonly")
        language_combo['values'] = (
            "中文（简体）",
            "中文（繁体）",
            "英语（美国）",
            "英语（英国）",
            "日语",
            "韩语",
            "法语",
            "德语",
            "西班牙语",
            "俄语"
        )
        language_combo.grid(row=9, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        ttk.Label(options_frame, text="exe属性中显示").grid(row=9, column=2, pady=3, padx=(5, 0), sticky=tk.W)

        # 配置网格权重
        parent.columnconfigure(1, weight=1)
    
    def create_resource_settings(self, parent):
        """创建资源文件设置界面"""
        # 添加资源文件框架
        add_frame = ttk.Frame(parent)
        add_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=3)

        ttk.Label(add_frame, text="添加资源文件/文件夹:").grid(row=0, column=0, sticky=tk.W)

        # 源路径
        ttk.Label(add_frame, text="源路径(支持拖放):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(add_frame, textvariable=self.source_var, width=40)
        source_entry.grid(row=1, column=1, pady=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # 为源路径输入框启用拖放功能
        if HAS_DND_SUPPORT:
            source_entry.drop_target_register(DND_FILES)
            source_entry.dnd_bind('<<Drop>>', self.on_source_drop)
        
        ttk.Button(add_frame, text="浏览", command=self.browse_source).grid(row=1, column=2, pady=2, padx=(5, 0))

        # 目标路径（在打包文件中的路径）
        ttk.Label(add_frame, text="目标路径:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(add_frame, textvariable=self.target_var, width=40)
        target_entry.grid(row=2, column=1, pady=2, padx=(5, 0), sticky=(tk.W, tk.E))
        ttk.Button(add_frame, text="自动生成", command=self.auto_generate_target).grid(row=2, column=2, pady=2, padx=(5, 0))

        # 添加按钮
        button_row_frame = ttk.Frame(add_frame)
        button_row_frame.grid(row=3, column=0, columnspan=3, pady=3)
        ttk.Button(button_row_frame, text="添加资源", command=self.add_resource).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_row_frame, text="批量添加", command=self.browse_source_multiple).pack(side=tk.LEFT, padx=5)

        # 资源文件列表
        list_frame = ttk.LabelFrame(parent, text="已添加的资源文件（支持拖放）", padding="5")
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 列表和滚动条
        self.resource_listbox = tk.Listbox(list_frame, height=6)
        self.resource_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 启用拖放功能
        if HAS_DND_SUPPORT:
            self.resource_listbox.drop_target_register(DND_FILES)
            self.resource_listbox.dnd_bind('<<Drop>>', self.on_resource_drop)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.resource_listbox.yview)
        list_scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.resource_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # 列表操作按钮
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=0, column=3, sticky=(tk.N, tk.S), padx=(5, 0))
        
        ttk.Button(button_frame, text="删除选中", command=self.delete_resource).pack(pady=2)
        ttk.Button(button_frame, text="清空列表", command=self.clear_resources).pack(pady=2)
        ttk.Button(button_frame, text="上移", command=self.move_up).pack(pady=2)
        ttk.Button(button_frame, text="下移", command=self.move_down).pack(pady=2)
        
        # 配置网格权重
        add_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
    
    def create_library_settings(self, parent):
        """创建库设置界面"""
        # 说明文本
        description = "有些库在打包时可能无法自动检测到，需要手动指定。\n" \
                     "例如：pandas、numpy、PyQt5等库有时需要明确指定。"
        ttk.Label(parent, text=description, foreground="blue").grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(5, 8))

        # 创建一个大框架包含常见库和添加库
        main_frame = ttk.LabelFrame(parent, text="库管理", padding="5")
        main_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))

        # 常见库快速添加（左侧）
        ttk.Label(main_frame, text="常见库快速添加:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        common_frame = ttk.Frame(main_frame)
        common_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        common_libraries = [
            "pandas", "numpy", "matplotlib", "requests",
            "scipy", "sklearn", "PyQt5", "pillow",
            "PySide2", "tkinter", "openpyxl", "xlwt"
        ]

        # 创建四列按钮布局
        for i, lib in enumerate(common_libraries):
            col = i % 4
            row = i // 4
            ttk.Button(
                common_frame,
                text=lib,
                width=10,
                command=lambda l=lib: self.add_common_library(l)
            ).grid(row=row, column=col, padx=4, pady=3, sticky=tk.W)

        # 添加库框架（右侧）
        add_frame = ttk.Frame(main_frame)
        add_frame.grid(row=1, column=1, sticky=(tk.N, tk.E, tk.W))

        ttk.Label(add_frame, text="添加需要打包的库:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        # 库名称标签
        ttk.Label(add_frame, text="库名称:").grid(row=1, column=0, sticky=tk.W)

        # 输入框
        self.library_var = tk.StringVar()
        library_entry = ttk.Entry(add_frame, textvariable=self.library_var, width=20)
        library_entry.grid(row=1, column=1, padx=5, sticky=tk.W)

        # 添加按钮
        ttk.Button(add_frame, text="添加库", command=self.add_library).grid(row=2, column=0, columnspan=2, pady=(5, 0), sticky=tk.W)

        # 配置列权重，让常见库区域占据更多空间
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)

        # 库列表
        list_frame = ttk.LabelFrame(parent, text="已添加的库（支持拖放.py文件自动提取库名）", padding="5")
        list_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))

        # 列表和滚动条
        self.library_listbox = tk.Listbox(list_frame, height=6)
        self.library_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 启用拖放功能
        if HAS_DND_SUPPORT:
            self.library_listbox.drop_target_register(DND_FILES)
            self.library_listbox.dnd_bind('<<Drop>>', self.on_library_drop)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.library_listbox.yview)
        list_scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.library_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # 列表操作按钮
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=0, column=3, sticky=(tk.N, tk.S), padx=(5, 0))
        
        ttk.Button(button_frame, text="删除选中", command=self.delete_library).pack(pady=2)
        ttk.Button(button_frame, text="清空列表", command=self.clear_libraries).pack(pady=2)
        
        # 配置网格权重
        add_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

    def create_sign_settings(self, parent):
        """创建数字签名设置界面"""
        # 说明文本
        description = "数字签名可以为您的EXE文件添加数字证书，提高软件的可信度。\n" \
                     "需要准备代码签名证书（.pfx或.p12格式）和Windows SDK。"
        ttk.Label(parent, text=description, foreground="blue").grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(5, 8))

        # 启用数字签名勾选框
        self.enable_sign_var = tk.BooleanVar(value=False)
        self.enable_sign_checkbox = ttk.Checkbutton(parent, text="启用数字签名(打包后自动签名)", variable=self.enable_sign_var, command=lambda: self.on_enable_sign_changed())
        self.enable_sign_checkbox.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=3)

        # 证书类型选择（移到上面）
        self.use_self_signed_var = tk.BooleanVar(value=True)
        cert_type_label = ttk.Label(parent, text="证书类型:")
        cert_type_label.grid(row=2, column=0, sticky=tk.W, pady=3)
        cert_type_frame = ttk.Frame(parent)
        cert_type_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=3, padx=(5, 0))
        self.cert_type_radio1 = ttk.Radiobutton(cert_type_frame, text="使用自签名证书(自动生成)", variable=self.use_self_signed_var, value=True, command=lambda: self.on_cert_type_changed())
        self.cert_type_radio1.pack(side=tk.LEFT)
        self.cert_type_radio2 = ttk.Radiobutton(cert_type_frame, text="使用自定义证书", variable=self.use_self_signed_var, value=False, command=lambda: self.on_cert_type_changed())
        self.cert_type_radio2.pack(side=tk.LEFT, padx=(15, 0))

        # 初始化时禁用证书类型选择
        self.cert_type_radio1.configure(state="disabled")
        self.cert_type_radio2.configure(state="disabled")

        # 签名工具设置框架（仅在使用自签名证书时显示）
        self.signtool_frame = ttk.LabelFrame(parent, text="签名工具设置", padding="8")
        self.signtool_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # signtool路径
        self.signtool_path_var = tk.StringVar()
        self.signtool_path_label = ttk.Label(self.signtool_frame, text="signtool路径(支持拖放):")
        self.signtool_path_label.grid(row=0, column=0, sticky=tk.W, pady=3)
        self.signtool_path_entry = ttk.Entry(self.signtool_frame, textvariable=self.signtool_path_var, width=35)
        self.signtool_path_entry.grid(row=0, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # 为signtool路径输入框启用拖放功能
        if HAS_DND_SUPPORT:
            self.signtool_path_entry.drop_target_register(DND_FILES)
            self.signtool_path_entry.dnd_bind('<<Drop>>', self.on_signtool_drop)
        
        signtool_button_frame = ttk.Frame(self.signtool_frame)
        signtool_button_frame.grid(row=0, column=2, pady=3, padx=(5, 0))
        self.browse_signtool_button = ttk.Button(signtool_button_frame, text="浏览", command=self.browse_signtool)
        self.browse_signtool_button.pack(side=tk.LEFT, padx=1)
        self.download_sdk_button = ttk.Button(signtool_button_frame, text="下载SDK", command=self.download_windows_sdk)
        self.download_sdk_button.pack(side=tk.LEFT, padx=1)

        # signtool状态显示
        self.signtool_status_var = tk.StringVar(value="未检测")
        self.signtool_status_label = ttk.Label(self.signtool_frame, textvariable=self.signtool_status_var, foreground="gray")
        self.signtool_status_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        # 可能的路径提示
        possible_paths = "可能的路径:\n下载SDK时指定的路径\\bin\\x64\\signtool.exe"
        self.signtool_hint_label = ttk.Label(self.signtool_frame, text=possible_paths, foreground="gray", font=("Arial", 8))
        self.signtool_hint_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        # 初始化时隐藏
        self.signtool_hint_label.grid_remove()

        # 设置自签名证书信息按钮
        self.config_self_sign_button = ttk.Button(self.signtool_frame, text="设置自签名证书信息", command=self.open_self_sign_config, width=20)
        self.config_self_sign_button.grid(row=3, column=0, columnspan=3, pady=5, sticky=tk.W)
        # 初始化时禁用
        self.config_self_sign_button.configure(state="disabled")

        # 配置signtool_frame的网格权重
        self.signtool_frame.columnconfigure(1, weight=1)
        
        # 初始化时禁用signtool_frame中的所有控件
        self.enable_signtool_frame(False)

        # 数字签名设置框架
        self.sign_container_frame = ttk.LabelFrame(parent, text="数字签名设置", padding="8")
        self.sign_container_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.options_frame = self.sign_container_frame  # 保持兼容性

        # 证书文件（仅在使用自定义证书时显示）
        self.cert_file_var = tk.StringVar()
        self.cert_file_label = ttk.Label(self.sign_container_frame, text="证书文件(.pfx/.p12)(支持拖放):")
        self.cert_file_label.grid(row=0, column=0, sticky=tk.W, pady=3)
        self.cert_file_entry = ttk.Entry(self.sign_container_frame, textvariable=self.cert_file_var, width=50)
        self.cert_file_entry.grid(row=0, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # 为证书文件输入框启用拖放功能
        if HAS_DND_SUPPORT:
            self.cert_file_entry.drop_target_register(DND_FILES)
            self.cert_file_entry.dnd_bind('<<Drop>>', self.on_cert_file_drop)
        
        self.cert_file_button = ttk.Button(self.sign_container_frame, text="选择证书", command=self.browse_cert_file)
        self.cert_file_button.grid(row=0, column=2, pady=3, padx=(5, 0))

        # 证书密码
        self.cert_password_var = tk.StringVar()
        self.cert_password_label = ttk.Label(self.sign_container_frame, text="证书密码:")
        self.cert_password_label.grid(row=1, column=0, sticky=tk.W, pady=3)
        self.cert_password_entry = ttk.Entry(self.sign_container_frame, textvariable=self.cert_password_var, width=50, show="*")
        self.cert_password_entry.grid(row=1, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))

        # 时间戳服务器
        self.timestamp_server_var = tk.StringVar(value="http://timestamp.digicert.com")
        self.timestamp_server_label = ttk.Label(self.sign_container_frame, text="时间戳服务器:")
        self.timestamp_server_label.grid(row=2, column=0, sticky=tk.W, pady=3)
        self.timestamp_entry = ttk.Entry(self.sign_container_frame, textvariable=self.timestamp_server_var, width=50)
        self.timestamp_entry.grid(row=2, column=1, pady=3, padx=(5, 0), sticky=(tk.W, tk.E))
        self.timestamp_default_label = ttk.Label(self.sign_container_frame, text="默认: DigiCert")
        self.timestamp_default_label.grid(row=2, column=2, pady=3, padx=(5, 0), sticky=tk.W)

        # 常用时间戳服务器
        self.common_timestamp_label = ttk.Label(self.sign_container_frame, text="常用时间戳服务器:")
        self.common_timestamp_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 3))
        self.timestamp_combo = ttk.Combobox(self.sign_container_frame, width=50, state="readonly")
        self.timestamp_combo['values'] = (
            "http://timestamp.digicert.com",
            "http://timestamp.sectigo.com",
            "http://timestamp.globalsign.com",
            "http://tsa.starfieldtech.com",
            "http://timestamp.apple.com/ts01"
        )
        self.timestamp_combo.set("http://timestamp.digicert.com")
        self.timestamp_combo.grid(row=3, column=1, pady=(10, 3), padx=(5, 0), sticky=(tk.W, tk.E))
        self.timestamp_combo.bind('<<ComboboxSelected>>', lambda e: self.timestamp_server_var.set(self.timestamp_combo.get()))

        # 配置网格权重
        parent.columnconfigure(1, weight=1)
        self.sign_container_frame.columnconfigure(1, weight=1)

        # 一键签名按钮框架（在sign_container_frame内）
        button_frame = ttk.Frame(self.sign_container_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(15, 5))

        self.sign_single_button = ttk.Button(button_frame, text="一键签名EXE文件", command=self.sign_single_exe, width=25)
        self.sign_single_button.pack(pady=5)
        
        # 为一键签名按钮启用拖放功能
        if HAS_DND_SUPPORT:
            self.sign_single_button.drop_target_register(DND_FILES)
            self.sign_single_button.dnd_bind('<<Drop>>', self.on_exe_drop_to_sign)

        # 说明
        note_label = ttk.Label(button_frame, text="直接选择EXE文件进行签名（无需打包，支持拖拽）", foreground="gray", font=("Arial", 8))
        note_label.pack(pady=(0, 5))

        # 初始化时禁用sign_container_frame
        self.enable_options_frame(False)
        
        # 初始化时显示signtool_frame但禁用（默认未勾选启用数字签名）
        self.signtool_frame.grid()
        self.enable_signtool_frame(False)

        # 初始化时隐藏证书文件字段（默认使用自签名证书）
        self.on_cert_type_changed()

        # 初始化时检查signtool路径
        self.check_signtool_path()

    def on_enable_sign_changed(self):
        """启用数字签名复选框状态变化时的回调函数"""
        enabled = self.enable_sign_var.get()

        if enabled:
            # 启用时，启用证书类型选择
            self.cert_type_radio1.configure(state="normal")
            self.cert_type_radio2.configure(state="normal")

            # 根据证书类型决定显示和启用什么
            if self.use_self_signed_var.get():
                # 使用自签名证书，显示signtool_frame并启用
                self.signtool_frame.grid()
                self.enable_signtool_frame(True)
                # 启用"设置自签名证书信息"按钮
                self.config_self_sign_button.configure(state="normal")
                # 检查signtool路径
                signtool_found = self.check_signtool_path()
                if signtool_found:
                    self.enable_options_frame(True)
                else:
                    self.enable_options_frame(False)
            else:
                # 使用自定义证书，隐藏signtool_frame，启用数字签名设置
                self.signtool_frame.grid_remove()
                # 禁用"设置自签名证书信息"按钮
                self.config_self_sign_button.configure(state="disabled")
                self.enable_options_frame(True)
        else:
            # 禁用时，禁用证书类型选择
            self.cert_type_radio1.configure(state="disabled")
            self.cert_type_radio2.configure(state="disabled")
            # 禁用"设置自签名证书信息"按钮
            self.config_self_sign_button.configure(state="disabled")
            
            # 根据当前选择的证书类型决定是否显示signtool_frame
            if self.use_self_signed_var.get():
                # 使用自签名证书，显示signtool_frame但禁用
                self.signtool_frame.grid()
                self.enable_signtool_frame(False)
            else:
                # 使用自定义证书，隐藏signtool_frame
                self.signtool_frame.grid_remove()
            
            # 禁用数字签名设置
            self.enable_options_frame(False)

    def auto_detect_signtool(self):
        """自动检测signtool.exe"""
        # 检查用户已设置的路径
        user_path = self.signtool_path_var.get().strip()
        if user_path and os.path.exists(user_path):
            self.signtool_status_var.set("✓ signtool.exe 已找到")
            self.signtool_status_label.configure(foreground="green")
            return True

        # 自动查找常见路径
        signtool_paths = [
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Windows Kits", "10", "bin", "x64", "signtool.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Windows Kits", "10", "bin", "x64", "signtool.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Windows Kits", "8.1", "bin", "x64", "signtool.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Windows Kits", "8.1", "bin", "x64", "signtool.exe"),
        ]

        for path in signtool_paths:
            if os.path.exists(path):
                # 找到了，保存路径
                self.signtool_path_var.set(path)
                self.signtool_status_var.set("✓ signtool.exe 已找到")
                self.signtool_status_label.configure(foreground="green")
                # 隐藏可能的路径提示
                self.signtool_hint_label.grid_remove()
                return True

        # 尝试使用where命令查找
        try:
            result = subprocess.run("where signtool.exe", shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                signtool_path = result.stdout.strip().split('\n')[0]
                if os.path.exists(signtool_path):
                    self.signtool_path_var.set(signtool_path)
                    self.signtool_status_var.set("✓ signtool.exe 已找到")
                    self.signtool_status_label.configure(foreground="green")
                    # 隐藏可能的路径提示
                    self.signtool_hint_label.grid_remove()
                    return True
        except:
            pass

        return False

    def check_signtool(self):
        """检测signtool.exe是否存在"""
        # 优先使用用户指定的路径
        user_path = self.signtool_path_var.get().strip()
        if user_path:
            if os.path.exists(user_path):
                return True
            else:
                # 用户指定了路径但文件不存在，返回False
                return False

        # 查找signtool.exe
        signtool_paths = [
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Windows Kits", "10", "bin", "x64", "signtool.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Windows Kits", "10", "bin", "x64", "signtool.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Windows Kits", "8.1", "bin", "x64", "signtool.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Windows Kits", "8.1", "bin", "x64", "signtool.exe"),
        ]

        for path in signtool_paths:
            if os.path.exists(path):
                return True

        # 尝试使用where命令查找
        try:
            result = subprocess.run("where signtool.exe", shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return True
        except:
            pass

        return False

    def on_cert_type_changed(self):
        """证书类型切换时的回调函数"""
        if self.use_self_signed_var.get():
            # 使用自签名证书，隐藏证书文件相关字段，显示signtool_frame
            self.cert_file_label.grid_remove()
            self.cert_file_entry.grid_remove()
            self.cert_file_button.grid_remove()
            self.cert_password_label.grid_remove()
            self.cert_password_entry.grid_remove()
            # 显示signtool_frame
            self.signtool_frame.grid()
            # 根据是否启用数字签名来控制启用/禁用
            if self.enable_sign_var.get():
                self.enable_signtool_frame(True)
                # 启用"设置自签名证书信息"按钮
                self.config_self_sign_button.configure(state="normal")
                # 检查signtool路径
                self.check_signtool_path()
            else:
                self.enable_signtool_frame(False)
                # 禁用"设置自签名证书信息"按钮
                self.config_self_sign_button.configure(state="disabled")
        else:
            # 使用自定义证书，显示证书文件相关字段，隐藏signtool_frame
            self.cert_file_label.grid()
            self.cert_file_entry.grid()
            self.cert_file_button.grid()
            self.cert_password_label.grid()
            self.cert_password_entry.grid()
            # 隐藏signtool_frame
            self.signtool_frame.grid_remove()
            # 禁用"设置自签名证书信息"按钮
            self.config_self_sign_button.configure(state="disabled")
            # 如果启用了数字签名，直接启用数字签名设置
            if self.enable_sign_var.get():
                self.enable_options_frame(True)

    def open_self_sign_config(self):
        """打开自签名证书信息配置窗口"""
        dialog = tk.Toplevel(self.root)
        dialog.title("自签名证书信息设置")
        dialog.geometry("450x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # 标题
        title_label = ttk.Label(dialog, text="自签名证书信息设置", font=("Arial", 12, "bold"))
        title_label.pack(pady=(15, 10))

        # 说明
        desc_label = ttk.Label(dialog, text="设置自签名证书的详细信息（可选）", foreground="gray")
        desc_label.pack(pady=(0, 10))

        # 创建表单框架
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # 配置网格
        form_frame.columnconfigure(1, weight=1)

        # 通用名称 (CN)
        ttk.Label(form_frame, text="通用名称 (CN):").grid(row=0, column=0, sticky=tk.W, pady=5)
        cn_entry = ttk.Entry(form_frame, textvariable=self.self_sign_cn, width=35)
        cn_entry.grid(row=0, column=1, pady=5, padx=(5, 0), sticky=tk.W)

        # 组织名称 (O)
        ttk.Label(form_frame, text="组织名称 (O):").grid(row=1, column=0, sticky=tk.W, pady=5)
        o_entry = ttk.Entry(form_frame, textvariable=self.self_sign_o, width=35)
        o_entry.grid(row=1, column=1, pady=5, padx=(5, 0), sticky=tk.W)

        # 组织单位 (OU)
        ttk.Label(form_frame, text="组织单位 (OU):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ou_entry = ttk.Entry(form_frame, textvariable=self.self_sign_ou, width=35)
        ou_entry.grid(row=2, column=1, pady=5, padx=(5, 0), sticky=tk.W)

        # 城市 (L)
        ttk.Label(form_frame, text="城市 (L):").grid(row=3, column=0, sticky=tk.W, pady=5)
        l_entry = ttk.Entry(form_frame, textvariable=self.self_sign_l, width=35)
        l_entry.grid(row=3, column=1, pady=5, padx=(5, 0), sticky=tk.W)

        # 省/州 (S)
        ttk.Label(form_frame, text="省/州 (S):").grid(row=4, column=0, sticky=tk.W, pady=5)
        s_entry = ttk.Entry(form_frame, textvariable=self.self_sign_s, width=35)
        s_entry.grid(row=4, column=1, pady=5, padx=(5, 0), sticky=tk.W)

        # 国家代码 (C)
        ttk.Label(form_frame, text="国家代码 (C):").grid(row=5, column=0, sticky=tk.W, pady=5)
        c_entry = ttk.Entry(form_frame, textvariable=self.self_sign_c, width=35)
        c_entry.grid(row=5, column=1, pady=5, padx=(5, 0), sticky=tk.W)
        ttk.Label(form_frame, text="例如: CN, US, JP", foreground="gray", font=("Arial", 8)).grid(row=5, column=2, sticky=tk.W, padx=(5, 0))

        # 友好名称
        ttk.Label(form_frame, text="友好名称:").grid(row=6, column=0, sticky=tk.W, pady=5)
        friendly_entry = ttk.Entry(form_frame, textvariable=self.self_sign_friendly, width=35)
        friendly_entry.grid(row=6, column=1, pady=5, padx=(5, 0), sticky=tk.W)

        # 有效期（年）
        ttk.Label(form_frame, text="有效期（年）:").grid(row=7, column=0, sticky=tk.W, pady=5)
        validity_entry = ttk.Entry(form_frame, textvariable=self.self_sign_validity, width=35)
        validity_entry.grid(row=7, column=1, pady=5, padx=(5, 0), sticky=tk.W)
        ttk.Label(form_frame, text="推荐值: 1-10", foreground="gray", font=("Arial", 8)).grid(row=7, column=2, sticky=tk.W, padx=(5, 0))

        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)

        def save():
            # 验证有效期
            try:
                validity = int(self.self_sign_validity.get())
                if validity < 1 or validity > 100:
                    messagebox.showwarning("提示", "有效期必须在 1-100 年之间")
                    return
            except ValueError:
                messagebox.showwarning("提示", "有效期必须是整数")
                return

            dialog.destroy()
            messagebox.showinfo("成功", "自签名证书信息已保存")

        def reset():
            # 重置为默认值
            self.self_sign_cn.set("SelfSignedCert")
            self.self_sign_o.set("MyCompany")
            self.self_sign_ou.set("Development")
            self.self_sign_l.set("Beijing")
            self.self_sign_s.set("Beijing")
            self.self_sign_c.set("CN")
            self.self_sign_friendly.set("SelfSigned Code Signing Certificate")
            self.self_sign_validity.set(10)

        ttk.Button(button_frame, text="保存", command=save, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置默认", command=reset, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)

    def create_log_settings(self, parent):
        """创建日志设置界面"""
        # 日志文本框
        self.log_text = tk.Text(parent, height=20, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # 配置网格权重
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

    def add_library(self):
        """添加库到列表"""
        library_name = self.library_var.get().strip()
        
        if not library_name:
            messagebox.showerror("错误", "请输入库名称")
            return
        
        # 检查是否已添加
        if library_name in self.hidden_imports:
            messagebox.showwarning("警告", "该库已添加")
            return
        
        # 添加到列表
        self.hidden_imports.append(library_name)
        
        # 更新列表显示
        self.update_library_list()
        
        # 清空输入框
        self.library_var.set("")
    
    def add_common_library(self, library_name):
        """添加常见库"""
        if library_name not in self.hidden_imports:
            self.hidden_imports.append(library_name)
            self.update_library_list()
            self.log(f"已添加库: {library_name}", "#5A96DB")
    
    def delete_library(self):
        """删除选中的库"""
        selection = self.library_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的库")
            return
        
        index = selection[0]
        removed_lib = self.hidden_imports.pop(index)
        self.update_library_list()
        self.log(f"已删除库: {removed_lib}", "red")
    
    def clear_libraries(self):
        """清空所有库"""
        if not self.hidden_imports:
            return
        
        if messagebox.askyesno("确认", "确定要清空所有库吗？"):
            self.hidden_imports = []
            self.update_library_list()
            self.log("已清空所有库", "red")
    
    def update_library_list(self):
        """更新库列表显示"""
        self.library_listbox.delete(0, tk.END)
        for library in self.hidden_imports:
            self.library_listbox.insert(tk.END, library)
    
    def on_library_drop(self, event):
        """处理库列表拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 处理每个拖放的文件
        added_count = 0
        for file_path in files:
            # 去除可能的花括号和引号
            file_path = file_path.strip('{}').strip('"').strip("'")
            
            if not file_path:
                continue
            
            # 检查是否是.py文件
            if file_path.lower().endswith('.py'):
                # 从Python文件中提取导入的库
                libraries = self.extract_imports_from_file(file_path)
                for lib in libraries:
                    if lib not in self.hidden_imports:
                        self.hidden_imports.append(lib)
                        added_count += 1
                        self.log(f"从文件中提取库: {lib}", "#5A96DB")
            else:
                # 如果不是.py文件，尝试将文件名作为库名
                # 去除扩展名
                lib_name = os.path.splitext(os.path.basename(file_path))[0]
                if lib_name and lib_name not in self.hidden_imports:
                    self.hidden_imports.append(lib_name)
                    added_count += 1
                    self.log(f"添加库: {lib_name}", "#5A96DB")
        
        # 更新列表显示
        self.update_library_list()

        if added_count > 0:
            self.log(f"通过拖放成功添加 {added_count} 个库", "#5A96DB")
    
    def extract_imports_from_file(self, file_path):
        """从Python文件中提取导入的库名"""
        libraries = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 匹配常见的导入语句
            import re
            
            # 匹配: import xxx
            matches = re.findall(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE)
            libraries.extend(matches)
            
            # 匹配: import xxx as yyy
            matches = re.findall(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+as', content, re.MULTILINE)
            libraries.extend(matches)
            
            # 匹配: import xxx, yyy, zzz
            matches = re.findall(r'^import\s+[a-zA-Z_][a-zA-Z0-9_]*,\s*([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE)
            libraries.extend(matches)
            
            # 匹配: from xxx import yyy
            matches = re.findall(r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import', content, re.MULTILINE)
            libraries.extend(matches)
            
            # 去重
            libraries = list(set(libraries))
            
            # 过滤掉Python内置模块（可选）
            builtin_modules = {'os', 'sys', 'json', 'time', 'datetime', 'math', 'random', 're', 'typing', 'collections', 'itertools', 'functools'}
            libraries = [lib for lib in libraries if lib not in builtin_modules]
            
        except Exception as e:
            self.log(f"读取文件失败 {file_path}: {str(e)}", "red")
        
        return libraries
    
    def browse_path(self):
        """浏览选择工作路径"""
        path = filedialog.askdirectory(title="选择工作路径")
        if path:
            self.path_var.set(path)
    
    def browse_file(self):
        """浏览选择Python文件"""
        file_path = filedialog.askopenfilename(
            title="选择Python文件",
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if file_path:
            # 存储文件的完整绝对路径
            self.file_var.set(os.path.abspath(file_path))
            # 如果工作路径为空，则设置为文件所在目录
            if not self.path_var.get().strip():
                self.path_var.set(os.path.dirname(file_path))
    
    def on_python_file_drop(self, event):
        """处理Python文件拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)

        if not files:
            return

        # 只处理第一个文件
        file_path = files[0]
        # 去除可能的花括号和引号
        file_path = file_path.strip('{}').strip('"').strip("'")

        if not file_path:
            return

        # 检查是否是.py文件
        if not file_path.lower().endswith('.py'):
            messagebox.showwarning("警告", "请拖放Python文件（.py）")
            return

        # 检查文件是否存在
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return

        # 存储文件的完整绝对路径
        self.file_var.set(os.path.abspath(file_path))
        # 如果工作路径为空，则设置为文件所在目录
        if not self.path_var.get().strip():
            self.path_var.set(os.path.dirname(file_path))
        self.log(f"已选择Python文件: {file_path}", "#5A96DB")

    def on_icon_drop(self, event):
        """处理图标文件拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 只处理第一个文件
        file_path = files[0]
        # 去除可能的花括号和引号
        file_path = file_path.strip('{}').strip('"').strip("'")
        
        if not file_path:
            return
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
        
        # 检查是否是图标文件（.ico）
        if not file_path.lower().endswith('.ico'):
            result = messagebox.askyesno(
                "提示",
                f"拖放的文件不是.ico格式：{os.path.basename(file_path)}\n\n是否继续使用？\n（建议使用.ico格式的图标文件）"
            )
            if not result:
                return
        
        self.icon_var.set(file_path)
        self.log(f"已选择图标文件: {file_path}", "#5A96DB")
    
    def on_desktop_icon_drop(self, event):
        """处理桌面快捷方式图标拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 只处理第一个文件
        file_path = files[0]
        # 去除可能的花括号和引号
        file_path = file_path.strip('{}').strip('"').strip("'")
        
        if not file_path:
            return
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
        
        # 检查是否是图标文件（.ico）
        if not file_path.lower().endswith('.ico'):
            result = messagebox.askyesno(
                "提示",
                f"拖放的文件不是.ico格式：{os.path.basename(file_path)}\n\n是否继续使用？\n（建议使用.ico格式的图标文件）"
            )
            if not result:
                return
        
        self.desktop_icon_var.set(file_path)
        self.log(f"已选择桌面快捷方式图标: {file_path}", "#5A96DB")
    
    def on_source_drop(self, event):
        """处理资源文件源路径拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 清理文件路径
        cleaned_files = []
        for file_path in files:
            # 去除可能的花括号和引号
            file_path = file_path.strip('{}').strip('"').strip("'")
            if file_path:
                cleaned_files.append(file_path)
        
        if not cleaned_files:
            return
        
        # 如果只有一个文件，设置到源路径输入框（保持原有行为）
        if len(cleaned_files) == 1:
            file_path = cleaned_files[0]
            
            # 检查路径是否存在
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"路径不存在: {file_path}")
                return
            
            self.source_var.set(file_path)
            # 自动生成目标路径
            self.auto_generate_target()
            self.log(f"已选择资源路径: {file_path}", "#5A96DB")
        else:
            # 如果有多个文件，批量添加到资源列表
            added_count = 0
            for file_path in cleaned_files:
                # 检查路径是否存在
                if not os.path.exists(file_path):
                    self.log(f"拖放的路径不存在: {file_path}", "red")
                    continue
                
                # 检查是否已添加
                already_exists = False
                for resource in self.resource_files:
                    if resource['source'] == file_path:
                        already_exists = True
                        break
                
                if already_exists:
                    self.log(f"资源已存在，跳过: {file_path}", "orange")
                    continue
                
                # 自动生成目标路径
                if os.path.isfile(file_path):
                    target_path = os.path.basename(file_path)
                else:
                    target_path = os.path.basename(file_path)
                    if not target_path:
                        target_path = os.path.basename(os.path.dirname(file_path))
                
                # 添加到列表
                resource = {
                    'source': file_path,
                    'target': target_path
                }
                self.resource_files.append(resource)
                added_count += 1
                self.log(f"已添加资源: {file_path}", "#5A96DB")
            
            # 更新列表显示
            self.update_resource_list()

            if added_count > 0:
                self.log(f"通过拖放成功添加 {added_count} 个资源文件", "#5A96DB")
    
    def on_signtool_drop(self, event):
        """处理signtool路径拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 只处理第一个文件
        file_path = files[0]
        # 去除可能的花括号和引号
        file_path = file_path.strip('{}').strip('"').strip("'")
        
        if not file_path:
            return
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
        
        # 检查是否是.signtool.exe文件
        if not os.path.basename(file_path).lower() == 'signtool.exe':
            result = messagebox.askyesno(
                "提示",
                f"拖放的文件不是signtool.exe：{os.path.basename(file_path)}\n\n是否继续使用？\n（建议使用signtool.exe文件）"
            )
            if not result:
                return
        
        self.signtool_path_var.set(file_path)
        self.check_signtool_path()
        self.log(f"已选择signtool路径: {file_path}", "#5A96DB")
    
    def on_cert_file_drop(self, event):
        """处理证书文件拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 只处理第一个文件
        file_path = files[0]
        # 去除可能的花括号和引号
        file_path = file_path.strip('{}').strip('"').strip("'")
        
        if not file_path:
            return
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
        
        # 检查是否是证书文件（.pfx或.p12）
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ['.pfx', '.p12']:
            result = messagebox.askyesno(
                "提示",
                f"拖放的文件不是证书格式：{os.path.basename(file_path)}\n\n是否继续使用？\n（建议使用.pfx或.p12格式的证书文件）"
            )
            if not result:
                return
        
        self.cert_file_var.set(file_path)
        self.log(f"已选择证书文件: {file_path}", "#5A96DB")
    
    def on_exe_drop_to_sign(self, event):
        """处理EXE文件拖放到一键签名按钮的事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 只处理第一个文件
        file_path = files[0]
        # 去除可能的花括号和引号
        file_path = file_path.strip('{}').strip('"').strip("'")
        
        if not file_path:
            return
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
        
        # 检查是否是EXE文件
        if not file_path.lower().endswith('.exe'):
            messagebox.showwarning("警告", "请拖放EXE文件（.exe）")
            return
        
        # 直接调用签名方法
        self.sign_single_exe(file_path)
    
    def browse_icon(self):
        """浏览选择图标文件"""
        icon_path = filedialog.askopenfilename(
            title="选择图标文件",
            filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")]
        )
        if icon_path:
            self.icon_var.set(icon_path)

    def browse_desktop_icon(self):
        """浏览选择桌面快捷方式图标文件"""
        icon_path = filedialog.askopenfilename(
            title="选择桌面快捷方式图标文件",
            filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")]
        )
        if icon_path:
            self.desktop_icon_var.set(icon_path)

    def browse_cert_file(self):
        """浏览选择数字签名证书文件"""
        cert_path = filedialog.askopenfilename(
            title="选择数字签名证书文件",
            filetypes=[("证书文件", "*.pfx;*.p12"), ("PFX证书", "*.pfx"), ("P12证书", "*.p12"), ("所有文件", "*.*")]
        )
        if cert_path:
            self.cert_file_var.set(cert_path)

    def browse_signtool(self):
        """浏览选择signtool.exe文件"""
        signtool_path = filedialog.askopenfilename(
            title="选择signtool.exe文件",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if signtool_path:
            self.signtool_path_var.set(signtool_path)
            self.check_signtool_path()

    def download_windows_sdk(self):
        """下载Windows SDK"""
        # 显示提示信息
        messagebox.showinfo(
            "安装提示",
            "请务必选择以下组件进行安装：\n\n"
            "✓ Windows SDK Signing Tools for Desktop Apps\n\n"
            "其他组件可以不选。"
        )
        import webbrowser
        url = "https://developer.microsoft.com/zh-cn/windows/downloads/windows-sdk/"
        try:
            webbrowser.open(url)
            self.log(f"已打开Windows SDK下载页面: {url}", "#5A96DB")
        except Exception as e:
            self.log(f"打开Windows SDK下载页面失败: {str(e)}", "red")
            messagebox.showerror("错误", f"无法打开浏览器：{str(e)}")

    def enable_signtool_frame(self, enabled):
        """启用或禁用签名工具设置中的所有控件"""
        state = "normal" if enabled else "disabled"
        # signtool路径相关
        self.signtool_path_label.configure(state=state)
        self.signtool_path_entry.configure(state=state)
        self.browse_signtool_button.configure(state=state)
        self.download_sdk_button.configure(state=state)
    
    def check_signtool_path(self):
        """检查signtool路径是否有效"""
        user_path = self.signtool_path_var.get().strip()
        if user_path:
            if os.path.exists(user_path):
                self.signtool_status_var.set("✓ signtool.exe 已找到")
                self.signtool_status_label.configure(foreground="green")
                # 隐藏可能的路径提示
                self.signtool_hint_label.grid_remove()
                # 只有在启用了数字签名时才启用options_frame
                if self.enable_sign_var.get():
                    self.enable_options_frame(True)
                return True
            else:
                self.signtool_status_var.set("✗ 文件不存在")
                self.signtool_status_label.configure(foreground="red")
                # 显示可能的路径提示
                self.signtool_hint_label.grid()
                # 禁用options_frame
                self.enable_options_frame(False)
                return False
        else:
            self.signtool_status_var.set("未检测")
            self.signtool_status_label.configure(foreground="gray")
            # 显示可能的路径提示
            self.signtool_hint_label.grid()
            # 禁用options_frame
            self.enable_options_frame(False)
            return False

    def enable_options_frame(self, enabled):
        """启用或禁用数字签名设置中的所有控件"""
        state = "normal" if enabled else "disabled"
        # 证书文件相关
        self.cert_file_label.configure(state=state)
        self.cert_file_entry.configure(state=state)
        self.cert_file_button.configure(state=state)
        # 证书密码相关
        self.cert_password_label.configure(state=state)
        self.cert_password_entry.configure(state=state)
        # 时间戳服务器相关
        self.timestamp_server_label.configure(state=state)
        self.timestamp_entry.configure(state=state)
        self.timestamp_default_label.configure(state=state)
        self.common_timestamp_label.configure(state=state)
        self.timestamp_combo.configure(state=state)
        # 一键签名按钮
        self.sign_single_button.configure(state=state)

    def sign_single_exe(self, exe_path=None):
        """一键签名单个EXE文件"""
        # 检查是否有任务正在进行
        if self.is_busy:
            messagebox.showwarning("提示", "正在执行其他任务，请稍候...")
            return
        
        # 检查证书设置
        cert_file = self.cert_file_var.get().strip()
        cert_password = self.cert_password_var.get()
        timestamp_server = self.timestamp_server_var.get().strip()

        if not self.use_self_signed_var.get() and not cert_file:
            messagebox.showwarning("提示", "请先设置证书文件和密码\n\n切换到\"数字签名\"选项卡进行配置")
            return

        # 如果没有提供exe_path，让用户选择
        if not exe_path:
            exe_path = filedialog.askopenfilename(
                title="选择要签名的EXE文件",
                filetypes=[("EXE文件", "*.exe"), ("所有文件", "*.*")]
            )

        if not exe_path:
            return

        # 确认签名
        cert_type = "自签名证书" if self.use_self_signed_var.get() else "自定义证书"
        result = messagebox.askyesno(
            "确认签名",
            f"确定要对以下文件进行数字签名吗？\n\n文件: {exe_path}\n\n证书类型: {cert_type}\n时间戳: {timestamp_server}"
        )

        if not result:
            return

        # 禁用按钮，防止重复点击
        self.sign_single_button.configure(state='disabled')
        self.is_busy = True
        
        # 定义签名线程函数
        def _sign():
            try:
                self.log(f"开始签名: {exe_path}")
                success = self.sign_exe(exe_path)

                # 在主线程中显示结果
                def show_result():
                    if success:
                        messagebox.showinfo("成功", "数字签名成功！")
                        # 如果使用自签名证书，询问是否删除临时文件
                        if self.use_self_signed_var.get():
                            result = messagebox.askyesno(
                                "清理临时文件",
                                "是否删除自签名证书临时文件？\n\n临时文件位于系统临时目录下，\n以 'self_signed_cert_' 开头的文件夹"
                            )
                            if result:
                                self.log("正在清理自签名证书临时文件...", "#5A96DB")
                                self.cleanup_self_signed_cert_temp()
                            else:
                                self.log("跳过清理自签名证书临时文件", "#5A96DB")
                    else:
                        messagebox.showerror("失败", "数字签名失败，请查看日志了解详情")
                    self.sign_single_button.configure(state='normal')
                    self.is_busy = False

                self.root.after(0, show_result)
            except Exception as e:
                # 在主线程中显示错误
                def show_error():
                    self.log(f"签名过程出错: {str(e)}", "red")
                    messagebox.showerror("错误", f"签名过程出错: {str(e)}")
                    self.sign_single_button.configure(state='normal')
                    self.is_busy = False
                
                self.root.after(0, show_error)
        
        # 启动后台线程
        self.current_thread = threading.Thread(target=_sign, daemon=True)
        self.current_thread.start()

    def browse_source(self):
        """浏览选择资源文件或文件夹"""
        # 创建自定义对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("选择资源")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 标题
        title_label = ttk.Label(dialog, text="选择资源类型", font=("Arial", 12, "bold"))
        title_label.pack(pady=(20, 10))
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        # 存储用户选择
        result = {'choice': None}
        
        def select_file():
            result['choice'] = 'file'
            dialog.destroy()
        
        def select_folder():
            result['choice'] = 'folder'
            dialog.destroy()
        
        def cancel():
            result['choice'] = None
            dialog.destroy()
        
        # 按钮
        ttk.Button(button_frame, text="文件", command=select_file, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="文件夹", command=select_folder, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # 等待对话框关闭
        self.root.wait_window(dialog)
        
        # 处理用户选择
        if result['choice'] == 'file':
            source_path = filedialog.askopenfilename(
                title="选择资源文件",
                filetypes=[("所有文件", "*.*")]
            )
        elif result['choice'] == 'folder':
            source_path = filedialog.askdirectory(title="选择资源文件夹")
        else:
            return
        
        if source_path:
            self.source_var.set(source_path)
            self.auto_generate_target()

    def browse_source_multiple(self):
        """批量浏览选择多个资源文件"""
        # 创建自定义对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("批量添加")
        dialog.geometry("450x180")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 标题
        title_label = ttk.Label(dialog, text="批量添加类型", font=("Arial", 12, "bold"))
        title_label.pack(pady=(20, 10))
        
        # 说明
        desc_label = ttk.Label(dialog, text="请选择批量添加的方式", foreground="gray")
        desc_label.pack(pady=(0, 10))
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        # 存储用户选择
        result = {'choice': None}
        
        def select_files():
            result['choice'] = 'files'
            dialog.destroy()
        
        def select_folder():
            result['choice'] = 'folder'
            dialog.destroy()
        
        def cancel():
            result['choice'] = None
            dialog.destroy()
        
        # 按钮
        ttk.Button(button_frame, text="批量文件", command=select_files, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="文件夹", command=select_folder, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # 等待对话框关闭
        self.root.wait_window(dialog)
        
        # 处理用户选择
        if result['choice'] is None:  # 取消
            return
        elif result['choice'] == 'files':  # 批量选择多个文件
            source_paths = filedialog.askopenfilenames(
                title="批量选择资源文件（可多选）",
                filetypes=[("所有文件", "*.*")]
            )
            
            if source_paths:
                # 创建自定义对话框
                dialog = tk.Toplevel(self.root)
                dialog.title("目标路径")
                dialog.geometry("450x200")
                dialog.transient(self.root)
                dialog.grab_set()
                
                # 居中显示
                dialog.update_idletasks()
                x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
                y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
                dialog.geometry(f"+{x}+{y}")
                
                # 标题
                title_label = ttk.Label(dialog, text=f"已选择 {len(source_paths)} 个文件", font=("Arial", 12, "bold"))
                title_label.pack(pady=(20, 10))
                
                # 说明
                desc_label = ttk.Label(dialog, text="请选择目标路径设置方式", foreground="gray")
                desc_label.pack(pady=(0, 10))
                
                # 按钮框架
                button_frame = ttk.Frame(dialog)
                button_frame.pack(pady=10)
                
                # 存储用户选择
                result = {'choice': None}
                
                def auto_generate():
                    result['choice'] = 'auto'
                    dialog.destroy()
                
                def unified():
                    result['choice'] = 'unified'
                    dialog.destroy()
                
                def cancel():
                    result['choice'] = None
                    dialog.destroy()
                
                # 按钮
                ttk.Button(button_frame, text="自动生成", command=auto_generate, width=15).pack(side=tk.LEFT, padx=5)
                ttk.Button(button_frame, text="统一设置", command=unified, width=15).pack(side=tk.LEFT, padx=5)
                ttk.Button(button_frame, text="取消", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
                
                # 等待对话框关闭
                self.root.wait_window(dialog)
                
                # 处理用户选择
                if result['choice'] is None:  # 取消
                    return
                elif result['choice'] == 'auto':  # 自动生成
                    # 自动生成每个文件的目标路径
                    for source_path in source_paths:
                        target_path = os.path.basename(source_path)
                        self._add_resource_to_list(source_path, target_path)
                else:  # 统一设置
                    # 让用户输入统一的目标路径前缀
                    target_prefix = filedialog.askdirectory(
                        title="选择目标文件夹（所有文件将放在此文件夹下）"
                    )
                    if target_prefix:
                        for source_path in source_paths:
                            target_path = os.path.join(target_prefix, os.path.basename(source_path))
                            self._add_resource_to_list(source_path, target_path)
                
                self.log(f"已批量添加 {len(source_paths)} 个资源文件", "#5A999")
        else:  # 选择整个文件夹
            source_path = filedialog.askdirectory(title="选择资源文件夹")
            
            if source_path:
                # 让用户选择目标路径
                target_path = filedialog.askdirectory(
                    title="选择目标路径（打包后的文件夹名）"
                )
                if not target_path:
                    # 如果没有选择，使用文件夹名
                    target_path = os.path.basename(source_path)
                
                self._add_resource_to_list(source_path, target_path)
                self.log(f"已添加文件夹: {source_path}", "#5A96DB")

    def _add_resource_to_list(self, source_path, target_path):
        """内部方法：添加单个资源到列表（不显示错误消息）"""
        if not source_path or not target_path:
            return
        
        if not os.path.exists(source_path):
            return
        
        # 检查是否已添加
        for resource in self.resource_files:
            if resource['source'] == source_path:
                return
        
        # 添加到列表
        resource = {
            'source': source_path,
            'target': target_path
        }
        self.resource_files.append(resource)
        
        # 更新列表显示
        self.update_resource_list()
    
    def auto_generate_target(self):
        """自动生成目标路径"""
        source_path = self.source_var.get()
        if not source_path:
            return
        
        # 如果是文件，目标路径为文件名
        if os.path.isfile(source_path):
            target_path = os.path.basename(source_path)
        # 如果是文件夹，目标路径为文件夹名
        else:
            target_path = os.path.basename(source_path)
            if not target_path:  # 如果文件夹是根目录，使用父文件夹名
                target_path = os.path.basename(os.path.dirname(source_path))
        
        self.target_var.set(target_path)
    
    def add_resource(self):
        """添加资源文件到列表"""
        source_path = self.source_var.get().strip()
        target_path = self.target_var.get().strip()
        
        if not source_path:
            messagebox.showerror("错误", "请选择源路径")
            return
        
        if not target_path:
            messagebox.showerror("错误", "请输入目标路径")
            return
        
        if not os.path.exists(source_path):
            messagebox.showerror("错误", f"源路径不存在: {source_path}")
            return
        
        # 检查是否已添加
        for resource in self.resource_files:
            if resource['source'] == source_path:
                messagebox.showwarning("警告", "该资源已添加")
                return
        
        # 添加到列表
        resource = {
            'source': source_path,
            'target': target_path
        }
        self.resource_files.append(resource)
        
        # 更新列表显示
        self.update_resource_list()
        
        # 只清空目标路径，保留源路径方便连续添加
        self.target_var.set("")
    
    def delete_resource(self):
        """删除选中的资源"""
        selection = self.resource_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的资源")
            return
        
        index = selection[0]
        self.resource_files.pop(index)
        self.update_resource_list()
    
    def clear_resources(self):
        """清空所有资源"""
        if not self.resource_files:
            return
        
        if messagebox.askyesno("确认", "确定要清空所有资源文件吗？"):
            self.resource_files = []
            self.update_resource_list()
    
    def move_up(self):
        """上移选中的资源"""
        selection = self.resource_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        # 交换位置
        self.resource_files[index], self.resource_files[index-1] = self.resource_files[index-1], self.resource_files[index]
        self.update_resource_list()
        # 重新选中
        self.resource_listbox.selection_set(index-1)
    
    def move_down(self):
        """下移选中的资源"""
        selection = self.resource_listbox.curselection()
        if not selection or selection[0] == len(self.resource_files)-1:
            return
        
        index = selection[0]
        # 交换位置
        self.resource_files[index], self.resource_files[index+1] = self.resource_files[index+1], self.resource_files[index]
        self.update_resource_list()
        # 重新选中
        self.resource_listbox.selection_set(index+1)

    def update_resource_list(self):
        """更新资源文件列表显示"""
        self.resource_listbox.delete(0, tk.END)
        for resource in self.resource_files:
            display_text = f"{resource['source']} -> {resource['target']}"
            self.resource_listbox.insert(tk.END, display_text)

    def on_resource_drop(self, event):
        """处理资源文件拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 处理每个拖放的文件/文件夹
        added_count = 0
        for file_path in files:
            # 去除可能的花括号和引号
            file_path = file_path.strip('{}').strip('"').strip("'")
            
            if not file_path:
                continue
            
            # 检查路径是否存在
            if not os.path.exists(file_path):
                self.log(f"拖放的路径不存在: {file_path}", "red")
                continue
            
            # 检查是否已添加
            already_exists = False
            for resource in self.resource_files:
                if resource['source'] == file_path:
                    already_exists = True
                    break
            
            if already_exists:
                self.log(f"资源已存在，跳过: {file_path}", "orange")
                continue
            
            # 自动生成目标路径
            if os.path.isfile(file_path):
                target_path = os.path.basename(file_path)
            else:
                target_path = os.path.basename(file_path)
                if not target_path:
                    target_path = os.path.basename(os.path.dirname(file_path))
            
            # 添加到列表
            resource = {
                'source': file_path,
                'target': target_path
            }
            self.resource_files.append(resource)
            added_count += 1
            self.log(f"已添加资源: {file_path}", "#5A96DB")
        
        # 更新列表显示
        self.update_resource_list()

        if added_count > 0:
            self.log(f"通过拖放成功添加 {added_count} 个资源文件", "#5A96DB")
    
    def load_config(self):
        """加载保存的配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                    self.path_var.set(config.get('path', os.getcwd()))
                    self.file_var.set(config.get('file', ''))
                    self.icon_var.set(config.get('icon', ''))
                    self.desktop_icon_var.set(config.get('desktop_icon', ''))
                    self.create_shortcut_var.set(config.get('create_shortcut', False))
                    self.uac_admin_var.set(config.get('uac_admin', False))
                    self.version_var.set(config.get('version', ''))
                    self.file_description_var.set(config.get('file_description', ''))
                    self.copyright_var.set(config.get('copyright', ''))
                    self.language_var.set(config.get('language', '中文（简体）'))
                    self.onefile_var.set(config.get('onefile', True))
                    self.console_var.set(config.get('console', True))
                    self.resource_files = config.get('resources', [])
                    self.hidden_imports = config.get('hidden_imports', [])
                    self.enable_sign_var.set(config.get('enable_sign', False))
                    self.use_self_signed_var.set(config.get('use_self_signed', True))
                    self.cert_file_var.set(config.get('cert_file', ''))
                    self.cert_password_var.set(config.get('cert_password', ''))
                    self.timestamp_server_var.set(config.get('timestamp_server', 'http://timestamp.digicert.com'))
                    self.signtool_path_var.set(config.get('signtool_path', ''))
                    # 加载自签名证书信息
                    self.self_sign_cn.set(config.get('self_sign_cn', 'SelfSignedCert'))
                    self.self_sign_o.set(config.get('self_sign_o', 'MyCompany'))
                    self.self_sign_ou.set(config.get('self_sign_ou', 'Development'))
                    self.self_sign_l.set(config.get('self_sign_l', 'Beijing'))
                    self.self_sign_s.set(config.get('self_sign_s', 'Beijing'))
                    self.self_sign_c.set(config.get('self_sign_c', 'CN'))
                    self.self_sign_friendly.set(config.get('self_sign_friendly', 'SelfSigned Code Signing Certificate'))
                    self.self_sign_validity.set(config.get('self_sign_validity', 10))

                    self.update_resource_list()
                    self.update_library_list()

                    # 检查signtool路径
                    self.check_signtool_path()

                    # 根据配置启用/禁用框架
                    if self.enable_sign_var.get():
                        # 启用数字签名
                        self.cert_type_radio1.configure(state="normal")
                        self.cert_type_radio2.configure(state="normal")
                        self.config_self_sign_button.configure(state="normal")
                        if self.use_self_signed_var.get():
                            # 使用自签名证书，显示signtool_frame并启用
                            self.signtool_frame.grid()
                            self.enable_signtool_frame(True)
                            if self.check_signtool_path():
                                self.enable_options_frame(True)
                            else:
                                self.enable_options_frame(False)
                        else:
                            # 使用自定义证书，隐藏signtool_frame
                            self.signtool_frame.grid_remove()
                            self.enable_options_frame(True)
                    else:
                        # 禁用数字签名，显示signtool_frame但禁用
                        self.cert_type_radio1.configure(state="disabled")
                        self.cert_type_radio2.configure(state="disabled")
                        self.config_self_sign_button.configure(state="disabled")
                        self.signtool_frame.grid()
                        self.enable_signtool_frame(False)
                        self.enable_options_frame(False)

            except Exception as e:
                self.log(f"加载配置失败: {str(e)}", "red")
                self.path_var.set(os.getcwd())
        else:
            self.path_var.set(os.getcwd())
            # 没有配置文件时，也要设置控件的初始状态
            self.on_enable_sign_changed()
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            'path': self.path_var.get(),
            'file': self.file_var.get(),
            'icon': self.icon_var.get(),
            'desktop_icon': self.desktop_icon_var.get(),
            'create_shortcut': self.create_shortcut_var.get(),
            'uac_admin': self.uac_admin_var.get(),
            'version': self.version_var.get(),
            'file_description': self.file_description_var.get(),
            'copyright': self.copyright_var.get(),
            'language': self.language_var.get(),
            'onefile': self.onefile_var.get(),
            'console': self.console_var.get(),
            'resources': self.resource_files,
            'hidden_imports': self.hidden_imports,
            'enable_sign': self.enable_sign_var.get(),
            'use_self_signed': self.use_self_signed_var.get(),
            'cert_file': self.cert_file_var.get(),
            'cert_password': self.cert_password_var.get(),
            'timestamp_server': self.timestamp_server_var.get(),
            'signtool_path': self.signtool_path_var.get(),
            # 自签名证书信息
            'self_sign_cn': self.self_sign_cn.get(),
            'self_sign_o': self.self_sign_o.get(),
            'self_sign_ou': self.self_sign_ou.get(),
            'self_sign_l': self.self_sign_l.get(),
            'self_sign_s': self.self_sign_s.get(),
            'self_sign_c': self.self_sign_c.get(),
            'self_sign_friendly': self.self_sign_friendly.get(),
            'self_sign_validity': self.self_sign_validity.get()
        }

        # 检查是否所有配置都是默认值（空值/False）
        is_default = (
            not config['file'] and
            not config['icon'] and
            not config['desktop_icon'] and
            not config['create_shortcut'] and
            not config['uac_admin'] and
            not config['version'] and
            not config['file_description'] and
            not config['copyright'] and
            config['language'] == '中文（简体）' and
            config['onefile'] and
            config['console'] and
            not config['resources'] and
            not config['hidden_imports'] and
            not config['enable_sign'] and
            config['use_self_signed'] and
            not config['cert_file'] and
            not config['cert_password'] and
            config['timestamp_server'] == 'http://timestamp.digicert.com' and
            not config['signtool_path'] and
            config['self_sign_cn'] == 'SelfSignedCert' and
            config['self_sign_o'] == 'MyCompany' and
            config['self_sign_ou'] == 'Development' and
            config['self_sign_l'] == 'Beijing' and
            config['self_sign_s'] == 'Beijing' and
            config['self_sign_c'] == 'CN' and
            config['self_sign_friendly'] == 'SelfSigned Code Signing Certificate' and
            config['self_sign_validity'] == 10
        )

        # 如果配置都是默认值且配置文件不存在，则不创建文件
        if is_default and not os.path.exists(self.config_file):
            return

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"保存配置失败: {str(e)}", "red")
    
    def create_version_file(self, path, version, file_name, copyright=None, language=None, file_description=None):
        """创建版本信息文件"""
        try:
            # 语言代码映射
            language_codes = {
                "中文（简体）": 0x0804,
                "中文（繁体）": 0x0404,
                "英语（美国）": 0x0409,
                "英语（英国）": 0x0809,
                "日语": 0x0411,
                "韩语": 0x0412,
                "法语": 0x040c,
                "德语": 0x0407,
                "西班牙语": 0x0c0a,
                "俄语": 0x0419
            }

            # 获取语言代码，默认为中文简体
            lang_code = language_codes.get(language, 0x0804) if language else 0x0804

            # 解析版本号
            version_parts = version.split('.')
            if len(version_parts) < 4:
                # 补全版本号到4位
                version_parts = version_parts + ['0'] * (4 - len(version_parts))
            version_parts = version_parts[:4]

            # 处理版权信息
            copyright_text = copyright if copyright else ''

            # 提取文件名（不含路径和扩展名），避免显示目录而不是文件名
            product_name = os.path.splitext(os.path.basename(file_name))[0]

            # 处理文件说明，如果未提供则使用product_name
            file_description_text = file_description if file_description else product_name

            # 生成版本信息文件内容
            version_content = f"""# UTF-8
#
# For more details about fixed file info:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({int(version_parts[0])}, {int(version_parts[1])}, {int(version_parts[2])}, {int(version_parts[3])}),
    prodvers=({int(version_parts[0])}, {int(version_parts[1])}, {int(version_parts[2])}, {int(version_parts[3])}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'{lang_code:04x}04B0',
        [StringStruct(u'CompanyName', u''),
        StringStruct(u'FileDescription', u'{file_description_text}'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'{product_name}'),
        StringStruct(u'LegalCopyright', u'{copyright_text}'),
        StringStruct(u'OriginalFilename', u'{product_name}.exe'),
        StringStruct(u'ProductName', u'{product_name}'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [{lang_code}, 1200])])
  ]
)
"""

            # 保存版本信息文件
            version_file_path = os.path.join(path, 'version_info.txt')
            with open(version_file_path, 'w', encoding='utf-8') as f:
                f.write(version_content)

            self.log(f"已创建版本信息文件: {version_file_path}", "#5A96DB")
            return version_file_path

        except Exception as e:
            self.log(f"创建版本信息文件失败: {str(e)}", "red")
            return None

    def get_system_python(self):
        """获取系统Python路径"""
        import sys

        # 检测是否在打包后的环境中运行
        if getattr(sys, 'frozen', False):
            # 在打包环境中，需要找到系统Python
            python_path = None

            # 尝试常见的方法找到系统Python
            import shutil
            python_path = shutil.which('python')
            if python_path:
                self.log(f"找到系统Python: {python_path}", "#5A96DB")
                return python_path

            python_path = shutil.which('python3')
            if python_path:
                self.log(f"找到系统Python3: {python_path}", "#5A96DB")
                return python_path

            # 尝试从注册表获取Python路径（Windows）
            if sys.platform == 'win32':
                try:
                    import winreg
                except ImportError:
                    self.log("无法导入winreg模块")
                else:
                    # 尝试从注册表获取Python路径
                    for key in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                        try:
                            with winreg.OpenKey(key, r'SOFTWARE\Python\PythonCore') as root_key:
                                i = 0
                                while True:
                                    try:
                                        version = winreg.EnumKey(root_key, i)
                                        i += 1
                                    except OSError:
                                        break
                                    try:
                                        with winreg.OpenKey(root_key, f'{version}\\InstallPath') as install_key:
                                            python_path = winreg.QueryValue(install_key, '')
                                            if python_path:
                                                python_exe = os.path.join(python_path, 'python.exe')
                                                if os.path.exists(python_exe):
                                                    self.log(f"从注册表找到Python: {python_exe}", "#5A96DB")
                                                    return python_exe
                                    except Exception:
                                        pass
                        except Exception:
                            pass

            # 如果都找不到，提示用户
            self.log("警告：无法找到系统Python，请确保已安装Python并添加到PATH环境变量中")
            return None

        else:
            # 在开发环境中，使用当前Python
            self.log(f"使用当前Python: {sys.executable}", "#5A96DB")
            return sys.executable

    def start_pack(self):
        """开始打包"""
        # 检查是否有任务正在进行
        if self.is_busy:
            messagebox.showwarning("提示", "正在执行其他任务，请稍候...")
            return

        # 保存配置（只在开始打包时保存）
        self.save_config()

        # 获取系统Python路径
        python_exe = self.get_system_python()
        if not python_exe:
            messagebox.showerror(
                "错误",
                "无法找到系统Python！\n\n"
                "请确保已安装Python并添加到PATH环境变量中。\n"
                "或者直接使用Python脚本运行此工具。"
            )
            return

        # 检查PyInstaller是否已安装
        try:
            import PyInstaller
            self.log_safe("PyInstaller已安装", "#5A96DB")
        except ImportError:
            self.log_safe("错误: 未安装PyInstaller")
            result = messagebox.askyesno(
                "缺少依赖",
                "未安装PyInstaller库，无法打包。\n\n是否现在安装？"
            )
            if result:
                self.install_pyinstaller()
            return

        # 检查是否需要pywin32（如果勾选了创建快捷方式且设置了图标）
        need_pywin32 = self.create_shortcut_var.get() and self.desktop_icon_var.get().strip()

        if need_pywin32:
            try:
                import win32com.client
                self.log_safe("pywin32已安装", "#5A96DB")
            except ImportError:
                self.log_safe("警告: 未安装pywin32库")
                result = messagebox.askyesno(
                    "缺少依赖",
                    "您勾选了创建桌面快捷方式，但未安装pywin32库。\n\n打包后将无法自动创建桌面快捷方式。\n\n是否现在安装pywin32？"
                )
                if result:
                    self.install_pywin32()
                    # 安装后继续打包
                else:
                    # 用户选择不安装，继续打包但提示功能受限
                    self.log_safe("用户选择不安装pywin32，将无法创建桌面快捷方式")

        path = self.path_var.get().strip()
        file_name = self.file_var.get().strip()

        if not path:
            messagebox.showerror("错误", "请选择工作路径")
            return

        if not file_name:
            messagebox.showerror("错误", "请选择要打包的Python文件")
            return

        # 判断文件路径是绝对路径还是相对路径
        if os.path.isabs(file_name):
            # 如果是绝对路径，直接使用
            file_path = file_name
        else:
            # 如果是相对路径（兼容旧配置），与工作路径组合
            file_path = os.path.join(path, file_name)

        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return

        # 提取文件名（不含路径），用于生成exe文件名和版本信息
        base_filename = os.path.basename(file_name)
        
        # 构建PyInstaller命令
        cmd = f'"{python_exe}" -m PyInstaller'

        # 添加 --clean 参数，清理缓存
        cmd += " --clean"

        # 收集 setuptools 和 PyInstaller 的所有依赖（包括 jaraco 模块）
        cmd += ' --collect-all setuptools'
        cmd += ' --collect-all PyInstaller'

        # 指定spec文件输出目录
        cmd += f' --specpath="{path}"'

        if self.onefile_var.get():
            cmd += " --onefile"

        if not self.console_var.get():
            cmd += " --windowed"

        # 处理图标路径
        icon_path = self.icon_var.get().strip()
        if icon_path:
            # 转换为绝对路径
            if not os.path.isabs(icon_path):
                icon_path = os.path.abspath(icon_path)

            # 验证图标文件是否存在
            if os.path.exists(icon_path):
                cmd += f' --icon="{icon_path}"'
                self.log_safe(f"使用图标: {icon_path}", "#5A96DB")
            else:
                self.log_safe(f"警告: 图标文件不存在: {icon_path}，将不使用图标")
                messagebox.showwarning("警告", f"图标文件不存在: {icon_path}\n将不使用图标继续打包")
                icon_path = None

        # 处理版本号
        version = self.version_var.get().strip()
        copyright_info = self.copyright_var.get().strip()
        version_file = None
        if version or copyright_info:
            # 生成版本信息文件
            version_file = self.create_version_file(path, version, base_filename, copyright_info, self.language_var.get(), self.file_description_var.get())
            if version_file:
                cmd += f' --version-file="{version_file}"'
                if version:
                    self.log_safe(f"使用版本号: {version}", "#5A96DB")
                if copyright_info:
                    self.log_safe(f"使用版权信息: {copyright_info}", "#5A96DB")

        # 处理UAC管理员权限
        if self.uac_admin_var.get():
            # 生成manifest文件
            manifest_file = self.create_uac_manifest(path, base_filename)
            if manifest_file:
                cmd += f' --manifest="{manifest_file}"'
                self.log_safe("已启用UAC管理员权限", "#5A96DB")

        # 添加资源文件
        separator = ";" if os.name == "nt" else ":"  # Windows用分号，其他用冒号
        for resource in self.resource_files:
            source = resource['source']
            target = resource['target']
            cmd += f' --add-data "{source}{separator}{target}"'

        # 添加隐藏导入的库
        for library in self.hidden_imports:
            cmd += f' --hidden-import "{library}"'
        
        cmd += f' "{file_path}"'

        self.log_safe(f"开始打包: {file_name}", "#5A96DB")
        self.log_safe(f"工作目录: {path}", "#5A96DB")
        self.log_safe(f"命令: {cmd}", "#5A96DB")
        self.log_safe("打包中，请稍候...")

        # 禁用按钮防止重复点击
        def disable_buttons():
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.configure(state='disabled')
        self.root.after(0, disable_buttons)

        # 初始化进度条
        self.update_progress_safe(0)
        self.update_status_safe("正在打包...")
        
        self.is_busy = True
        self.is_packing = True
        
        # 在后台线程中执行打包
        def _pack():
            try:
                # 切换到目标目录
                original_cwd = os.getcwd()
                os.chdir(path)

                # 执行打包命令（实时输出）
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                # 用于跟踪打包阶段
                stage = 0
                total_stages = 12  # 总共12个主要阶段
                last_stage = 0  # 记录上一个阶段，防止后退
                hook_count = 0  # 统计处理的hook数量
                hidden_import_count = 0  # 统计处理的hidden import数量

                # 实时读取输出
                for line in process.stdout:
                    self.log_safe(line.strip())

                    # 根据输出更新进度
                    line_lower = line.lower()

                    # 按照具体程度从高到低检测
                    if 'info: build complete' in line_lower or 'build complete' in line_lower:
                        stage = 12
                        self.update_status_safe("打包完成！")
                    elif 'info: fixing exe headers' in line_lower or 'fixing exe' in line_lower:
                        if last_stage < 11:
                            stage = 11
                            self.update_status_safe("修复EXE头...")
                    elif 'info: appending pkg archive' in line_lower or 'appending pkg' in line_lower:
                        if last_stage < 10:
                            stage = 10
                            self.update_status_safe("嵌入PKG...")
                    elif 'info: embedding manifest' in line_lower or 'embedding manifest' in line_lower:
                        if last_stage < 9:
                            stage = 9
                            self.update_status_safe("嵌入清单...")
                    elif 'info: copying version information' in line_lower or 'copying version' in line_lower:
                        if last_stage < 8:
                            stage = 8
                            self.update_status_safe("复制版本信息...")
                    elif 'info: copying icon' in line_lower or 'copy icon' in line_lower:
                        if last_stage < 7:
                            stage = 7
                            self.update_status_safe("嵌入图标...")
                    elif 'info: building exe' in line_lower or 'building exe' in line_lower:
                        if last_stage < 6:
                            stage = 6
                            self.update_status_safe("生成 EXE...")
                    elif 'info: building pkg' in line_lower or 'building pkg' in line_lower:
                        if last_stage < 5:
                            stage = 5
                            self.update_status_safe("构建 PKG...")
                    elif 'info: building pyz' in line_lower or 'building pyz' in line_lower:
                        if last_stage < 4:
                            stage = 4
                            self.update_status_safe("构建 PYZ...")
                    elif 'info: creating base_library.zip' in line_lower or 'creating base_library.zip' in line_lower:
                        if last_stage < 3:
                            stage = 3
                            self.update_status_safe("创建基础库...")
                    elif 'info: processing module hooks' in line_lower or 'processing module hooks' in line_lower:
                        if last_stage < 2:
                            stage = 2
                            self.update_status_safe("处理模块钩子...")
                    elif 'info: analyzing' in line_lower:
                        if 'hidden import' in line_lower:
                            hidden_import_count += 1
                            if hidden_import_count % 10 == 0:  # 每10个hidden import更新一次
                                self.update_status_safe(f"分析隐藏导入 ({hidden_import_count})...")
                        elif 'hook' in line_lower:
                            hook_count += 1
                            if hook_count % 5 == 0:  # 每5个hook更新一次
                                self.update_status_safe(f"处理模块钩子 ({hook_count})...")
                        elif last_stage < 1:
                            stage = 1
                            self.update_status_safe("分析Python文件...")
                    elif 'info: pyinstaller' in line_lower or 'info: python' in line_lower or 'info: platform' in line_lower:
                        if last_stage < 1:
                            stage = 1
                            self.update_status_safe("初始化 PyInstaller...")

                    # 更新进度条
                    if stage > last_stage:
                        last_stage = stage
                    progress = (stage / total_stages) * 100
                    self.update_progress_safe(progress)

                # 等待进程完成
                returncode = process.wait()

                # 切换回原目录
                os.chdir(original_cwd)

                if returncode == 0:
                    self.update_progress_safe(100)
                    self.update_status_safe("打包成功！")
                    self.log_safe("打包成功完成！", "#5A96DB")
                    self.log_safe(f"输出目录: {os.path.join(path, 'dist')}", "#5A96DB")

                    # 获取生成的exe文件路径
                    exe_name = os.path.splitext(base_filename)[0] + '.exe'

                    # 根据是否打包为单个exe文件，确定exe文件的实际路径
                    if self.onefile_var.get():
                        # 单文件模式：exe文件直接在dist目录下
                        exe_path = os.path.join(path, "dist", exe_name)
                    else:
                        # 目录模式：exe文件在dist目录下的子文件夹中
                        exe_folder = os.path.splitext(base_filename)[0]
                        exe_path = os.path.join(path, "dist", exe_folder, exe_name)

                    # 验证exe文件是否存在
                    if not os.path.exists(exe_path):
                        self.log_safe(f"警告: 未找到exe文件: {exe_path}", "red")
                        
                        def show_error():
                            messagebox.showerror("错误", f"未找到exe文件: {exe_path}")
                            self.enable_buttons()
                            self.is_packing = False
                            self.is_busy = False
                        self.root.after(0, show_error)
                        return
                    else:
                        self.log_safe(f"找到exe文件: {exe_path}", "#5A96DB")

                        # 如果启用了数字签名，对exe文件进行签名
                        if self.enable_sign_var.get():
                            self.log_safe("准备进行数字签名...", "#5A96DB")
                            sign_success = self.sign_exe(exe_path)
                            if sign_success:
                                self.log_safe("数字签名完成！", "#5A96DB")
                            else:
                                self.log_safe("数字签名失败，但打包已完成", "#FF9500")

                        # 如果勾选了创建快捷方式且设置了图标，创建桌面快捷方式
                        if self.create_shortcut_var.get():
                            desktop_icon = self.desktop_icon_var.get().strip()
                            if desktop_icon:
                                self.create_desktop_shortcut(path, base_filename, desktop_icon)

                    # 询问是否删除临时文件夹（必须在主线程中执行）
                    def ask_cleanup():
                        self.ask_cleanup_temp_files(path, base_filename)
                        # 清理完成后显示成功消息
                        messagebox.showinfo("成功", "打包完成！")
                        self.enable_buttons()
                        self.is_packing = False
                        self.is_busy = False
                    self.root.after(0, ask_cleanup)
                else:
                    self.update_status_safe("打包失败！")
                    self.log_safe(f"打包失败，错误代码: {returncode}", "red")
                    
                    def show_error():
                        messagebox.showerror("错误", "打包失败，请查看日志")
                        self.enable_buttons()
                        self.is_packing = False
                        self.is_busy = False
                    self.root.after(0, show_error)

            except Exception as e:
                self.update_status_safe("打包出错！")
                self.log_safe(f"打包过程中出现错误: {str(e)}", "red")
                
                def show_exception():
                    messagebox.showerror("错误", f"打包失败: {str(e)}")
                    self.enable_buttons()
                    self.is_packing = False
                    self.is_busy = False
                self.root.after(0, show_exception)
        
        # 启动后台线程
        self.current_thread = threading.Thread(target=_pack, daemon=True)
        self.current_thread.start()
    
    def enable_buttons(self):
        """重新启用所有按钮"""
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='normal')
    
    def create_uac_manifest(self, path, file_name):
        """创建UAC管理员权限的manifest文件"""
        try:
            # 生成manifest文件内容
            manifest_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="{os.path.splitext(file_name)[0]}"
    type="win32"
  />
  <description>{os.path.splitext(file_name)[0]}</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>
"""

            # 保存manifest文件
            manifest_file_path = os.path.join(path, 'app.manifest')
            with open(manifest_file_path, 'w', encoding='utf-8') as f:
                f.write(manifest_content)

            self.log(f"已创建UAC manifest文件: {manifest_file_path}", "#5A96DB")
            return manifest_file_path

        except Exception as e:
            self.log(f"创建UAC manifest文件失败: {str(e)}", "red")
            return None

    def install_pyinstaller(self):
        """安装PyInstaller"""
        # 检查是否有任务正在进行
        if self.is_busy:
            messagebox.showwarning("提示", "正在执行其他任务，请稍候...")
            return
        
        # 获取系统Python路径
        python_exe = self.get_system_python()
        if not python_exe:
            messagebox.showerror(
                "错误",
                "无法找到系统Python！\n\n"
                "请确保已安装Python并添加到PATH环境变量中。\n"
                "或者直接使用Python脚本运行此工具。"
            )
            return

        self.is_busy = True
        self.is_installing = True
        self.log_safe("开始安装PyInstaller（使用清华源）...", "#5A96DB")
        self.update_status_safe("正在安装PyInstaller...")
        self.update_progress_safe(10)
        
        # 在后台线程中执行安装
        def _install():
            try:
                # 使用Popen来实时获取输出
                process = subprocess.Popen(
                    f'"{python_exe}" -m pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple',
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # 实时读取输出
                output_lines = []
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        line = line.strip()
                        output_lines.append(line)
                        # 更新进度条（模拟进度）
                        current_progress = self.progress_var.get()
                        if current_progress < 80:
                            self.update_progress_safe(current_progress + 2)
                
                result = process.poll()
                
                if result == 0:
                    self.update_progress_safe(90)
                    self.log_safe("PyInstaller 安装成功！", "#5A96DB")
                    
                    # 检查版本
                    version_result = subprocess.run(f'"{python_exe}" -m PyInstaller --version', shell=True, capture_output=True, text=True)
                    if version_result.returncode == 0:
                        self.log_safe(f"PyInstaller版本: {version_result.stdout.strip()}", "#5A96DB")
                    
                    self.update_progress_safe(100)
                    self.update_status_safe("PyInstaller安装完成")
                    
                    def show_success():
                        messagebox.showinfo("成功", f"PyInstaller 安装成功！\n版本: {version_result.stdout.strip()}")
                        self.is_installing = False
                        self.is_busy = False
                    self.root.after(0, show_success)
                else:
                    self.update_progress_safe(0)
                    self.update_status_safe("安装失败")
                    
                    error_msg = "\n".join(output_lines[-10:]) if output_lines else "未知错误"
                    self.log_safe(f"安装失败: {error_msg}", "red")
                    
                    def show_error():
                        messagebox.showerror("错误", f"PyInstaller 安装失败\n\n{error_msg}")
                        self.is_installing = False
                        self.is_busy = False
                    self.root.after(0, show_error)

            except Exception as e:
                self.update_progress_safe(0)
                self.update_status_safe("安装出错")
                self.log_safe(f"安装过程中出现错误: {str(e)}", "red")
                
                def show_exception():
                    messagebox.showerror("错误", f"安装失败: {str(e)}")
                    self.is_installing = False
                    self.is_busy = False
                self.root.after(0, show_exception)
        
        # 启动后台线程
        self.current_thread = threading.Thread(target=_install, daemon=True)
        self.current_thread.start()

    def create_desktop_shortcut(self, path, file_name, icon_path):
        """创建桌面快捷方式"""
        try:
            import win32com.client
            import os

            # 获取exe文件路径
            exe_name = os.path.splitext(file_name)[0] + '.exe'
            
            # 根据是否打包为单个exe文件，确定exe文件的实际路径
            if self.onefile_var.get():
                # 单文件模式：exe文件直接在dist目录下
                exe_path = os.path.join(path, "dist", exe_name)
            else:
                # 目录模式：exe文件在dist目录下的子文件夹中
                exe_folder = os.path.splitext(file_name)[0]
                exe_path = os.path.join(path, "dist", exe_folder, exe_name)

            if not os.path.exists(exe_path):
                self.log(f"警告: exe文件不存在，无法创建快捷方式: {exe_path}")
                return

            # 获取桌面路径
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop_path, f"{os.path.splitext(file_name)[0]}.lnk")

            # 创建快捷方式
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)

            # 设置快捷方式属性
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)

            # 设置图标
            if os.path.exists(icon_path):
                shortcut.IconLocation = icon_path
                self.log(f"快捷方式图标: {icon_path}", "#5A96DB")
            else:
                # 如果图标文件不存在，使用exe本身的图标
                shortcut.IconLocation = exe_path + ",0"
                self.log(f"使用exe本身的图标", "#5A96DB")

            shortcut.Description = os.path.splitext(file_name)[0]
            shortcut.save()

            self.log(f"已创建桌面快捷方式: {shortcut_path}", "#5A96DB")

        except ImportError:
            self.log("警告: 未安装pywin32库，无法创建桌面快捷方式")
            messagebox.showwarning("警告", "未安装pywin32库，无法创建桌面快捷方式\n\n请点击\"安装pywin32\"按钮安装后重试")
        except Exception as e:
            self.log(f"创建桌面快捷方式失败: {str(e)}", "red")
            messagebox.showwarning("警告", f"创建桌面快捷方式失败: {str(e)}")

    def install_pywin32(self):
        """安装pywin32库"""
        # 检查是否有任务正在进行
        if self.is_busy:
            messagebox.showwarning("提示", "正在执行其他任务，请稍候...")
            return
        
        # 获取系统Python路径
        python_exe = self.get_system_python()
        if not python_exe:
            messagebox.showerror(
                "错误",
                "无法找到系统Python！\n\n"
                "请确保已安装Python并添加到PATH环境变量中。\n"
                "或者直接使用Python脚本运行此工具。"
            )
            return

        self.is_busy = True
        self.is_installing = True
        self.log_safe("开始安装pywin32库...", "#5A96DB")
        self.update_status_safe("正在安装pywin32...")
        self.update_progress_safe(10)
        
        # 在后台线程中执行安装
        def _install():
            try:
                # 使用Popen来实时获取输出
                process = subprocess.Popen(
                    f'"{python_exe}" -m pip install pywin32 -i https://pypi.tuna.tsinghua.edu.cn/simple',
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # 实时读取输出
                output_lines = []
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        line = line.strip()
                        output_lines.append(line)
                        # 更新进度条（模拟进度）
                        current_progress = self.progress_var.get()
                        if current_progress < 80:
                            self.update_progress_safe(current_progress + 2)
                
                result = process.poll()
                
                if result == 0:
                    self.update_progress_safe(90)
                    self.log_safe("pywin32安装成功！", "#5A96DB")
                    
                    # 检查版本
                    try:
                        import pywin32
                        self.log_safe("pywin32库已成功导入", "#5A96DB")
                    except ImportError:
                        self.log_safe("注意: pywin32安装成功，但可能需要运行 post-install 脚本", "orange")
                        self.log_safe(f"如果遇到问题，请尝试运行: {python_exe} Scripts/pywin32_postinstall.py -install", "orange")
                    
                    self.update_progress_safe(100)
                    self.update_status_safe("pywin32安装完成")
                    
                    def show_success():
                        messagebox.showinfo("成功", "pywin32安装成功！")
                        self.is_installing = False
                        self.is_busy = False
                    self.root.after(0, show_success)
                else:
                    self.update_progress_safe(0)
                    self.update_status_safe("安装失败")
                    
                    error_msg = "\n".join(output_lines[-10:]) if output_lines else "未知错误"
                    self.log_safe(f"安装失败: {error_msg}", "red")
                    
                    def show_error():
                        messagebox.showerror("错误", f"pywin32安装失败\n\n{error_msg}")
                        self.is_installing = False
                        self.is_busy = False
                    self.root.after(0, show_error)

            except Exception as e:
                self.update_progress_safe(0)
                self.update_status_safe("安装出错")
                self.log_safe(f"安装过程中出现错误: {str(e)}", "red")
                
                def show_exception():
                    messagebox.showerror("错误", f"安装失败: {str(e)}")
                    self.is_installing = False
                    self.is_busy = False
                self.root.after(0, show_exception)
        
        # 启动后台线程
        self.current_thread = threading.Thread(target=_install, daemon=True)
        self.current_thread.start()

    def ask_cleanup_temp_files(self, path, file_name):
        """询问是否删除临时文件夹（spec、build 等）"""
        try:
            # 检查哪些临时文件夹存在
            temp_folders = []

            # 检查 build 文件夹
            build_folder = os.path.join(path, "build")
            if os.path.exists(build_folder):
                temp_folders.append(('build 文件夹', build_folder))

            # 检查 __pycache__ 文件夹
            pycache_folder = os.path.join(path, "__pycache__")
            if os.path.exists(pycache_folder):
                temp_folders.append(('__pycache__ 文件夹', pycache_folder))

            # 检查 spec 文件
            spec_file = os.path.join(path, f"{os.path.splitext(file_name)[0]}.spec")
            if os.path.exists(spec_file):
                temp_folders.append(('spec 文件', spec_file))

            # 检查版本信息文件
            version_file = os.path.join(path, "version_info.txt")
            if os.path.exists(version_file):
                temp_folders.append(('版本信息文件', version_file))

            # 检查UAC manifest文件
            manifest_file = os.path.join(path, "app.manifest")
            if os.path.exists(manifest_file):
                temp_folders.append(('UAC manifest文件', manifest_file))

            # 检查打包配置文件
            if os.path.exists(self.config_file):
                temp_folders.append(('打包配置文件', self.config_file))

            # 检查自签名证书临时目录
            import tempfile
            temp_base_dir = tempfile.gettempdir()
            if os.path.exists(temp_base_dir):
                for item in os.listdir(temp_base_dir):
                    if item.startswith("self_signed_cert_"):
                        cert_temp_dir = os.path.join(temp_base_dir, item)
                        if os.path.isdir(cert_temp_dir):
                            temp_folders.append(('自签名证书临时目录', cert_temp_dir))

            if not temp_folders:
                self.log("没有找到需要清理的临时文件", "#5A96DB")
                return

            # 创建询问对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("清理临时文件")
            dialog.geometry("550x400")
            dialog.transient(self.root)
            dialog.grab_set()

            # 设置对话框背景色
            dialog.configure(bg="#f5f5f5")

            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")

            # 标题
            title_frame = tk.Frame(dialog, bg="#f5f5f5")
            title_frame.pack(fill="x", padx=20, pady=(15, 12))
            title_label = tk.Label(
                title_frame,
                text="是否删除以下临时文件？",
                font=("Microsoft YaHei UI", 11, "bold"),
                bg="#f5f5f5",
                fg="#2c3e50"
            )
            title_label.pack()

            # 说明
            desc_label = tk.Label(
                title_frame,
                text="这些文件在打包过程中生成，打包完成后通常不再需要",
                font=("Microsoft YaHei UI", 9),
                bg="#f5f5f5",
                fg="#7f8c8d"
            )
            desc_label.pack()

            # 创建滚动区域
            canvas = tk.Canvas(dialog, bg="#f5f5f5", highlightthickness=0)
            scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # 使用鼠标滚轮滚动
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            # 创建复选框列表
            checkboxes = []
            checkbox_vars = {}

            for name, folder_path in temp_folders:
                var = tk.BooleanVar(value=True)
                checkbox_vars[name] = var

                frame = tk.Frame(scrollable_frame, bg="#ffffff", highlightthickness=1, highlightbackground="#e0e0e0")
                frame.pack(fill="x", padx=20, pady=4)

                checkbox = tk.Checkbutton(
                    frame,
                    text=f"  {name}",
                    variable=var,
                    font=("Microsoft YaHei UI", 9),
                    bg="#ffffff",
                    fg="#2c3e50",
                    activebackground="#ffffff",
                    activeforeground="#2c3e50",
                    selectcolor="#f5f5f5",
                    cursor="hand2"
                )
                checkbox.pack(side=tk.LEFT, padx=10, pady=8)

                # 显示路径（截断过长的路径）
                display_path = folder_path
                if len(display_path) > 50:
                    display_path = "..." + display_path[-47:]

                path_label = tk.Label(
                    frame,
                    text=display_path,
                    font=("Microsoft YaHei UI", 8),
                    bg="#ffffff",
                    fg="#95a5a6"
                )
                path_label.pack(side=tk.LEFT, padx=5)

            # 按钮框架
            button_frame = tk.Frame(dialog, bg="#f5f5f5")
            button_frame.pack(pady=(0, 15))

            # 打包canvas和scrollbar
            canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=5)
            scrollbar.pack(side="right", fill="y", pady=5)

            def on_cleanup():
                # 删除选中的文件
                deleted_count = 0
                for name, folder_path in temp_folders:
                    if checkbox_vars[name].get():
                        try:
                            if os.path.isfile(folder_path):
                                os.remove(folder_path)
                                self.log(f"已删除: {name}", "red")
                            elif os.path.isdir(folder_path):
                                import shutil
                                shutil.rmtree(folder_path)
                                self.log(f"已删除: {name}", "red")
                            deleted_count += 1
                        except Exception as e:
                            self.log(f"删除 {name} 失败: {str(e)}", "red")

                if deleted_count > 0:
                    self.log(f"成功删除 {deleted_count} 个临时文件/文件夹", "#5A96DB")
                else:
                    self.log("没有删除任何文件", "#5A96DB")

                # 取消绑定鼠标滚轮事件
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()

            def on_skip():
                self.log("跳过清理临时文件", "#5A96DB")
                # 取消绑定鼠标滚轮事件
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()

            # 清理按钮
            cleanup_button = tk.Button(
                button_frame,
                text="清理选中",
                width=12,
                height=1,
                font=("Microsoft YaHei UI", 10, "bold"),
                bg="#e67e22",
                fg="white",
                activebackground="#d35400",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                command=on_cleanup
            )
            cleanup_button.pack(side=tk.LEFT, padx=5)

            # 跳过按钮
            skip_button = tk.Button(
                button_frame,
                text="跳过",
                width=12,
                height=1,
                font=("Microsoft YaHei UI", 10),
                bg="#95a5a6",
                fg="white",
                activebackground="#7f8c8d",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                command=on_skip
            )
            skip_button.pack(side=tk.LEFT, padx=5)

            # 对话框关闭时的处理
            def on_close():
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()
            dialog.protocol("WM_DELETE_WINDOW", on_close)

        except Exception as e:
            self.log(f"清理临时文件时出错: {str(e)}")

    def clear_config(self):
        """清空配置"""
        # 检查是否有任务正在进行
        if self.is_busy:
            messagebox.showwarning("提示", "正在执行任务，请等待任务完成后再清空配置")
            return
        
        if messagebox.askyesno("确认", "确定要清空所有配置吗？"):
            # 删除配置文件
            if os.path.exists(self.config_file):
                os.remove(self.config_file)

            # 清空所有变量
            self.path_var.set(os.getcwd())
            self.file_var.set("")
            self.icon_var.set("")
            self.desktop_icon_var.set("")
            self.create_shortcut_var.set(False)
            self.uac_admin_var.set(False)
            self.version_var.set("")
            self.copyright_var.set("")
            self.language_var.set("中文（简体）")
            self.enable_sign_var.set(False)
            self.use_self_signed_var.set(True)
            self.cert_file_var.set("")
            self.cert_password_var.set("")
            self.timestamp_server_var.set("http://timestamp.digicert.com")
            self.signtool_path_var.set("")

            # 清空复选框状态
            self.onefile_var.set(True)
            self.console_var.set(True)

            # 清空列表数据
            self.resource_files = []
            self.hidden_imports = []

            # 清空输入框变量
            self.source_var.set("")
            self.target_var.set("")
            self.library_var.set("")

            # 更新界面列表
            self.update_resource_list()
            self.update_library_list()

            # 隐藏签名相关框架
            self.signtool_frame.grid()
            self.enable_signtool_frame(False)
            self.enable_options_frame(False)

            # 检查signtool路径状态
            self.check_signtool_path()

            # 清空日志
            self.log_text.delete(1.0, tk.END)

            # 重置进度条和状态
            self.progress_var.set(0)
            self.status_var.set("就绪")

            # 记录日志
            self.log("配置已清空", "#5A96DB")
            self.log("当前工作路径: " + os.getcwd(), "#5A96DB")
    
    def safe_quit(self):
        """安全退出函数"""
        # 检查是否有任务正在进行
        if self.is_busy:
            result = messagebox.askyesno(
                "警告",
                "正在执行任务，退出可能会导致任务中断。\n\n确定要退出吗？"
            )
            if not result:
                return
        
        # 退出程序
        self.root.quit()
    
    def on_image_drop_to_converter(self, event, listbox, image_paths):
        """处理图片转换窗口的拖放事件"""
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 支持的图片扩展名
        supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        
        # 处理每个拖放的文件
        added_count = 0
        for file_path in files:
            # 去除可能的花括号和引号
            file_path = file_path.strip('{}').strip('"').strip("'")
            
            if not file_path:
                continue
            
            # 检查路径是否存在
            if not os.path.exists(file_path):
                continue
            
            # 检查是否为支持的图片格式
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in supported_extensions:
                continue
            
            # 检查是否已添加
            if file_path not in image_paths:
                image_paths.append(file_path)
                listbox.insert(tk.END, os.path.basename(file_path))
                added_count += 1
        
        if added_count > 0:
            self.log(f"通过拖放成功添加 {added_count} 个图片文件", "#5A96DB")
    
    def open_icon_converter(self):
        """打开图片转换工具窗口（转换为ICO）"""
        try:
            from PIL import Image
        except ImportError:
            result = messagebox.askyesno(
                "缺少依赖",
                "需要安装Pillow库才能使用图片转换功能\n\n是否现在安装？"
            )
            if result:
                # 检查是否有任务正在进行
                if self.is_busy:
                    messagebox.showwarning("提示", "正在执行其他任务，请稍候...")
                    return
                
                # 获取系统Python路径
                python_exe = self.get_system_python()
                if python_exe:
                    self.is_busy = True
                    self.is_installing = True
                    self.log_safe("开始安装Pillow库...", "#5A96DB")
                    self.update_status_safe("正在安装Pillow库...")
                    self.update_progress_safe(10)
                    
                    # 在后台线程中执行安装
                    def _install():
                        try:
                            # 使用Popen来实时获取输出
                            process = subprocess.Popen(
                                f'"{python_exe}" -m pip install pillow -i https://pypi.tuna.tsinghua.edu.cn/simple',
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                bufsize=1,
                                universal_newlines=True
                            )
                            
                            # 实时读取输出
                            output_lines = []
                            while True:
                                line = process.stdout.readline()
                                if not line and process.poll() is not None:
                                    break
                                if line:
                                    line = line.strip()
                                    output_lines.append(line)
                                    # 更新进度条（模拟进度）
                                    current_progress = self.progress_var.get()
                                    if current_progress < 80:
                                        self.update_progress_safe(current_progress + 2)
                            
                            result = process.poll()
                            
                            if result == 0:
                                self.update_progress_safe(90)
                                self.log_safe("Pillow库安装成功！", "#5A96DB")
                                
                                self.update_progress_safe(100)
                                self.update_status_safe("Pillow库安装完成")
                                
                                def show_success():
                                    messagebox.showinfo("成功", "Pillow库安装成功！\n请重新点击图片转换按钮")
                                    self.is_installing = False
                                    self.is_busy = False
                                self.root.after(0, show_success)
                            else:
                                self.update_progress_safe(0)
                                self.update_status_safe("安装失败")
                                
                                error_msg = "\n".join(output_lines[-10:]) if output_lines else "未知错误"
                                self.log_safe(f"Pillow库安装失败: {error_msg}", "red")
                                
                                def show_error():
                                    messagebox.showerror("错误", f"Pillow库安装失败\n\n{error_msg}")
                                    self.is_installing = False
                                    self.is_busy = False
                                self.root.after(0, show_error)

                        except Exception as e:
                            self.update_progress_safe(0)
                            self.update_status_safe("安装出错")
                            self.log_safe(f"安装Pillow库失败: {str(e)}", "red")
                            
                            def show_exception():
                                messagebox.showerror("错误", f"安装失败: {str(e)}")
                                self.is_installing = False
                                self.is_busy = False
                            self.root.after(0, show_exception)
                    
                    # 启动后台线程
                    self.current_thread = threading.Thread(target=_install, daemon=True)
                    self.current_thread.start()
            return

        # 创建图片转换窗口
        convert_window = tk.Toplevel(self.root)
        convert_window.title("图片转换工具")
        convert_window.geometry("600x450")

        # 居中显示
        convert_window.update_idletasks()
        x = (convert_window.winfo_screenwidth() // 2) - (convert_window.winfo_width() // 2)
        y = (convert_window.winfo_screenheight() // 2) - (convert_window.winfo_height() // 2)
        convert_window.geometry(f"+{x}+{y}")

        # 标题
        title_label = ttk.Label(convert_window, text="图片转换工具", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # 说明
        desc_label = ttk.Label(convert_window, text="选择图片文件，将其转换为ICO格式", foreground="gray")
        desc_label.pack(pady=(0, 5))

        # 图片列表框架
        list_frame = ttk.LabelFrame(convert_window, text="已选择的图片", padding="5")
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # 图片列表
        image_listbox = tk.Listbox(list_frame, height=8)
        image_listbox.pack(side=tk.LEFT, fill="both", expand=True)

        # 滚动条
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=image_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill="y")
        image_listbox.configure(yscrollcommand=list_scrollbar.set)

        # 启用拖放功能
        if HAS_DND_SUPPORT:
            image_listbox.drop_target_register(DND_FILES)
            image_listbox.dnd_bind('<<Drop>>', lambda event: self.on_image_drop_to_converter(event, image_listbox, image_paths))

        # 存储图片路径
        image_paths = []

        # 选择图片按钮
        def select_images():
            files = filedialog.askopenfilenames(
                title="选择图片文件",
                filetypes=[
                    ("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                    ("PNG文件", "*.png"),
                    ("JPEG文件", "*.jpg;*.jpeg"),
                    ("BMP文件", "*.bmp"),
                    ("GIF文件", "*.gif"),
                    ("所有文件", "*.*")
                ]
            )
            if files:
                for file in files:
                    if file not in image_paths:
                        image_paths.append(file)
                        image_listbox.insert(tk.END, os.path.basename(file))

        # 删除选中图片
        def remove_image():
            selection = image_listbox.curselection()
            if selection:
                index = selection[0]
                image_listbox.delete(index)
                del image_paths[index]

        # 清空列表
        def clear_list():
            image_paths.clear()
            image_listbox.delete(0, tk.END)

        # 尺寸选择框架
        size_frame = ttk.LabelFrame(convert_window, text="转换尺寸", padding="5")
        size_frame.pack(fill="x", padx=15, pady=5)

        # 尺寸选项
        size_var = tk.StringVar(value="48x48")
        sizes = ["16x16", "32x32", "48x48", "64x64", "128x128", "256x256"]
        
        size_combo = ttk.Combobox(size_frame, textvariable=size_var, values=sizes, state="readonly", width=20)
        size_combo.pack(side=tk.LEFT, padx=5)

        # 操作按钮（放在尺寸选择右边）
        ttk.Button(size_frame, text="选择图片", command=select_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(size_frame, text="删除选中", command=remove_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(size_frame, text="清空", command=clear_list).pack(side=tk.LEFT, padx=5)

        # 转换图片为ICO
        def convert_to_ico():
            if not image_paths:
                messagebox.showwarning("警告", "请先选择图片文件")
                return

            # 获取选择的尺寸
            selected_size = size_var.get()
            target_size = int(selected_size.split('x')[0])

            # 选择保存目录
            save_dir = filedialog.askdirectory(title="选择保存目录")
            if not save_dir:
                return

            success_count = 0
            fail_count = 0

            try:
                for img_path in image_paths:
                    try:
                        # 打开图片
                        img = Image.open(img_path)
                        
                        # 转换为RGBA格式
                        img = img.convert('RGBA')
                        
                        # 缩放到目标尺寸
                        img = img.resize((target_size, target_size), Image.LANCZOS)
                        
                        # 生成保存路径
                        base_name = os.path.splitext(os.path.basename(img_path))[0]
                        save_path = os.path.join(save_dir, base_name + ".ico")
                        
                        # 保存ICO，只包含选中的尺寸
                        img.save(save_path, format='ICO', sizes=[(target_size, target_size)])
                        success_count += 1
                        
                    except Exception as e:
                        self.log(f"转换失败: {os.path.basename(img_path)} - {str(e)}", "red")
                        fail_count += 1

                messagebox.showinfo(
                    "转换完成",
                    f"成功转换: {success_count} 个文件\n失败: {fail_count} 个文件\n尺寸: {selected_size}"
                )
                if success_count > 0:
                    self.log(f"成功转换 {success_count} 个图片为ICO格式 (尺寸: {selected_size})", "#5A96DB")

            except Exception as e:
                messagebox.showerror("错误", f"转换失败:\n{str(e)}")

        # 转换按钮框架（单独一行）
        convert_button_frame = ttk.Frame(convert_window)
        convert_button_frame.pack(fill="x", padx=15, pady=10)

        ttk.Button(convert_button_frame, text="转换为ICO", command=convert_to_ico, width=20).pack()
        
        # 记录日志
        self.log("已打开图片转换工具", "#5A96DB")

    def generate_self_signed_cert(self):
        """生成自签名证书"""
        try:
            import tempfile
            import uuid

            self.log("正在生成自签名证书...", "#5A96DB")

            # 更新进度条
            self.status_var.set("正在生成自签名证书...")
            self.progress_var.set(10)
            self.root.update()

            # 获取配置的证书信息
            cn = self.self_sign_cn.get().strip()
            o = self.self_sign_o.get().strip()
            ou = self.self_sign_ou.get().strip()
            l = self.self_sign_l.get().strip()
            s = self.self_sign_s.get().strip()
            c = self.self_sign_c.get().strip()
            friendly_name = self.self_sign_friendly.get().strip()
            validity_years = self.self_sign_validity.get()

            # 构建 Subject 字符串
            subject_parts = []
            if cn:
                subject_parts.append(f"CN={cn}")
            if o:
                subject_parts.append(f"O={o}")
            if ou:
                subject_parts.append(f"OU={ou}")
            if l:
                subject_parts.append(f"L={l}")
            if s:
                subject_parts.append(f"S={s}")
            if c:
                subject_parts.append(f"C={c}")
            subject = ",".join(subject_parts) if subject_parts else "CN=SelfSignedCert"

            # 创建临时目录存放证书
            temp_dir = tempfile.mkdtemp(prefix="self_signed_cert_")
            cert_name = f"SelfSignedCert_{uuid.uuid4().hex[:8]}"
            cert_password = "123456"  # 自签名证书使用固定密码
            pfx_path = os.path.join(temp_dir, f"{cert_name}.pfx")

            self.log(f"创建临时目录: {temp_dir}")
            self.log(f"证书主题: {subject}")
            self.log(f"有效期: {validity_years} 年")
            self.progress_var.set(30)
            self.root.update()

            # 使用PowerShell生成自签名证书
            ps_script = f'''
$certName = "{cert_name}"
$pfxPath = "{pfx_path}"
$password = ConvertTo-SecureString -String "{cert_password}" -Force -AsPlainText
$friendlyName = "{friendly_name}"
$validityYears = {validity_years}

# 创建自签名证书
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "{subject}" -CertStoreLocation "Cert:\\CurrentUser\\My" -NotAfter (Get-Date).AddYears($validityYears) -FriendlyName $friendlyName

# 导出为PFX文件
$certBytes = $cert.Export("Pfx", $password)
[System.IO.File]::WriteAllBytes($pfxPath, $certBytes)

Write-Output "SUCCESS:$($cert.Thumbprint)"
'''

            self.log("正在执行PowerShell脚本...")
            self.progress_var.set(50)
            self.root.update()

            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True
            )

            self.progress_var.set(80)
            self.root.update()

            if result.returncode == 0 and "SUCCESS:" in result.stdout:
                thumbprint = result.stdout.split("SUCCESS:")[1].strip()
                self.log(f"自签名证书生成成功！", "#5A96DB")
                self.log(f"证书名称: {cert_name}", "#5A96DB")
                self.log(f"证书主题: {subject}", "#5A96DB")
                self.log(f"证书指纹: {thumbprint}", "#5A96DB")
                self.log(f"证书路径: {pfx_path}", "#5A96DB")
                self.log(f"证书密码: {cert_password}", "#5A96DB")
                self.progress_var.set(100)
                self.root.update()
                return pfx_path, cert_password
            else:
                self.log(f"生成自签名证书失败: {result.stderr}", "red")
                self.progress_var.set(0)
                self.root.update()
                return None, None

        except Exception as e:
            self.log(f"生成自签名证书时出错: {str(e)}")
            self.progress_var.set(0)
            self.root.update()
            return None, None

    def sign_exe(self, exe_path):
        """对EXE文件进行数字签名"""
        try:
            cert_file = self.cert_file_var.get().strip()
            cert_password = self.cert_password_var.get()
            timestamp_server = self.timestamp_server_var.get().strip()

            # 检查是否使用自签名证书
            if self.use_self_signed_var.get():
                self.log("使用自签名证书...", "#5A96DB")
                cert_file, cert_password = self.generate_self_signed_cert()
                if not cert_file:
                    messagebox.showerror("签名错误", "生成自签名证书失败")
                    return False
            else:
                # 使用自定义证书
                if not cert_file:
                    self.log("错误: 未指定证书文件")
                    messagebox.showerror("签名错误", "未指定证书文件")
                    return False

                if not os.path.exists(cert_file):
                    self.log(f"错误: 证书文件不存在: {cert_file}")
                    messagebox.showerror("签名错误", f"证书文件不存在: {cert_file}")
                    return False

            if not os.path.exists(exe_path):
                self.log(f"错误: EXE文件不存在: {exe_path}")
                messagebox.showerror("签名错误", f"EXE文件不存在: {exe_path}")
                return False

            self.log("开始数字签名...", "#5A96DB")
            self.log(f"EXE文件: {exe_path}", "#5A96DB")
            self.log(f"证书文件: {cert_file}", "#5A96DB")
            self.log(f"时间戳服务器: {timestamp_server}", "#5A96DB")

            # 查找signtool.exe
            signtool_exe = None

            # 优先使用用户指定的路径
            user_path = self.signtool_path_var.get().strip()
            if user_path and os.path.exists(user_path):
                signtool_exe = user_path

            # 如果用户未指定或路径不存在，尝试自动查找
            if not signtool_exe:
                signtool_paths = [
                    os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Windows Kits", "10", "bin", "x64", "signtool.exe"),
                    os.path.join(os.environ.get("ProgramFiles", ""), "Windows Kits", "10", "bin", "x64", "signtool.exe"),
                    os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Windows Kits", "8.1", "bin", "x64", "signtool.exe"),
                    os.path.join(os.environ.get("ProgramFiles", ""), "Windows Kits", "8.1", "bin", "x64", "signtool.exe"),
                ]

                for path in signtool_paths:
                    if os.path.exists(path):
                        signtool_exe = path
                        break

                if not signtool_exe:
                    # 尝试使用where命令查找
                    try:
                        result = subprocess.run("where signtool.exe", shell=True, capture_output=True, text=True)
                        if result.returncode == 0 and result.stdout.strip():
                            signtool_exe = result.stdout.strip().split('\n')[0]
                    except:
                        pass

            if not signtool_exe:
                self.log("错误: 未找到signtool.exe")
                self.log("请确保已安装Windows SDK并添加到PATH环境变量")
                messagebox.showerror(
                    "签名错误",
                    "未找到signtool.exe\n\n"
                    "请安装Windows SDK（包含Windows SDK签名工具）\n"
                    "下载地址: https://developer.microsoft.com/zh-cn/windows/downloads/windows-sdk/"
                )
                return False

            self.log(f"使用signtool: {signtool_exe}", "#5A96DB")

            # 构建签名命令
            cmd = [
                signtool_exe,
                "sign",
                "/f", cert_file,
                "/p", cert_password,
                "/tr", timestamp_server,
                "/td", "sha256",
                "/fd", "sha256",
                exe_path
            ]

            self.log("正在签名，请稍候...")

            # 执行签名命令
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.log("数字签名成功！")
                self.log(f"签名输出: {result.stdout}")
                return True
            else:
                self.log(f"数字签名失败！", "red")
                self.log(f"错误代码: {result.returncode}")
                self.log(f"错误信息: {result.stderr}")
                messagebox.showerror(
                    "签名失败",
                    f"数字签名失败\n\n错误代码: {result.returncode}\n错误信息:\n{result.stderr}"
                )
                return False

        except Exception as e:
            self.log(f"签名过程中出现错误: {str(e)}")
            messagebox.showerror("签名错误", f"数字签名失败: {str(e)}")
            return False

    def cleanup_self_signed_cert_temp(self):
        """清理自签名证书临时文件"""
        try:
            import tempfile
            import shutil

            temp_base_dir = tempfile.gettempdir()
            deleted_count = 0

            if os.path.exists(temp_base_dir):
                for item in os.listdir(temp_base_dir):
                    if item.startswith("self_signed_cert_"):
                        cert_temp_dir = os.path.join(temp_base_dir, item)
                        if os.path.isdir(cert_temp_dir):
                            try:
                                shutil.rmtree(cert_temp_dir)
                                self.log(f"已删除自签名证书临时目录: {cert_temp_dir}", "#5A96DB")
                                deleted_count += 1
                            except Exception as e:
                                self.log(f"删除 {cert_temp_dir} 失败: {str(e)}", "red")

            if deleted_count > 0:
                self.log(f"成功清理 {deleted_count} 个自签名证书临时目录", "#5A96DB")
            else:
                self.log("没有找到需要清理的自签名证书临时文件", "#5A96DB")

        except Exception as e:
            self.log(f"清理自签名证书临时文件时出错: {str(e)}", "red")

    def log(self, message, color=None):
        """添加日志到文本框"""
        if color:
            self.log_text.insert(tk.END, f"{message}\n", (color,))
            # 配置颜色标签
            self.log_text.tag_config(color, foreground=color)
        else:
            self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_progress_safe(self, value):
        """线程安全地更新进度条"""
        self.root.after(0, lambda: self.progress_var.set(value))
    
    def update_status_safe(self, text):
        """线程安全地更新状态标签"""
        self.root.after(0, lambda: self.status_var.set(text))
    
    def log_safe(self, message, color=None):
        """线程安全地添加日志"""
        def _log():
            if color:
                self.log_text.insert(tk.END, f"{message}\n", (color,))
                self.log_text.tag_config(color, foreground=color)
            else:
                self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        self.root.after(0, _log)

def main():
    # 检查是否安装了tkinter
    try:
        # 如果支持DND，使用TkinterDnD.Tk
        if HAS_DND_SUPPORT:
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()
        
        # 设置主题样式（如果可用）
        try:
            style = ttk.Style()
            # 尝试使用Windows默认主题，这样复选框会显示勾号
            available_themes = style.theme_names()
            if sys.platform == 'win32':
                # Windows系统优先使用原生主题
                if 'vista' in available_themes:
                    style.theme_use('vista')
                elif 'xpnative' in available_themes:
                    style.theme_use('xpnative')
                elif 'winnative' in available_themes:
                    style.theme_use('winnative')
                else:
                    style.theme_use('clam')
            else:
                style.theme_use('clam')
        except:
            pass
        
        app = PyInstallerGUI(root)
        root.mainloop()
    except ImportError:
        print("错误：需要安装tkinter才能使用图形界面")
        print("在Windows上，tkinter通常是Python自带的")
        print("在Linux上，可以安装：sudo apt-get install python3-tk")

if __name__ == "__main__":
    main()