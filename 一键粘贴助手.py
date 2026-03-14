import tkinter as tk
from tkinter import messagebox, font, filedialog
from tkinter import ttk
import pyperclip
import time
import threading
import keyboard
import pyautogui

# 颜色配置
颜色配置 = {
    '主色': '#4A90E2',        # 蓝色
    '次要色': '#50E3C2',      # 青绿色
    '警告色': '#FF6B6B',      # 红色
    '成功色': '#4ECDC4',      # 青色
    '紫色': '#9B59B6',        # 紫色
    '背景色': '#F5F6FA',      # 浅灰背景
    '卡片色': '#FFFFFF',      # 白色卡片
    '文字色': '#2C3E50',      # 深灰文字
    '次要文字': '#95A5A6',    # 浅灰文字
    '边框色': '#E1E8ED',      # 浅灰边框
}

root = tk.Tk()
root.title("一键粘贴助手")
root.geometry("650x630")
root.configure(bg=颜色配置['背景色'])
root.resizable(False, False)

# 自定义字体
标题字体 = font.Font(family="微软雅黑", size=16, weight="bold")
标签字体 = font.Font(family="微软雅黑", size=10)
按钮字体 = font.Font(family="微软雅黑", size=10)

# ========== 全局变量 ==========
# 自动粘贴相关变量
是否正在粘贴 = False
当前索引 = 0
粘贴事件 = threading.Event()
是否被停止 = False  # 标志位，表示是否被用户停止
当前粘贴线程 = None  # 当前粘贴线程的引用
自动执行模式已触发 = False  # 标志位，表示是否已经触发过自动执行模式

# 快捷键配置
停止快捷键 = "ctrl+shift+x"
停止快捷键显示 = "Ctrl+Shift+X"  # 用于显示
开始快捷键 = "ctrl+shift+s"
开始快捷键显示 = "Ctrl+Shift+S"  # 用于显示

# 任务列表
任务列表 = []  # 默认为空，只包含额外操作（如回车、粘贴）

# 发送消息快捷键配置（微信默认使用 Ctrl+Enter 发送消息）
发送消息快捷键 = "ctrl+enter"

# 停止粘贴函数（在绑定快捷键时使用）
def 按快捷键停止(event=None):
    停止粘贴()

# 开始粘贴函数（在绑定快捷键时使用）
def 按快捷键开始(event=None):
    开始粘贴()

# 注册快捷键
def 更新停止快捷键(新快捷键):
    global 停止快捷键, 停止快捷键显示
    
    # 移除旧的快捷键绑定
    try:
        旧tk格式 = 转换为Tk格式(停止快捷键)
        root.unbind(旧tk格式)
    except:
        pass
    
    # 更新变量
    停止快捷键 = 新快捷键
    停止快捷键显示 = 格式化显示快捷键(新快捷键)
    
    # 绑定新的快捷键
    新tk格式 = 转换为Tk格式(新快捷键)
    root.bind(新tk格式, 按快捷键停止)

def 更新开始快捷键(新快捷键):

    global 开始快捷键, 开始快捷键显示

    

    # 移除旧的快捷键绑定

    try:

        旧tk格式 = 转换为Tk格式(开始快捷键)

        root.unbind(旧tk格式)

    except:

        pass

    

    # 更新变量

    开始快捷键 = 新快捷键

    开始快捷键显示 = 格式化显示快捷键(新快捷键)

    

    # 绑定新的快捷键

    新tk格式 = 转换为Tk格式(新快捷键)

    root.bind(新tk格式, 按快捷键开始)



def 转换为Tk格式(快捷键):
    """将快捷键转换为Tkinter格式，例如 ctrl+shift+x -> <Control-Shift-X>"""
    部分 = 快捷键.lower().split('+')
    结果 = []
    for 部分 in 部分:
        if 部分 == 'ctrl':
            结果.append('Control')
        elif 部分 == 'shift':
            结果.append('Shift')
        elif 部分 == 'alt':
            结果.append('Alt')
        else:
            # 键名大写
            结果.append(部分.upper())
    return '<' + '-'.join(结果) + '>'

def 格式化显示快捷键(快捷键):
    """将快捷键格式化为显示格式，例如 ctrl+shift+x -> Ctrl+Shift+X"""
    部分 = 快捷键.lower().split('+')
    结果 = []
    for 部分 in 部分:
        if 部分 == 'ctrl':
            结果.append('Ctrl')
        elif 部分 == 'shift':
            结果.append('Shift')
        elif 部分 == 'alt':
            结果.append('Alt')
        else:
            结果.append(部分.upper())
    return '+'.join(结果)

# 创建样式化按钮函数
def 创建按钮(父容器, 文本, 颜色, 命令, 宽度=None):
    if 颜色 == '主色':
        bg色 = 颜色配置['主色']
        fg色 = 'white'
    elif 颜色 == '成功':
        bg色 = 颜色配置['成功色']
        fg色 = 'white'
    elif 颜色 == '警告':
        bg色 = 颜色配置['警告色']
        fg色 = 'white'
    elif 颜色 == '次要':
        bg色 = 颜色配置['次要色']
        fg色 = 'white'
    elif 颜色 == '紫色':
        bg色 = 颜色配置['紫色']
        fg色 = 'white'
    else:
        bg色 = '#E0E0E0'
        fg色 = 颜色配置['文字色']
    
    按钮 = tk.Button(父容器, text=文本, font=按钮字体, bg=bg色, fg=fg色,
                     activebackground=bg色, activeforeground=fg色,
                     relief=tk.FLAT, cursor='hand2', command=命令, padx=20, pady=8)
    if 宽度:
        按钮.config(width=宽度)
    return 按钮

# 顶部标题区域
标题卡片 = tk.Frame(root, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                    highlightthickness=1)
标题卡片.pack(fill=tk.X, padx=20, pady=15)
标题内部容器 = tk.Frame(标题卡片, bg=颜色配置['卡片色'])
标题内部容器.pack(fill=tk.BOTH, padx=15, pady=15)
标题 = tk.Label(标题内部容器, text="📋 一键粘贴助手", font=标题字体, 
                bg=颜色配置['卡片色'], fg=颜色配置['文字色'])
标题.pack()

快捷键提示 = tk.Label(标题内部容器, text=f"按 {开始快捷键显示} 开始 | 按 {停止快捷键显示} 停止", font=("微软雅黑", 8),
                      bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
快捷键提示.pack(pady=(5, 0))

# 创建Notebook（标签页）
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# ========== 第一页：输入内容 ==========
第一页 = tk.Frame(notebook, bg=颜色配置['背景色'])
notebook.add(第一页, text="📝 输入内容")

# 文本输入区域
文本卡片 = tk.Frame(第一页, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                    highlightthickness=1)
文本卡片.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)
文本内部容器 = tk.Frame(文本卡片, bg=颜色配置['卡片色'])
文本内部容器.pack(fill=tk.BOTH, padx=15, pady=15)

文本标签 = tk.Label(文本内部容器, text="输入内容:", font=标签字体, 
                    bg=颜色配置['卡片色'], fg=颜色配置['次要文字'], anchor=tk.W)
文本标签.pack(fill=tk.X, pady=(0, 8))

文本框 = tk.Text(文本内部容器, height=12, font=("微软雅黑", 10), 
                 bg=颜色配置['背景色'], fg=颜色配置['文字色'],
                 insertbackground=颜色配置['主色'], relief=tk.FLAT,
                 highlightbackground=颜色配置['边框色'], highlightthickness=1,
                 padx=10, pady=8)
文本框.pack(fill=tk.BOTH, expand=True)

# ========== 第二页：内容列表 ==========
第二页 = tk.Frame(notebook, bg=颜色配置['背景色'])
notebook.add(第二页, text="📋 内容列表")

# 列表区域
列表卡片 = tk.Frame(第二页, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                    highlightthickness=1)
列表卡片.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
列表内部容器 = tk.Frame(列表卡片, bg=颜色配置['卡片色'])
列表内部容器.pack(fill=tk.BOTH, padx=15, pady=10)

列表标题 = tk.Label(列表内部容器, text="待粘贴内容列表:", font=标签字体, 
                    bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
列表标题.pack(anchor=tk.W, pady=(0, 5))

列表容器 = tk.Frame(列表内部容器, bg=颜色配置['卡片色'])
列表容器.pack(fill=tk.BOTH, expand=True)

列表滚动条 = tk.Scrollbar(列表容器, bg=颜色配置['卡片色'], 
                           highlightthickness=0, troughcolor=颜色配置['背景色'])
列表滚动条.pack(side=tk.RIGHT, fill=tk.Y)

# 使用Treeview替代Listbox，支持不同颜色
内容列表 = ttk.Treeview(列表容器, columns=('content',), show='headings', 
                       selectmode='browse')
内容列表.heading('content', text='')
内容列表.column('content', width=600)
内容列表.pack(fill=tk.BOTH, expand=True)
列表滚动条.config(command=内容列表.yview)
内容列表.configure(yscrollcommand=列表滚动条.set)

# 配置Treeview样式
样式 = ttk.Style()
样式.configure("Treeview", 
               font=("微软雅黑", 10),
               background=颜色配置['背景色'],
               foreground=颜色配置['文字色'],
               rowheight=20)
样式.configure("Treeview.Heading", font=("微软雅黑", 10))
样式.map("Treeview", 
         background=[('selected', 颜色配置['主色'])],
         foreground=[('selected', 'white')])

# Tkinter的Treeview不支持列级别的颜色控制
# 所以我们使用tag来控制整行的颜色
# 有提示信息的行显示为浅蓝色
内容列表.tag_configure('有提示', foreground='#4A90E2')  # 浅蓝色
内容列表.tag_configure('无提示', foreground=颜色配置['文字色'])  # 黑色
# 自动执行的行显示为橙色
内容列表.tag_configure('自动执行', foreground='#FF9800')  # 橙色

# 状态标签
状态标签 = tk.Label(列表内部容器, text="待粘贴: 0 条", font=("微软雅黑", 9),
                     bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
状态标签.pack(anchor=tk.E, pady=(5, 0))

def 更新状态标签():
    计数 = 内容列表.get_children().__len__()
    状态标签.config(text=f"待粘贴: {计数} 条")

def 清空文本():
    文本框.delete("1.0", tk.END)

def 增加内容():
    内容 = 文本框.get("1.0", tk.END).strip()
    if 内容:
        # 解析内容和提示信息
        内容部分, 提示部分, 自动执行标记 = 解析内容提示(内容)
        
        # 构建显示文本（不显示分隔符和⏩符号）
        if 提示部分:
            显示文本 = f"{内容部分} ({提示部分})"
        else:
            显示文本 = 内容部分
        
        # 根据是否有自动执行标记设置标签颜色
        if 自动执行标记:
            新项ID = 内容列表.insert('', tk.END, values=(显示文本,), tags=('自动执行',))
        elif 提示部分:
            新项ID = 内容列表.insert('', tk.END, values=(显示文本,), tags=('有提示',))
        else:
            新项ID = 内容列表.insert('', tk.END, values=(显示文本,), tags=('无提示',))
        
        # 保存原始内容（包含分隔符）
        if not hasattr(内容列表, '_original_data'):
            内容列表._original_data = {}
        内容列表._original_data[新项ID] = 内容
        
        文本框.delete("1.0", tk.END)
        更新状态标签()
    else:
        messagebox.showwarning("提示", "请输入内容！")

# 解析内容和提示信息
def 解析内容提示(完整内容):
    自动执行标记 = False
    提示 = ''
    
    if '|' in 完整内容:
        部分 = 完整内容.rsplit('|', 1)  # 从右边分割最后一个 |
        内容 = 部分[0].strip()
        
        if len(部分) > 1:
            提示部分 = 部分[1].strip()
            # 检查是否有⏩符号（自动执行标记）
            if 提示部分.endswith('⏩'):
                自动执行标记 = True
                提示 = 提示部分[:-1].strip()  # 移除⏩符号
            else:
                提示 = 提示部分
        
        return 内容, 提示, 自动执行标记
    else:
        return 完整内容.strip(), '', False

# 显示右下角提示信息
def 显示提示信息(提示文本):
    if not 提示文本:
        return
    
    def 关闭提示():
        try:
            提示窗口.destroy()
        except:
            pass
    
    提示窗口 = tk.Toplevel(root)
    提示窗口.overrideredirect(True)
    提示窗口.attributes('-topmost', True)
    提示窗口.configure(bg=颜色配置['主色'])
    
    屏幕宽度 = 提示窗口.winfo_screenwidth()
    屏幕高度 = 提示窗口.winfo_screenheight()
    
    提示标签 = tk.Label(提示窗口, text=提示文本, font=("微软雅黑", 10),
                        bg=颜色配置['主色'], fg='white', padx=15, pady=10)
    提示标签.pack()
    
    提示窗口.update_idletasks()
    窗口宽度 = 提示窗口.winfo_width()
    窗口高度 = 提示窗口.winfo_height()
    x = 屏幕宽度 - 窗口宽度 - 20
    y = 屏幕高度 - 窗口高度 - 20
    提示窗口.geometry(f"+{x}+{y}")
    
    # 根据提示文本长度动态计算显示时长
    # 最短显示2000ms，长度超过5个字时每增加1个字增加300ms
    字数 = len(提示文本)
    if 字数 <= 5:
        显示时长 = 2000
    else:
        显示时长 = 2000 + (字数 - 5) * 300
    
    提示窗口.after(显示时长, 关闭提示)

def 清空列表():
    # 删除Treeview中的所有项
    for item in 内容列表.get_children():
        内容列表.delete(item)
    更新状态标签()

def 复制选中内容():
    """复制内容列表中选中的内容"""
    选中项 = 内容列表.selection()
    if 选中项:
        # 获取原始内容
        if hasattr(内容列表, '_original_data') and 选中项[0] in 内容列表._original_data:
            完整内容 = 内容列表._original_data[选中项[0]]
        else:
            显示文本 = 内容列表.item(选中项[0], 'values')[0]
            完整内容 = 显示文本.replace(' (', ' | ').replace(')', '') if ' (' in 显示文本 else 显示文本
        
        # 解析出纯内容（去掉提示信息）
        内容, 提示, 自动执行标记 = 解析内容提示(完整内容)
        
        # 复制到剪贴板
        pyperclip.copy(内容)
        messagebox.showinfo("成功", "已复制到剪贴板！")
    else:
        messagebox.showwarning("提示", "请先选择要复制的内容！")

# 第一页的按钮（分成两行显示）
第一页按钮容器 = tk.Frame(第一页, bg=颜色配置['背景色'])
第一页按钮容器.pack(fill=tk.X, padx=20, pady=(0, 15))

# 第一行按钮（添加到列表、添加提示、自动执行）
第一页第一行按钮容器 = tk.Frame(第一页按钮容器, bg=颜色配置['背景色'])
第一页第一行按钮容器.pack(fill=tk.X, pady=(0, 5))

添加按钮 = 创建按钮(第一页第一行按钮容器, "➕ 添加到列表", '主色', 增加内容, 宽度=15)
添加按钮.config(padx=8)
添加按钮.pack(side=tk.LEFT, padx=3, expand=True)

# 添加提示信息按钮
def 添加分隔符():
    """在文本框中添加分隔符"""
    当前位置 = 文本框.index(tk.INSERT)
    文本框.insert(当前位置, " | ")
    文本框.focus_set()

def 添加自动执行标记():
    """在文本框末尾添加自动执行标记"""
    当前文本 = 文本框.get("1.0", tk.END).strip()
    if 当前文本:
        # 检查是否已经有|符号，如果没有则先添加
        if '|' not in 当前文本:
            文本框.insert(tk.END, " | ")
        # 添加自动执行标记
        文本框.insert(tk.END, "⏩")
        文本框.focus_set()
    else:
        messagebox.showwarning("提示", "请先输入内容！")

添加提示按钮 = 创建按钮(第一页第一行按钮容器, "💡 添加提示", '次要', 添加分隔符, 宽度=15)
添加提示按钮.config(padx=8)
添加提示按钮.pack(side=tk.LEFT, padx=3, expand=True)

添加自动执行按钮 = 创建按钮(第一页第一行按钮容器, "⚡ 自动执行", '紫色', 添加自动执行标记, 宽度=15)
添加自动执行按钮.config(padx=8)
添加自动执行按钮.pack(side=tk.LEFT, padx=3, expand=True)

# 第二行按钮（清空输入框拉长）
第一页第二行按钮容器 = tk.Frame(第一页按钮容器, bg=颜色配置['背景色'])
第一页第二行按钮容器.pack(fill=tk.X)

清空文本按钮 = 创建按钮(第一页第二行按钮容器, "🗑️ 清空输入框", '警告', 清空文本, 宽度=20)
清空文本按钮.pack(fill=tk.X)

# 第二页的按钮区域
第二页按钮容器 = tk.Frame(第二页, bg=颜色配置['背景色'])
第二页按钮容器.pack(fill=tk.X, padx=20, pady=(0, 10))

# 导入和导出功能
def 导入配置():
    try:
        文件路径 = filedialog.askopenfilename(
            title="导入配置",
            filetypes=[("粘贴配置文件", "*.paste"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if 文件路径:
            with open(文件路径, 'r', encoding='utf-8') as f:
                内容 = f.read().strip()
                if 内容:
                    清空列表()
                    行列表 = [line for line in 内容.split('\n') if line.strip()]
                    for 行 in 行列表:
                        # 解析内容和提示信息
                        内容部分, 提示部分, 自动执行标记 = 解析内容提示(行.strip())
                        
                        # 构建显示文本（不显示分隔符和⏩符号）
                        if 提示部分:
                            显示文本 = f"{内容部分} ({提示部分})"
                        else:
                            显示文本 = 内容部分
                        
                        # 根据是否有自动执行标记设置标签颜色
                        if 自动执行标记:
                            新项ID = 内容列表.insert('', tk.END, values=(显示文本,), tags=('自动执行',))
                        elif 提示部分:
                            新项ID = 内容列表.insert('', tk.END, values=(显示文本,), tags=('有提示',))
                        else:
                            新项ID = 内容列表.insert('', tk.END, values=(显示文本,), tags=('无提示',))
                        
                        # 保存原始内容（包含分隔符）
                        if not hasattr(内容列表, '_original_data'):
                            内容列表._original_data = {}
                        内容列表._original_data[新项ID] = 行.strip()
                    
                    更新状态标签()
                    messagebox.showinfo("成功", f"已导入 {len(行列表)} 条内容！")
                else:
                    messagebox.showwarning("提示", "文件为空！")
    except Exception as e:
        messagebox.showerror("错误", f"导入失败: {str(e)}")

def 导出配置():
    if len(内容列表.get_children()) == 0:
        messagebox.showwarning("提示", "列表中没有内容！")
        return
    
    try:
        文件路径 = filedialog.asksaveasfilename(
            title="导出配置",
            initialfile="粘贴配置",
            defaultextension=".paste",
            filetypes=[("粘贴配置文件", "*.paste"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if 文件路径:
            with open(文件路径, 'w', encoding='utf-8') as f:
                for item in 内容列表.get_children():
                    # 获取原始内容（包含分隔符）
                    if hasattr(内容列表, '_original_data') and item in 内容列表._original_data:
                        原始内容 = 内容列表._original_data[item]
                    else:
                        # 如果没有原始数据，使用显示文本
                        显示文本 = 内容列表.item(item, 'values')[0]
                        原始内容 = 显示文本.replace(' (', ' | ').replace(')', '') if ' (' in 显示文本 else 显示文本
                    f.write(原始内容 + '\n')
            messagebox.showinfo("成功", f"已导出 {len(内容列表.get_children())} 条内容到 {文件路径}！")
    except Exception as e:
        messagebox.showerror("错误", f"导出失败: {str(e)}")

def 检测到粘贴():
    """检测到粘贴操作"""
    粘贴事件.set()

def 开始粘贴(起始索引=0):
    global 是否正在粘贴, 当前索引, 是否被停止, 当前粘贴线程, 自动执行模式已触发
    
    if len(内容列表.get_children()) == 0:
        messagebox.showwarning("提示", "列表中没有内容！")
        return
    
    # 检查是否正在运行
    if 是否正在粘贴:
        messagebox.showinfo("提示", "正在粘贴中...")
        return
    
    # 确保之前的热键已清除（防止之前停止时热键没有移除）
    try:
        keyboard.remove_hotkey('ctrl+v')
    except:
        pass
    
    # 设置状态
    是否正在粘贴 = True
    当前索引 = 起始索引
    是否被停止 = False
    自动执行模式已触发 = False  # 重置自动执行模式
    
    # 清除所有粘贴事件
    粘贴事件.clear()
    
    root.iconify()
    
    # 启动粘贴线程
    当前粘贴线程 = threading.Thread(target=执行粘贴, daemon=True)
    当前粘贴线程.start()

def 从头开始粘贴():
    """从头开始粘贴"""
    开始粘贴(起始索引=0)

def 从选中开始粘贴():
    """从选中项开始粘贴"""
    选中项 = 内容列表.selection()
    if 选中项:
        子项列表 = list(内容列表.get_children())
        起始索引 = 子项列表.index(选中项[0])
        开始粘贴(起始索引=起始索引)
    else:
        messagebox.showwarning("提示", "请先选择要开始的位置！")

def 执行任务列表操作(是否橙色=False):
    """执行任务列表中的额外操作"""
    for 任务 in 任务列表:
        # 检查是否为字典格式（新格式，带条件）
        if isinstance(任务, dict):
            任务名称 = 任务["任务"]
            条件 = 任务["条件"]
            # 如果有条件且不是橙色条目，跳过该任务
            if 条件 and not 是否橙色:
                continue
        else:
            任务名称 = 任务
        
        if 任务名称 == "回车":
            # 使用 pyautogui 模拟 Enter 键发送消息
            time.sleep(0.3)  # 增加前置延时，确保粘贴操作完成
            pyautogui.press('enter')
            time.sleep(0.5)  # 增加后置延时，确保微信能正确发送
        elif 任务名称 == "粘贴":
            # 使用keyboard.send()模拟粘贴，更可靠
            keyboard.send('ctrl+v')
            time.sleep(0.3)
        elif 任务名称.startswith("按键:"):
            # 执行自定义按键
            自定义按键 = 任务名称[3:]  # 去掉"按键:"前缀
            keyboard.send(自定义按键)
            time.sleep(0.3)
        elif 任务名称.startswith("延迟:"):
            # 执行自定义延迟
            延迟时间 = float(任务名称[3:])  # 去掉"延迟:"前缀
            time.sleep(延迟时间)
        else:
            time.sleep(0.1)

def 执行粘贴():
    global 是否正在粘贴, 当前索引, 是否被停止, 自动执行模式已触发
    
    正常完成 = True
    子项列表 = list(内容列表.get_children())
    
    while 是否正在粘贴 and not 是否被停止 and 当前索引 < len(子项列表):
        # 获取当前项的ID
        当前项ID = 子项列表[当前索引]
        
        # 获取原始内容（从_original_data中获取）
        if hasattr(内容列表, '_original_data') and 当前项ID in 内容列表._original_data:
            完整内容 = 内容列表._original_data[当前项ID]
        else:
            # 如果没有原始数据，使用显示文本
            完整内容 = 内容列表.item(当前项ID, 'values')[0]
        
        # 解析内容和提示信息
        内容, 提示, 自动执行标记 = 解析内容提示(完整内容)
        
        pyperclip.copy(内容)
        
        # 根据是否有自动执行标记和是否已触发模式来决定执行方式
        if 自动执行标记:
            if 自动执行模式已触发:
                # 已经触发过自动执行模式，直接自动粘贴
                keyboard.send('ctrl+v')
                time.sleep(0.3)
                # 先显示提示信息
                if 提示:
                    root.after(0, lambda t=提示: 显示提示信息(t))
                # 再执行任务列表中的额外操作（橙色条目）
                执行任务列表操作(是否橙色=True)
                # 增加索引，继续下一次循环
                当前索引 += 1
                continue
            else:
                # 第一次遇到橙色条目，需要手动粘贴
                # 清除粘贴事件
                粘贴事件.clear()
                
                # 添加热键
                try:
                    keyboard.add_hotkey('ctrl+v', 检测到粘贴)
                except:
                    pass
                
                print("等待粘贴...")
                粘贴事件.wait(timeout=120)
                
                # 立即移除热键
                try:
                    keyboard.remove_hotkey('ctrl+v')
                except:
                    pass
                
                # 每次等待后都要检查状态
                if not 是否正在粘贴 or 是否被停止:
                    正常完成 = False
                    break
                
                # 增加延时，确保微信处理完粘贴操作
                time.sleep(0.5)
                
                # 先显示提示信息
                if 提示:
                    root.after(0, lambda t=提示: 显示提示信息(t))
                # 再执行任务列表中的额外操作（橙色条目）
                执行任务列表操作(是否橙色=True)
                
                # 设置自动执行模式已触发
                自动执行模式已触发 = True
                
                # 增加索引
                当前索引 += 1
                continue
        
        # 没有自动执行标记，重置自动执行模式，需要等待用户按Ctrl+V
        自动执行模式已触发 = False
        
        # 清除粘贴事件
        粘贴事件.clear()
        
        # 添加热键
        try:
            keyboard.add_hotkey('ctrl+v', 检测到粘贴)
        except:
            pass
        
        print("等待粘贴...")
        粘贴事件.wait(timeout=120)
        
        # 立即移除热键
        try:
            keyboard.remove_hotkey('ctrl+v')
        except:
            pass
        
        # 每次等待后都要检查状态
        if not 是否正在粘贴 or 是否被停止:
            正常完成 = False
            break
        
        # 先显示提示信息
        if 提示:
            root.after(0, lambda t=提示: 显示提示信息(t))
        # 再执行任务列表中的额外操作（普通条目）
        执行任务列表操作(是否橙色=False)
        
        # 增加索引
        当前索引 += 1
        time.sleep(0.3)
    
    是否正在粘贴 = False
    
    if 正常完成 and not 是否被停止:
        pyperclip.copy("")
        root.after(100, lambda: root.deiconify())
        root.after(200, lambda: messagebox.showinfo("完成", "所有内容已粘贴完毕！"))
    else:
        # 如果是被停止的，只恢复窗口，不显示完成消息
        pass

def 停止粘贴():
    global 是否正在粘贴, 当前索引, 是否被停止, 当前粘贴线程
    是否正在粘贴 = False
    当前索引 = 0
    是否被停止 = True
    
    # 清除所有粘贴事件
    粘贴事件.set()  # 设置事件，让等待中的线程能够退出
    
    # 尝试移除热键（多次尝试确保清除）
    for _ in range(3):
        try:
            keyboard.remove_hotkey('ctrl+v')
        except:
            break
    
    root.deiconify()

# 第一行按钮：导入导出
操作按钮容器_第一行 = tk.Frame(第二页按钮容器, bg=颜色配置['背景色'])
操作按钮容器_第一行.pack(fill=tk.X, pady=(0, 5))

导入按钮 = 创建按钮(操作按钮容器_第一行, "📂 导入", '次要', 导入配置, 宽度=14)
导入按钮.config(padx=10)
导入按钮.pack(side=tk.LEFT, padx=3, expand=True)

导出按钮 = 创建按钮(操作按钮容器_第一行, "💾 导出", '次要', 导出配置, 宽度=14)
导出按钮.config(padx=10)
导出按钮.pack(side=tk.LEFT, padx=3, expand=True)

复制选中按钮 = 创建按钮(操作按钮容器_第一行, "📋 复制", '紫色', 复制选中内容, 宽度=14)
复制选中按钮.config(padx=10)
复制选中按钮.pack(side=tk.LEFT, padx=3, expand=True)

# 第二行按钮：开始停止清空
操作按钮容器_第二行 = tk.Frame(第二页按钮容器, bg=颜色配置['背景色'])
操作按钮容器_第二行.pack(fill=tk.X)

从头开始按钮_第二页 = 创建按钮(操作按钮容器_第二行, "▶️ 从头开始", '成功', 从头开始粘贴, 宽度=12)
从头开始按钮_第二页.config(padx=8)
从头开始按钮_第二页.pack(side=tk.LEFT, padx=3, expand=True)

从选中开始按钮_第二页 = 创建按钮(操作按钮容器_第二行, "📍 选中开始", '成功', 从选中开始粘贴, 宽度=12)
从选中开始按钮_第二页.config(padx=8)
从选中开始按钮_第二页.pack(side=tk.LEFT, padx=3, expand=True)

停止按钮 = 创建按钮(操作按钮容器_第二行, "⏹ 停止", '警告', 停止粘贴, 宽度=12)
停止按钮.config(padx=8)
停止按钮.pack(side=tk.LEFT, padx=3, expand=True)

清空列表按钮 = 创建按钮(操作按钮容器_第二行, "🗑️ 清空", '警告', 清空列表, 宽度=12)
清空列表按钮.config(padx=8)
清空列表按钮.pack(side=tk.LEFT, padx=3, expand=True)

# ========== 第三页：任务执行 ==========
第三页 = tk.Frame(notebook, bg=颜色配置['背景色'])
notebook.add(第三页, text="🚀 任务执行")

# 任务列表区域
任务卡片 = tk.Frame(第三页, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                    highlightthickness=1)
任务卡片.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)
任务内部容器 = tk.Frame(任务卡片, bg=颜色配置['卡片色'])
任务内部容器.pack(fill=tk.BOTH, padx=15, pady=15)

任务列表标题 = tk.Label(任务内部容器, text="复制后的额外操作（按顺序执行）:", font=标签字体, 
                        bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
任务列表标题.pack(anchor=tk.W, pady=(0, 5))

任务提示标签 = tk.Label(任务内部容器, text="💡 按Ctrl+V复制下一条并执行任务（橙色⏩除外）", 
                         font=("微软雅黑", 8), bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
任务提示标签.pack(anchor=tk.W, pady=(0, 8))

任务列表容器 = tk.Frame(任务内部容器, bg=颜色配置['卡片色'])
任务列表容器.pack(fill=tk.BOTH, expand=True)

任务滚动条 = tk.Scrollbar(任务列表容器, bg=颜色配置['卡片色'], 
                           highlightthickness=0, troughcolor=颜色配置['背景色'])
任务滚动条.pack(side=tk.RIGHT, fill=tk.Y)

# 任务列表显示
任务列表显示 = tk.Listbox(任务列表容器, font=("微软雅黑", 10),
                          bg=颜色配置['背景色'], fg=颜色配置['文字色'],
                          relief=tk.FLAT, highlightthickness=0,
                          activestyle='none')
任务列表显示.pack(fill=tk.BOTH, expand=True)
任务滚动条.config(command=任务列表显示.yview)
任务列表显示.config(yscrollcommand=任务滚动条.set)

def 更新任务列表显示():
    """更新任务列表显示"""
    任务列表显示.delete(0, tk.END)
    for 任务 in 任务列表:
        if isinstance(任务, dict):
            任务名称 = 任务["任务"]
            条件 = 任务["条件"]
            if 条件:
                显示文本 = f"{任务名称} [橙色]"
            else:
                显示文本 = 任务名称
            任务列表显示.insert(tk.END, 显示文本)
        else:
            任务列表显示.insert(tk.END, 任务)

# 初始化任务列表显示
更新任务列表显示()

# 任务状态标签
任务状态标签 = tk.Label(任务内部容器, text=f"当前任务: {len(任务列表)} 个", font=("微软雅黑", 9),
                         bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
任务状态标签.pack(anchor=tk.E, pady=(5, 0))

# 可添加的任务选项
可添加任务 = ["回车", "粘贴", "自定义按键", "自定义延迟"]

def 添加任务到列表():
    """添加任务到列表"""
    def 添加选中任务():
        选中项 = 任务选择框.curselection()
        if 选中项:
            任务名称 = 任务选择框.get(选中项[0])
            条件 = 条件复选框_var.get()
            
            if 任务名称 == "自定义按键":
                添加窗口.destroy()
                打开自定义按键窗口(条件=条件)
            elif 任务名称 == "自定义延迟":
                添加窗口.destroy()
                打开自定义延迟窗口(条件=条件)
            else:
                # 构建任务字符串，带条件信息
                任务信息 = {"任务": 任务名称, "条件": 条件}
                任务列表.append(任务信息)
                更新任务列表显示()
                任务状态标签.config(text=f"当前任务: {len(任务列表)} 个")
                添加窗口.destroy()
    
    添加窗口 = tk.Toplevel(root)
    添加窗口.title("添加任务")
    添加窗口.geometry("300x300")
    添加窗口.configure(bg=颜色配置['背景色'])
    添加窗口.resizable(False, False)
    添加窗口.attributes('-topmost', True)
    
    添加内部容器 = tk.Frame(添加窗口, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                            highlightthickness=1)
    添加内部容器.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    tk.Label(添加内部容器, text="选择要添加的任务:", font=标签字体,
            bg=颜色配置['卡片色'], fg=颜色配置['文字色']).pack(pady=(10, 5))
    
    任务选择框 = tk.Listbox(添加内部容器, font=("微软雅黑", 10),
                           bg=颜色配置['背景色'], fg=颜色配置['文字色'],
                           relief=tk.FLAT, highlightthickness=0,
                           height=4, activestyle='none')
    任务选择框.pack(fill=tk.X, pady=(0, 10))
    for 任务 in 可添加任务:
        任务选择框.insert(tk.END, 任务)
    
    # 条件复选框
    条件复选框_var = tk.BooleanVar(value=False)
    条件复选框 = tk.Checkbutton(添加内部容器, text="只在橙色条目时执行", 
                                font=("微软雅黑", 9),
                                bg=颜色配置['卡片色'], fg=颜色配置['文字色'],
                                activebackground=颜色配置['卡片色'],
                                variable=条件复选框_var,
                                relief=tk.FLAT)
    条件复选框.pack(anchor=tk.W, pady=(5, 10))
    
    按钮容器 = tk.Frame(添加内部容器, bg=颜色配置['卡片色'])
    按钮容器.pack(fill=tk.X)
    
    确定按钮 = 创建按钮(按钮容器, "确定", '主色', 添加选中任务, 宽度=8)
    确定按钮.pack(side=tk.LEFT, padx=3, expand=True)
    
    取消按钮 = 创建按钮(按钮容器, "取消", '次要', 添加窗口.destroy, 宽度=8)
    取消按钮.pack(side=tk.LEFT, padx=3, expand=True)
    
    添加窗口.protocol('WM_DELETE_WINDOW', 添加窗口.destroy)

def 打开自定义延迟窗口(条件=False):
    """打开自定义延迟设置窗口"""
    设置窗口 = tk.Toplevel(root)
    设置窗口.title("设置自定义延迟")
    设置窗口.geometry("350x180")
    设置窗口.configure(bg=颜色配置['背景色'])
    设置窗口.resizable(False, False)
    设置窗口.attributes('-topmost', True)
    
    设置内部容器 = tk.Frame(设置窗口, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                            highlightthickness=1)
    设置内部容器.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    tk.Label(设置内部容器, text="设置延迟时间（秒）:", font=标签字体,
            bg=颜色配置['卡片色'], fg=颜色配置['文字色']).pack(pady=(10, 5))
    
    延迟输入框 = tk.Entry(设置内部容器, font=("微软雅黑", 11),
                         bg=颜色配置['背景色'], fg=颜色配置['文字色'],
                         relief=tk.FLAT, highlightbackground=颜色配置['边框色'],
                         highlightthickness=1, width=20)
    延迟输入框.pack(pady=(0, 15))
    延迟输入框.focus_set()
    
    # 添加提示信息
    提示标签 = tk.Label(设置内部容器, text="请输入数字，例如: 0.5", font=("微软雅黑", 8),
                       bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
    提示标签.pack()
    
    def 确认延迟():
        延迟值 = 延迟输入框.get().strip()
        try:
            延迟时间 = float(延迟值)
            if 延迟时间 <= 0:
                messagebox.showwarning("提示", "延迟时间必须大于0！")
                return
            
            # 将自定义延迟添加到任务列表（使用传递过来的条件）
            任务信息 = {"任务": f"延迟:{延迟时间}", "条件": 条件}
            任务列表.append(任务信息)
            更新任务列表显示()
            任务状态标签.config(text=f"当前任务: {len(任务列表)} 个")
            
            messagebox.showinfo("成功", f"已添加自定义延迟: {延迟时间}秒")
            设置窗口.destroy()
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的数字！")
    
    def 关闭设置窗口():
        设置窗口.destroy()
    
    按钮容器 = tk.Frame(设置内部容器, bg=颜色配置['卡片色'])
    按钮容器.pack(fill=tk.X, pady=(15, 0))
    
    确定按钮 = 创建按钮(按钮容器, "确定", '主色', 确认延迟, 宽度=8)
    确定按钮.pack(side=tk.LEFT, padx=3, expand=True)
    
    取消按钮 = 创建按钮(按钮容器, "取消", '次要', 关闭设置窗口, 宽度=8)
    取消按钮.pack(side=tk.LEFT, padx=3, expand=True)
    
    设置窗口.bind('<Return>', lambda e: 确认延迟())
    设置窗口.protocol('WM_DELETE_WINDOW', 关闭设置窗口)

def 打开自定义按键窗口(条件=False):
    """打开自定义按键选择窗口"""
    设置窗口 = tk.Toplevel(root)
    设置窗口.title("设置自定义按键")
    设置窗口.geometry("400x200")
    设置窗口.configure(bg=颜色配置['背景色'])
    设置窗口.resizable(False, False)
    设置窗口.attributes('-topmost', True)
    
    设置内部容器 = tk.Frame(设置窗口, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                            highlightthickness=1)
    设置内部容器.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    tk.Label(设置内部容器, text="请按下要自定义的按键:", font=标签字体,
            bg=颜色配置['卡片色'], fg=颜色配置['文字色']).pack(pady=(20, 10))
    
    显示框 = tk.Label(设置内部容器, text="按下按键...", font=("微软雅黑", 12),
                     bg=颜色配置['背景色'], fg=颜色配置['次要文字'],
                     relief=tk.FLAT, highlightbackground=颜色配置['边框色'], highlightthickness=1,
                     padx=20, pady=15)
    显示框.pack(pady=(10, 20))
    
    # 添加提示信息
    提示标签 = tk.Label(设置内部容器, text="按 ESC 取消 | 可以使用修饰键(Ctrl/Shift/Alt)", font=("微软雅黑", 8),
                       bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
    提示标签.pack()
    
    窗口关闭标记 = [False]
    当前主键 = ['']
    
    def 更新显示():
        """更新显示框内容"""
        try:
            if 窗口关闭标记[0]:
                return
                
            当前按键 = []
            # 检测修饰键
            if keyboard.is_pressed('ctrl'):
                当前按键.append('Ctrl')
            if keyboard.is_pressed('shift'):
                当前按键.append('Shift')
            if keyboard.is_pressed('alt'):
                当前按键.append('Alt')
            
            # 添加主键
            if 当前主键[0]:
                # 特殊按键名称映射（保留常用按键的友好显示）
                特殊按键映射 = {
                    'up': '↑', 'down': '↓', 'left': '←', 'right': '→',
                    'backspace': 'Backspace', 'tab': 'Tab', 'home': 'Home', 'end': 'End',
                    'page_up': 'Page Up', 'page_down': 'Page Down', 'insert': 'Insert',
                    'delete': 'Delete', 'prior': 'Page Up', 'next': 'Page Down',
                    'return': 'Enter', 'space': 'Space', 'escape': 'Esc'
                }
                显示名称 = 特殊按键映射.get(当前主键[0], 当前主键[0].upper())
                当前按键.append(显示名称)
            
            # 如果只有修饰键没有主键，显示红色
            if 当前按键 and len(当前按键) <= 3 and not 当前主键[0]:
                显示框.config(text='+'.join(当前按键), fg=颜色配置['警告色'])
            else:
                显示框.config(text='+'.join(当前按键), fg=颜色配置['次要文字'])
            
            # 如果窗口还存在，继续更新
            if 设置窗口.winfo_exists() and not 窗口关闭标记[0]:
                设置窗口.after(50, 更新显示)
        except:
            pass
    
    # 启动显示更新
    设置窗口.after(50, 更新显示)
    
    def 按键事件(event):
        if 窗口关闭标记[0]:
            return
            
        # ESC键关闭窗口
        if event.keysym.lower() == 'escape':
            关闭设置窗口()
            return
            
        # 更新当前主键
        键名 = event.keysym.lower()
        
        # 只过滤左右版本的修饰键（避免重复），允许单独的ctrl/shift/alt作为主键
        修饰键列表 = ['ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift_l', 'shift_r']
        当前主键[0] = 键名
            
        # 使用 keyboard 库检测实际按下的按键
        按键列表 = []
        
        # 检测修饰键（跳过当前主键，避免重复）
        if keyboard.is_pressed('ctrl') and 键名 not in ['ctrl', 'control']:
            按键列表.append("ctrl")
        if keyboard.is_pressed('shift') and 键名 not in ['shift']:
            按键列表.append("shift")
        if keyboard.is_pressed('alt') and 键名 not in ['alt']:
            按键列表.append("alt")
        
        # 添加主键（所有按键都允许）
        按键列表.append(键名)
        
        # 至少要有一个主键（可以只有单键）
        if len(按键列表) >= 1:
            新快捷键 = '+'.join(按键列表)
            
            # 对于特殊按键，跳过Tk格式测试（因为某些特殊按键在Tk格式中可能不兼容）
            特殊按键列表 = ['up', 'down', 'left', 'right', 'backspace', 'tab', 'home', 'end', 
                          'page_up', 'page_down', 'insert', 'delete', 'prior', 'next', 'return', 'space']
            
            # 只有非特殊按键才进行Tk格式测试
            if 键名 not in 特殊按键列表:
                try:
                    tk格式 = 转换为Tk格式(新快捷键)
                    # 尝试临时绑定来测试是否有效
                    root.bind(tk格式, lambda e: None)
                    root.unbind(tk格式)
                except Exception as e:
                    return
            
            # 将自定义按键添加到任务列表（使用传递过来的条件）
            任务信息 = {"任务": f"按键:{新快捷键}", "条件": 条件}
            任务列表.append(任务信息)
            更新任务列表显示()
            任务状态标签.config(text=f"当前任务: {len(任务列表)} 个")
            
            显示文本 = 格式化显示快捷键(新快捷键)
            messagebox.showinfo("成功", f"已添加自定义按键: {显示文本}")
            
            设置窗口.destroy()
    
    def 按键释放事件(event):
        """处理按键释放"""
        键名 = event.keysym.lower()
        # 只过滤左右版本的修饰键和escape，其他按键都允许
        修饰键列表 = ['ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift_l', 'shift_r', 'escape']
        if 键名 not in 修饰键列表:
            当前主键[0] = ''
    
    def 关闭设置窗口():
        """关闭设置窗口"""
        窗口关闭标记[0] = True
        try:
            设置窗口.destroy()
        except:
            pass
    
    # 绑定按键事件
    设置窗口.bind('<Key>', 按键事件)
    设置窗口.bind('<KeyRelease>', 按键释放事件)
    设置窗口.protocol('WM_DELETE_WINDOW', 关闭设置窗口)
    显示框.focus_set()

def 导入任务配置():
    """导入任务配置"""
    try:
        文件路径 = filedialog.askopenfilename(
            title="导入任务配置",
            filetypes=[("任务配置文件", "*.task"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if 文件路径:
            import json
            with open(文件路径, 'r', encoding='utf-8') as f:
                内容 = f.read().strip()
                if 内容:
                    任务列表.clear()
                    任务数据 = json.loads(内容)
                    任务列表.extend(任务数据)
                    更新任务列表显示()
                    任务状态标签.config(text=f"当前任务: {len(任务列表)} 个")
                    messagebox.showinfo("成功", f"已导入 {len(任务列表)} 个任务！")
                else:
                    messagebox.showwarning("提示", "文件为空！")
    except json.JSONDecodeError:
        messagebox.showerror("错误", "配置文件格式错误！")
    except Exception as e:
        messagebox.showerror("错误", f"导入失败: {str(e)}")

def 导出任务配置():
    """导出任务配置"""
    if len(任务列表) == 0:
        messagebox.showwarning("提示", "任务列表为空！")
        return
    
    try:
        import json
        文件路径 = filedialog.asksaveasfilename(
            title="导出任务配置",
            initialfile="任务配置",
            defaultextension=".task",
            filetypes=[("任务配置文件", "*.task"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if 文件路径:
            with open(文件路径, 'w', encoding='utf-8') as f:
                json.dump(任务列表, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"已导出 {len(任务列表)} 个任务到 {文件路径}！")
    except Exception as e:
        messagebox.showerror("错误", f"导出失败: {str(e)}")

def 删除选中的任务():
    """删除选中的任务"""
    选中项 = 任务列表显示.curselection()
    if 选中项:
        索引 = 选中项[0]
        任务列表.pop(索引)
        更新任务列表显示()
        任务状态标签.config(text=f"当前任务: {len(任务列表)} 个")
    else:
        messagebox.showwarning("提示", "请先选择要删除的任务！")

def 任务上移():
    """将选中的任务上移"""
    选中项 = 任务列表显示.curselection()
    if 选中项:
        索引 = 选中项[0]
        if 索引 > 0:
            任务列表[索引], 任务列表[索引-1] = 任务列表[索引-1], 任务列表[索引]
            更新任务列表显示()
            任务列表显示.selection_set(索引-1)
        else:
            messagebox.showinfo("提示", "已经是第一个任务了！")
    else:
        messagebox.showwarning("提示", "请先选择要移动的任务！")

def 任务下移():
    """将选中的任务下移"""
    选中项 = 任务列表显示.curselection()
    if 选中项:
        索引 = 选中项[0]
        if 索引 < len(任务列表) - 1:
            任务列表[索引], 任务列表[索引+1] = 任务列表[索引+1], 任务列表[索引]
            更新任务列表显示()
            任务列表显示.selection_set(索引+1)
        else:
            messagebox.showinfo("提示", "已经是最后一个任务了！")
    else:
        messagebox.showwarning("提示", "请先选择要移动的任务！")

def 清空任务列表():
    """清空任务列表"""
    if messagebox.askyesno("确认", "确定要清空所有任务吗？"):
        任务列表.clear()
        更新任务列表显示()
        任务状态标签.config(text=f"当前任务: {len(任务列表)} 个")

# 任务按钮区域
任务按钮容器 = tk.Frame(第三页, bg=颜色配置['背景色'])
任务按钮容器.pack(fill=tk.X, padx=20, pady=(0, 10))

# 第一行：添加、导入、导出、删除、清空
操作任务按钮容器_第一行 = tk.Frame(任务按钮容器, bg=颜色配置['背景色'])
操作任务按钮容器_第一行.pack(fill=tk.X, pady=(0, 5))

添加任务按钮 = 创建按钮(操作任务按钮容器_第一行, "➕ 添加", '主色', 添加任务到列表, 宽度=10)
添加任务按钮.config(padx=6)
添加任务按钮.pack(side=tk.LEFT, padx=2, expand=True)

导入任务按钮 = 创建按钮(操作任务按钮容器_第一行, "📂 导入", '次要', 导入任务配置, 宽度=10)
导入任务按钮.config(padx=6)
导入任务按钮.pack(side=tk.LEFT, padx=2, expand=True)

导出任务按钮 = 创建按钮(操作任务按钮容器_第一行, "💾 导出", '次要', 导出任务配置, 宽度=10)
导出任务按钮.config(padx=6)
导出任务按钮.pack(side=tk.LEFT, padx=2, expand=True)

删除任务按钮 = 创建按钮(操作任务按钮容器_第一行, "➖ 删除", '警告', 删除选中的任务, 宽度=10)
删除任务按钮.config(padx=6)
删除任务按钮.pack(side=tk.LEFT, padx=2, expand=True)

清空任务按钮 = 创建按钮(操作任务按钮容器_第一行, "🗑️ 清空", '警告', 清空任务列表, 宽度=10)
清空任务按钮.config(padx=6)
清空任务按钮.pack(side=tk.LEFT, padx=2, expand=True)

# 第二行：上移、下移、从头开始、选中开始
操作任务按钮容器_第二行 = tk.Frame(任务按钮容器, bg=颜色配置['背景色'])
操作任务按钮容器_第二行.pack(fill=tk.X)

上移任务按钮 = 创建按钮(操作任务按钮容器_第二行, "⬆️ 上移", '次要', 任务上移, 宽度=11)
上移任务按钮.config(padx=7)
上移任务按钮.pack(side=tk.LEFT, padx=2, expand=True)

下移任务按钮 = 创建按钮(操作任务按钮容器_第二行, "⬇️ 下移", '次要', 任务下移, 宽度=11)
下移任务按钮.config(padx=7)
下移任务按钮.pack(side=tk.LEFT, padx=2, expand=True)

从头开始按钮 = 创建按钮(操作任务按钮容器_第二行, "▶️ 从头开始", '成功', 从头开始粘贴, 宽度=11)
从头开始按钮.config(padx=7)
从头开始按钮.pack(side=tk.LEFT, padx=2, expand=True)

从选中开始按钮 = 创建按钮(操作任务按钮容器_第二行, "📍 选中开始", '成功', 从选中开始粘贴, 宽度=11)
从选中开始按钮.config(padx=7)
从选中开始按钮.pack(side=tk.LEFT, padx=2, expand=True)

# ========== 第四页：快捷键管理 ==========
第四页 = tk.Frame(notebook, bg=颜色配置['背景色'])
notebook.add(第四页, text="⌨️ 快捷键")

# 快捷键管理区域
快捷键卡片 = tk.Frame(第四页, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                    highlightthickness=1)
快捷键卡片.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)
快捷键内部容器 = tk.Frame(快捷键卡片, bg=颜色配置['卡片色'])
快捷键内部容器.pack(fill=tk.BOTH, padx=15, pady=15)

# 开始粘贴快捷键设置（放在前面）
开始快捷键标签 = tk.Label(快捷键内部容器, text="开始粘贴快捷键:", font=标签字体, 
                         bg=颜色配置['卡片色'], fg=颜色配置['次要文字'], anchor=tk.W)
开始快捷键标签.pack(fill=tk.X, pady=(0, 8))

开始快捷键输入容器 = tk.Frame(快捷键内部容器, bg=颜色配置['卡片色'])
开始快捷键输入容器.pack(fill=tk.X, pady=(0, 15))

# 创建开始快捷键显示标签并保存引用
开始快捷键显示_标签对象 = tk.Label(开始快捷键输入容器, text=开始快捷键显示, font=("微软雅黑", 11),
                                bg=颜色配置['背景色'], fg=颜色配置['主色'],
                                relief=tk.FLAT, highlightbackground=颜色配置['边框色'], highlightthickness=1,
                                padx=10, pady=8)
开始快捷键显示_标签对象.pack(side=tk.LEFT)

设置开始快捷键按钮 = 创建按钮(开始快捷键输入容器, "设置", '次要', lambda: 设置快捷键("开始"), 宽度=8)
设置开始快捷键按钮.pack(side=tk.RIGHT, padx=(10, 0))

# 停止粘贴快捷键设置（放在后面）
停止快捷键标签 = tk.Label(快捷键内部容器, text="停止粘贴快捷键:", font=标签字体, 
                         bg=颜色配置['卡片色'], fg=颜色配置['次要文字'], anchor=tk.W)
停止快捷键标签.pack(fill=tk.X, pady=(0, 8))

停止快捷键输入容器 = tk.Frame(快捷键内部容器, bg=颜色配置['卡片色'])
停止快捷键输入容器.pack(fill=tk.X, pady=(0, 15))

# 创建停止快捷键显示标签并保存引用
停止快捷键显示_标签对象 = tk.Label(停止快捷键输入容器, text=停止快捷键显示, font=("微软雅黑", 11),
                                bg=颜色配置['背景色'], fg=颜色配置['主色'],
                                relief=tk.FLAT, highlightbackground=颜色配置['边框色'], highlightthickness=1,
                                padx=10, pady=8)
停止快捷键显示_标签对象.pack(side=tk.LEFT)

设置停止快捷键按钮 = 创建按钮(停止快捷键输入容器, "设置", '次要', lambda: 设置快捷键("停止"), 宽度=8)
设置停止快捷键按钮.pack(side=tk.RIGHT, padx=(10, 0))

# 冲突提示
冲突提示标签 = tk.Label(快捷键内部容器, text="⚠️ 当前快捷键可能与其他软件冲突，建议更换", 
                         font=("微软雅黑", 9), bg=颜色配置['卡片色'], fg=颜色配置['警告色'])

# 提示信息
提示信息 = tk.Label(快捷键内部容器, 
                    text="提示：\n• 快捷键建议使用组合键（如 Ctrl+Shift+X）\n• 避免与其他常用快捷键冲突\n• 常见冲突快捷键：Ctrl+C、Ctrl+V、Ctrl+A、Ctrl+Z、F1-F12", 
                    font=("微软雅黑", 9), bg=颜色配置['卡片色'], fg=颜色配置['次要文字'],
                    justify=tk.LEFT, anchor=tk.W)
提示信息.pack(fill=tk.X, pady=(10, 0))

# 恢复默认快捷键函数
def 恢复默认快捷键():
    默认开始 = "ctrl+shift+s"
    默认停止 = "ctrl+shift+x"
    
    # 恢复开始快捷键
    更新开始快捷键(默认开始)
    开始快捷键显示_标签对象.config(text=格式化显示快捷键(默认开始))
    
    # 恢复停止快捷键
    更新停止快捷键(默认停止)
    停止快捷键显示_标签对象.config(text=格式化显示快捷键(默认停止))
    
    # 检查冲突
    检查快捷键冲突(默认开始)
    检查快捷键冲突(默认停止)
    
    messagebox.showinfo("成功", "已恢复默认快捷键：\n开始: Ctrl+Shift+S\n停止: Ctrl+Shift+X")

# 恢复默认按钮（移动到提示信息下面）
恢复默认按钮 = 创建按钮(快捷键内部容器, "↺ 恢复默认", '次要', 恢复默认快捷键, 宽度=15)
恢复默认按钮.pack(pady=(10, 0))

# 检查快捷键冲突
def 检查快捷键冲突(快捷键):
    冲突列表 = ['ctrl+c', 'ctrl+v', 'ctrl+a', 'ctrl+z', 'ctrl+x', 'ctrl+s', 'ctrl+f', 'ctrl+n', 'ctrl+w', 'ctrl+p', 'ctrl+o', 'ctrl+q', 'ctrl+r', 'ctrl+y', 'ctrl+b', 'ctrl+i', 'ctrl+u', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']
    
    if 快捷键.lower() in 冲突列表:
        冲突提示标签.pack(pady=(0, 10))
    else:
        冲突提示标签.pack_forget()

# 设置快捷键的函数
def 设置快捷键(快捷键类型):
    显示名称 = {
        "停止": "停止粘贴",
        "开始": "开始粘贴"
    }.get(快捷键类型, 快捷键类型)
    
    设置窗口 = tk.Toplevel(root)
    设置窗口.title(f"设置{显示名称}快捷键")
    设置窗口.geometry("400x200")
    设置窗口.configure(bg=颜色配置['背景色'])
    设置窗口.resizable(False, False)
    设置窗口.attributes('-topmost', True)
    
    设置内部容器 = tk.Frame(设置窗口, bg=颜色配置['卡片色'], highlightbackground=颜色配置['边框色'], 
                            highlightthickness=1)
    设置内部容器.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    tk.Label(设置内部容器, text=f"请按下新的{显示名称}快捷键:", font=标签字体,
            bg=颜色配置['卡片色'], fg=颜色配置['文字色']).pack(pady=(20, 10))
    
    显示框 = tk.Label(设置内部容器, text="按下按键...", font=("微软雅黑", 12),
                     bg=颜色配置['背景色'], fg=颜色配置['次要文字'],
                     relief=tk.FLAT, highlightbackground=颜色配置['边框色'], highlightthickness=1,
                     padx=20, pady=15)
    显示框.pack(pady=(10, 20))
    
    # 添加提示信息
    提示标签 = tk.Label(设置内部容器, text="按 ESC 取消 | 按组合键设置", font=("微软雅黑", 8),
                       bg=颜色配置['卡片色'], fg=颜色配置['次要文字'])
    提示标签.pack()
    
    窗口关闭标记 = [False]  # 使用列表作为可变标记
    当前主键 = ['']  # 记录当前按下的主键
    
    def 更新显示():
        """更新显示框内容"""
        try:
            if 窗口关闭标记[0]:
                return
                
            当前按键 = []
            # 检测修饰键
            if keyboard.is_pressed('ctrl'):
                当前按键.append('Ctrl')
            if keyboard.is_pressed('shift'):
                当前按键.append('Shift')
            if keyboard.is_pressed('alt'):
                当前按键.append('Alt')
            
            # 添加主键
            if 当前主键[0]:
                当前按键.append(当前主键[0].upper())
            
            # 如果只有修饰键没有主键，显示红色
            if 当前按键 and len(当前按键) <= 3 and not 当前主键[0]:
                显示框.config(text='+'.join(当前按键), fg=颜色配置['警告色'])
            else:
                显示框.config(text='+'.join(当前按键), fg=颜色配置['次要文字'])
            
            # 如果窗口还存在，继续更新
            if 设置窗口.winfo_exists() and not 窗口关闭标记[0]:
                设置窗口.after(50, 更新显示)
        except:
            pass
    
    # 启动显示更新
    设置窗口.after(50, 更新显示)
    
    def 按键事件(event):
        if 窗口关闭标记[0]:
            return
            
        # ESC键关闭窗口
        if event.keysym.lower() == 'escape':
            关闭设置窗口()
            return
            
        # 更新当前主键
        键名 = event.keysym.lower()
        
        # 过滤修饰键本身
        修饰键列表 = ['ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift_l', 'shift_r', 'control', 'alt', 'shift']
        if 键名 not in 修饰键列表 and len(键名) <= 4:
            当前主键[0] = 键名
            
        # 使用 keyboard 库检测实际按下的按键
        按键列表 = []
        
        # 检测修饰键
        if keyboard.is_pressed('ctrl'):
            按键列表.append("ctrl")
        if keyboard.is_pressed('shift'):
            按键列表.append("shift")
        if keyboard.is_pressed('alt'):
            按键列表.append("alt")
        
        # 过滤无效按键
        if len(键名) > 4:
            当前主键[0] = ''
            return
        
        # 添加主键
        按键列表.append(键名)
        
        # 至少要有一个修饰键和一个主键
        if len(按键列表) >= 2:
            新快捷键 = '+'.join(按键列表)
            
            # 转换为Tk格式测试是否有效
            try:
                tk格式 = 转换为Tk格式(新快捷键)
                # 尝试临时绑定来测试是否有效
                root.bind(tk格式, lambda e: None)
                root.unbind(tk格式)
            except Exception as e:
                return
            
            冲突列表 = ['ctrl+c', 'ctrl+v', 'ctrl+a', 'ctrl+z', 'ctrl+x', 'ctrl+s', 'ctrl+f', 'ctrl+n', 'ctrl+w', 'ctrl+p', 'ctrl+o', 'ctrl+q', 'ctrl+r', 'ctrl+y', 'ctrl+b', 'ctrl+i', 'ctrl+u', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']
            
            if 新快捷键 in 冲突列表:
                messagebox.showwarning("快捷键冲突", f"{新快捷键} 是常见快捷键，可能与其他软件冲突！\n\n建议使用其他组合键。")
            
            if 快捷键类型 == "停止":
                更新停止快捷键(新快捷键)
                快捷键提示.config(text=f"按 {开始快捷键显示} 开始 | 按 {停止快捷键显示} 停止")
                停止快捷键显示_标签对象.config(text=停止快捷键显示)
                检查快捷键冲突(新快捷键)
                messagebox.showinfo("成功", f"停止快捷键已设置为 {停止快捷键显示}")
            elif 快捷键类型 == "开始":
                更新开始快捷键(新快捷键)
                快捷键提示.config(text=f"按 {开始快捷键显示} 开始 | 按 {停止快捷键显示} 停止")
                开始快捷键显示_标签对象.config(text=开始快捷键显示)
                检查快捷键冲突(新快捷键)
                messagebox.showinfo("成功", f"开始快捷键已设置为 {开始快捷键显示}")
            
            设置窗口.destroy()
    
    def 按键释放事件(event):
        """处理按键释放"""
        键名 = event.keysym.lower()
        修饰键列表 = ['ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift_l', 'shift_r', 'control', 'alt', 'shift', 'escape']
        if 键名 not in 修饰键列表:
            当前主键[0] = ''
    
    def 关闭设置窗口():
        """关闭设置窗口"""
        窗口关闭标记[0] = True
        try:
            设置窗口.destroy()
        except:
            pass
    
    # 绑定按键事件
    设置窗口.bind('<Key>', 按键事件)
    设置窗口.bind('<KeyRelease>', 按键释放事件)
    设置窗口.protocol('WM_DELETE_WINDOW', 关闭设置窗口)
    显示框.focus_set()

# 初始化默认快捷键
更新停止快捷键(停止快捷键)
更新开始快捷键(开始快捷键)
检查快捷键冲突(停止快捷键)
检查快捷键冲突(开始快捷键)

root.mainloop()