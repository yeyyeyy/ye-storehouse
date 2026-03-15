import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path
import os, sys
import shutil
import ctypes
import subprocess
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

root = tk.Tk()
root.title("文件管理")
root.geometry("650x650+550+150")

# 尝试导入并初始化tkinterdnd2
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    拖拽可用 = True
    
    # 手动加载64位版本的TkDnD库
    try:
        # 根据系统架构选择正确的平台
        if sys.maxsize > 2**32:  # 64位系统
            platform = 'win-x64'
        else:  # 32位系统
            platform = 'win-x86'
        
        tkdnd_dir = os.path.join(os.path.dirname(TkinterDnD.__file__), 'tkdnd', platform)
        if os.path.exists(tkdnd_dir):
            # 添加到Tcl路径
            root.tk.call('lappend', 'auto_path', tkdnd_dir)
            # 尝试加载
            root.tk.call('package', 'require', 'tkdnd')
            print(f"TkDnD loaded successfully from {platform}")
        else:
            print(f"TkDnD library not found for {platform}")
            拖拽可用 = False
    except Exception as e:
        print(f"Failed to load TkDnD: {e}")
        拖拽可用 = False
except ImportError:
    拖拽可用 = False
try:
    临时目录 = sys._MEIPASS
    图标路径 = os.path.join(临时目录, "图标.ico\\图标.ico")
    root.iconbitmap(图标路径)
    图标方式 = 0
except:
    try:
        root.iconbitmap("E:\\Python\\图标.ico")
        图标方式 = 1
    except:
        图标方式 = 2

# 创建标签页
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 第一个标签页：文件管理
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="文件管理")

# 第二个标签页：视频提取音频
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="视频提取音频")

# ============ 第一个标签页：文件管理 ============
label = tk.Label(tab1,text="文件管理",font=("微软雅黑",11,"bold"),fg="black",pady=0)
label.pack(pady=5)

frame = tk.Frame(tab1)
frame.pack()

文件夹 = "无"
def 列出文件():
    global 文件夹
    if 文件夹 == "无":
        return
    文件列表.delete(0,tk.END)
    folder = Path(文件夹)
    for file_path in folder.iterdir():
        文件列表.insert(tk.END,file_path)
def 选择文件夹():
    global 文件夹
    记录 = 文件夹
    文件夹 = filedialog.askdirectory(
        title="选择文件夹",
    )
    if 文件夹:
        messagebox.showinfo("提示","文件夹选择成功~")
        列出文件()
    else:
        文件夹 = 记录
    当前文件夹.config(text=f'当前选择文件夹：{文件夹}')

选择文件夹按钮 = tk.Button(frame,text="选择文件夹",fg="#3ECACF",font=("微软雅黑",9),width=15,height=2,command=选择文件夹)
选择文件夹按钮.pack(side=tk.LEFT)
当前文件夹 = tk.Label(tab1,text=f'当前选择文件夹：{文件夹}')
当前文件夹.pack()

文件列表文本 = tk.Label(tab1,text="文件列表",font=("微软雅黑",10,"bold"),fg="orange",pady=0)
文件列表文本.pack()

frame1 = tk.Frame(tab1)
frame1.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

条 = tk.Scrollbar(frame1)
条.pack(side=tk.RIGHT, fill=tk.Y)
文件列表 = tk.Listbox(frame1,width=55,height=8,selectmode="extended")
文件列表.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
文件列表.config(yscrollcommand=条.set)
条.config(command=文件列表.yview)

# 文件列表拖拽处理
def 处理文件拖拽(event):
    """处理拖拽到文件列表的文件"""
    data = event.data
    # 去除大括号和引号
    if data.startswith('{') and data.endswith('}'):
        data = data[1:-1]

    # 分割多个文件路径
    files = data.replace('}', '').split(' {')

    for 文件路径 in files:
        文件路径 = 文件路径.strip()
        if 文件路径:
            # 如果是文件，复制到当前文件夹
            if os.path.isfile(文件路径):
                try:
                    文件名 = os.path.basename(文件路径)
                    目标路径 = os.path.join(文件夹, 文件名)
                    shutil.copy2(文件路径, 目标路径)
                    列出文件()
                except Exception as e:
                    messagebox.showerror("错误",f"复制失败：{str(e)}")
            # 如果是文件夹，提示用户
            elif os.path.isdir(文件路径):
                messagebox.showinfo("提示","不支持拖拽文件夹")

# 绑定拖拽事件到文件列表
if 拖拽可用:
    try:
        文件列表.drop_target_register(DND_FILES)
        文件列表.dnd_bind('<<Drop>>', 处理文件拖拽)
    except Exception as e:
        print(f"拖拽功能初始化失败: {e}")
        拖拽可用 = False

按钮容器 = tk.Frame(tab1)
按钮容器.pack(pady=10)

def 后退():
    global 文件夹
    try:
        文件夹 = os.path.dirname(文件夹)
        当前文件夹.config(text=f'当前选择文件夹：{文件夹}')
        列出文件()
    except Exception as e:
        messagebox.showerror("错误",e)
def 删除():
    选中 = 文件列表.curselection()
    if 选中 == ():
        messagebox.showerror("错误","请选择列表内的文件")
        return
    选中内容 = [文件列表.get(i) for i in 选中]
    回复 = messagebox.askyesno("提示",f"是否删除选中内容？\n选中内容：{选中内容[0]}...")
    if 回复:
        for i in 选中内容:
            try:
                if os.path.isfile(Path(i)):
                    os.remove(Path(i))
                elif os.path.isdir(Path(i)):
                    shutil.rmtree(Path(i))
            except PermissionError as e:
                messagebox.showerror("错误","拒绝访问，可能是文件正在被使用")
                return
            except Exception as e:
                messagebox.showerror("错误",f"删除失败：{str(e)}")
                return
        messagebox.showinfo("提示","删除成功！")
        列出文件()
def 重命名():
    小窗 = tk.Toplevel(root)
    小窗.title("文件管理-重命名")
    小窗.geometry("400x400+650+250")
    小窗.grab_set()
    小窗.focus()
    文本容器 = tk.Frame(小窗)
    文本容器.pack(pady=5)
    文本 = tk.Label(文本容器,text="请输入修改内容：")
    文本.pack(side=tk.LEFT)
    文本框 = tk.Text(文本容器,width=40,height=1,font=("微软雅黑",9,"bold"))
    文本框.pack(side=tk.LEFT)
    按钮容器1 = tk.Frame(小窗)
    按钮容器1.pack(pady=5)
    def 重命名文件():
        新文件名 = 文本框.get("1.0",tk.END).strip()
        选中 = 文件列表1.curselection()
        if 选中 == ():
            messagebox.showerror("错误","请选择列表内的文件")
            return
        else:
            选中内容 = 文件列表1.get(选中[0])
        dir_path = os.path.dirname(选中内容)
        filename = os.path.basename(选中内容)
        name_without_ext, ext = os.path.splitext(filename)
        回答 = messagebox.askyesno("提示",f'是否将"{filename}"重命名为"{新文件名}{ext}"？')
        if 回答:
            try:
                new_filename = 新文件名 + ext
                new_path = os.path.join(dir_path, new_filename)
                old_path = os.path.join(文件夹, 选中内容)
                os.rename(old_path, new_path)
                messagebox.showinfo("提示","重命名成功~")
                所有项目 = 文件列表1.get(0,tk.END)
                a = 0
                found = False
                for i in 所有项目:
                    if i == old_path:
                        found = True
                        break
                    a += 1
                if found:
                    文件列表1.delete(a)
                    文件列表1.insert(a, str(new_path))
                列出文件()
            except Exception as e:
                messagebox.showerror("错误",f"重命名失败：{str(e)}")
    重命名文件按钮 = tk.Button(按钮容器1,text="重命名",command=重命名文件)
    重命名文件按钮.pack(side=tk.LEFT,padx=5)
    def 修改后缀名():
        新后缀名 = 文本框.get("1.0",tk.END).strip()
        if "." not in 新后缀名:
            新后缀名 = "." + 新后缀名
        提问 = 0
        回答 = messagebox.askyesno("提示",f'是否确认将以下列表内文件的后缀名修改为"{新后缀名}"？')
        if 回答:
            try:
                for 路径 in 文件列表1.get(0, tk.END):
                    if os.path.isdir(Path(路径)):
                        if 提问 == 0:
                            回复 = messagebox.askyesno("提示","检测到列表内有文件夹，是否继续？\n选择后本次操作再次遇到将不提问")
                            if 回复:
                                提问 = 1
                            else:
                                提问 = 2
                        if 提问 == 2:
                            continue
                    dir_path = os.path.dirname(路径)
                    filename = os.path.basename(路径)
                    name_without_ext, ext = os.path.splitext(filename)
                    new_filename = name_without_ext + 新后缀名
                    new_path = os.path.join(dir_path, new_filename)
                    old_path = os.path.join(文件夹, 路径)
                    os.rename(old_path, new_path)
                    所有项目 = 文件列表1.get(0,tk.END)
                    a = 0
                    found = False
                    for i in 所有项目:
                        if i == old_path:
                            found = True
                            break
                        a += 1
                    if found:
                        文件列表1.delete(a)
                        文件列表1.insert(a, str(new_path))
                messagebox.showinfo("提示","重命名成功~")
                列出文件()
            except Exception as e:
                messagebox.showerror("错误",f"重命名失败：{str(e)}")
    修改后缀名按钮 = tk.Button(按钮容器1,text="修改后缀名",command=修改后缀名)
    修改后缀名按钮.pack(side=tk.LEFT,padx=5)

    列表容器 = tk.Frame(小窗)
    列表容器.pack()
    条1 = tk.Scrollbar(列表容器)
    条1.pack(side=tk.RIGHT, fill=tk.Y)
    文件列表1 = tk.Listbox(列表容器,width=48,height=12)
    文件列表1.pack(side=tk.LEFT, fill=tk.Y)
    文件列表1.config(yscrollcommand=条1.set)
    条1.config(command=文件列表1.yview)

    选中 = 文件列表.curselection()
    if 选中 == ():
        小窗.destroy()
        messagebox.showerror("错误","请选择列表内的文件")
        return
    选中内容 = [文件列表.get(i) for i in 选中]
    for i in 选中内容:
        文件列表1.insert(tk.END,i)
def 进入文件夹():
    global 文件夹
    记录 = 文件夹
    try:
        选中 = 文件列表.curselection()
        if 选中 == ():
            messagebox.showerror("错误","请选择列表内的文件")
            return
        选中内容 = [文件列表.get(i) for i in 选中]
        if len(选中内容) > 1:
            messagebox.showerror("错误","只能选择一个文件夹打开")
            return
        选中内容 = 文件列表.get(选中[0])
        if os.path.isfile(Path(选中内容)):
            messagebox.showerror("错误","请选择文件夹")
            return
        文件夹 = os.path.join(文件夹,选中内容)
        当前文件夹.config(text=f'当前选择文件夹：{文件夹}')
        列出文件()
    except Exception as e:
        messagebox.showerror("错误",e)
        文件夹 = 记录
        当前文件夹.config(text=f'当前选择文件夹：{文件夹}')
        列出文件()
def 复制路径():
    global 文件夹
    选中 = 文件列表.curselection()
    if 选中 == ():
        root.clipboard_clear()
        root.clipboard_append(文件夹)
        return
    选中内容 = [文件列表.get(i) for i in 选中]
    if len(选中内容) > 1:
        messagebox.showerror("错误","只能选择一个路径")
        return
    选中内容 = 文件列表.get(选中[0])
    root.clipboard_clear()
    root.clipboard_append(选中内容)

刷新按钮 = tk.Button(按钮容器,text="刷新",width=10,height=2,font=("微软雅黑",9),command=列出文件)
刷新按钮.pack(side=tk.LEFT,padx=5)
删除按钮 = tk.Button(按钮容器,text="删除",width=10,height=2,font=("微软雅黑",9),command=删除)
删除按钮.pack(side=tk.LEFT,padx=5)
重命名按钮 = tk.Button(按钮容器,text="重命名",width=10,height=2,font=("微软雅黑",9),command=重命名)
重命名按钮.pack(side=tk.LEFT,padx=5)
进入文件夹按钮 =tk.Button(按钮容器,text="进入文件夹",width=12,height=2,font=("微软雅黑",9),command=进入文件夹)
进入文件夹按钮.pack(side=tk.LEFT,padx=5)
后退按钮 = tk.Button(按钮容器,text="后退",width=10,height=2,font=("微软雅黑",9),command=后退)
后退按钮.pack(side=tk.LEFT,padx=5)
复制路径按钮 = tk.Button(按钮容器,text="复制路径",width=10,height=2,font=("微软雅黑",9),command=复制路径)
复制路径按钮.pack(side=tk.LEFT,padx=5)

# ============ 第二个标签页：视频提取音频 ============
label2 = tk.Label(tab2,text="视频提取音频",font=("微软雅黑",11,"bold"),fg="black",pady=0)
label2.pack(pady=5)

# 说明文本
说明 = tk.Label(tab2,text="支持批量提取多个视频文件 | 使用多线程处理 | 界面不会卡顿",font=("微软雅黑",8),fg="gray")
说明.pack(pady=5)

# 视频文件列表
列表容器2 = tk.Frame(tab2)
列表容器2.pack(pady=5, fill=tk.X, padx=10)

# 左侧：文件列表
左侧容器 = tk.Frame(列表容器2)
左侧容器.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(左侧容器,text="待处理文件列表：",font=("微软雅黑",9,"bold")).pack(anchor=tk.W)

列表框容器 = tk.Frame(左侧容器)
列表框容器.pack(fill=tk.BOTH, expand=True)

条2 = tk.Scrollbar(列表框容器)
条2.pack(side=tk.RIGHT, fill=tk.Y)
视频文件列表 = tk.Listbox(列表框容器,width=40,height=12,selectmode="extended")
视频文件列表.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
视频文件列表.config(yscrollcommand=条2.set)
条2.config(command=视频文件列表.yview)

# 视频文件列表拖拽处理
def 处理视频拖拽(event):
    """处理拖拽到视频文件列表的文件"""
    data = event.data
    
    # 处理多个文件的格式
    files = []
    if data.startswith('{') and data.endswith('}'):
        # Windows格式的多文件路径: {path1} {path2}
        data = data[1:-1]
        files = [f.strip() for f in data.split('} {') if f.strip()]
    else:
        # 单个文件路径
        files = [data]

    for 文件路径 in files:
        文件路径 = 文件路径.strip()
        if 文件路径 and os.path.isfile(文件路径):
            # 检查是否为视频文件
            视频扩展名 = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.mpg']
            文件扩展名 = os.path.splitext(文件路径)[1].lower()
            if 文件扩展名 in 视频扩展名:
                # 检查是否已存在
                已存在 = False
                for i in range(视频文件列表.size()):
                    if 视频文件列表.get(i) == 文件路径:
                        已存在 = True
                        break
                if not 已存在:
                    视频文件列表.insert(tk.END, 文件路径)
            else:
                messagebox.showwarning("警告",f"文件 {os.path.basename(文件路径)} 不是支持的视频格式")

# 绑定拖拽事件到视频文件列表
if 拖拽可用:
    try:
        视频文件列表.drop_target_register(DND_FILES)
        视频文件列表.dnd_bind('<<Drop>>', 处理视频拖拽)
    except Exception as e:
        print(f"视频拖拽功能初始化失败: {e}")
        拖拽可用 = False

# 右侧：操作按钮
右侧容器 = tk.Frame(列表容器2)
右侧容器.pack(side=tk.RIGHT, padx=10)

def 选择视频文件():
    视频文件 = filedialog.askopenfilenames(
        title="选择视频文件（可多选）",
        filetypes=[
            ("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.mpeg"),
            ("所有文件", "*.*")
        ]
    )
    if 视频文件:
        for 文件 in 视频文件:
            # 检查是否已存在
            已存在 = False
            for i in range(视频文件列表.size()):
                if 视频文件列表.get(i) == 文件:
                    已存在 = True
                    break
            if not 已存在:
                视频文件列表.insert(tk.END, 文件)

选择视频按钮 = tk.Button(右侧容器,text="添加文件\n(可多选)",width=10,height=2,command=选择视频文件)
选择视频按钮.pack(pady=5)

def 清空列表():
    if not 提取任务队列.empty():
        回复 = messagebox.askyesno("提示","正在处理任务，确定要清空列表吗？")
        if not 回复:
            return
    视频文件列表.delete(0, tk.END)
    进度条.config(value=0)
    状态标签.config(text="就绪")

清空按钮 = tk.Button(右侧容器,text="清空列表",width=10,height=2,command=清空列表)
清空按钮.pack(pady=5)

def 删除选中():
    选中 = 视频文件列表.curselection()
    if 选中:
        # 从后往前删除，避免索引问题
        for i in reversed(选中):
            视频文件列表.delete(i)

删除选中按钮 = tk.Button(右侧容器,text="删除选中",width=10,height=2,command=删除选中)
删除选中按钮.pack(pady=5)

# 输出设置
设置容器 = tk.Frame(tab2)
设置容器.pack(pady=5)
tk.Label(设置容器,text="输出质量：",font=("微软雅黑",9,"bold")).pack(side=tk.LEFT)
质量变量 = tk.StringVar(value="标准")
质量选择 = ttk.Combobox(设置容器, textvariable=质量变量, values=["低", "标准", "高"], width=10, state="readonly")
质量选择.pack(side=tk.LEFT, padx=5)

# 线程设置
线程容器 = tk.Frame(tab2)
线程容器.pack(pady=5)
tk.Label(线程容器,text="同时处理数：",font=("微软雅黑",9,"bold")).pack(side=tk.LEFT)
线程数变量 = tk.StringVar(value="2")
线程选择 = ttk.Combobox(线程容器, textvariable=线程数变量, values=["1", "2", "3", "4"], width=5, state="readonly")
线程选择.pack(side=tk.LEFT, padx=5)

# 进度显示
进度容器 = tk.Frame(tab2)
进度容器.pack(pady=10, fill=tk.X, padx=10)
进度条 = ttk.Progressbar(进度容器, length=400, mode='determinate')
进度条.pack(fill=tk.X)
状态标签 = tk.Label(进度容器,text="就绪",font=("微软雅黑",8),fg="gray")
状态标签.pack(pady=5)

# 全局变量
提取任务队列 = queue.Queue()
正在运行 = False
停止标志 = False
成功数量 = 0
失败数量 = 0

def 提取单个视频(视频文件, 质量):
    """在单独线程中提取单个视频的音频"""
    global 停止标志

    if 停止标志:
        return False, "已停止"

    try:
        ffmpeg_path = "E:\\ffmpeg-8.0.1-essentials_build\\bin\\ffmpeg.exe"
        if not os.path.exists(ffmpeg_path):
            return False, "未找到FFmpeg"

        # 根据质量选择比特率
        if 质量 == "低":
            比特率 = "128k"
        elif 质量 == "高":
            比特率 = "320k"
        else:  # 标准
            比特率 = "192k"

        # 确定输出路径
        视频路径 = Path(视频文件)
        输出路径 = 视频路径.with_suffix('.mp3')

        command = [
            ffmpeg_path,
            "-i", 视频文件,
            "-vn",  # 不包含视频
            "-acodec", "libmp3lame",
            "-b:a", 比特率,
            "-ar", "44100",
            "-y",  # 覆盖输出文件
            str(输出路径)
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        process.wait()

        if process.returncode == 0:
            return True, str(输出路径)
        else:
            return False, "提取失败"

    except Exception as e:
        return False, str(e)

def 更新进度(当前完成, 总数, 成功, 失败):
    """更新进度条和状态"""
    if 总数 > 0:
        进度 = (当前完成 / 总数) * 100
        进度条.config(value=进度)
        状态标签.config(text=f"进度：{当前完成}/{总数} | 成功：{成功} | 失败：{失败}")

def 提取音频工作线程():
    """后台工作线程，处理提取任务"""
    global 正在运行, 停止标志, 成功数量, 失败数量

    质量 = 质量变量.get()
    线程数 = int(线程数变量.get())

    # 获取所有文件
    所有文件 = [视频文件列表.get(i) for i in range(视频文件列表.size())]
    总数 = len(所有文件)

    if not 所有文件:
        正在运行 = False
        root.after(0, lambda: 执行提取按钮.config(state=tk.NORMAL, text="开始提取"))
        root.after(0, lambda: 停止按钮.config(state=tk.DISABLED))
        return

    # 使用线程池处理
    with ThreadPoolExecutor(max_workers=线程数) as executor:
        futures = {executor.submit(提取单个视频, 文件, 质量): 文件 for 文件 in 所有文件}

        for future in futures:
            if 停止标志:
                break

            文件名 = futures[future]
            try:
                成功, 结果 = future.result()
                if 成功:
                    成功数量 += 1
                    root.after(0, lambda f=文件名: 状态标签.config(text=f"完成：{Path(f).name}"))
                else:
                    失败数量 += 1
                    root.after(0, lambda f=文件名, r=结果: 状态标签.config(text=f"失败：{Path(f).name} - {r}"))
            except Exception as e:
                失败数量 += 1
                root.after(0, lambda f=文件名, r=str(e): 状态标签.config(text=f"错误：{Path(f).name} - {r}"))

            # 使用回调函数更新进度，传递当前状态
            当前完成 = 成功数量 + 失败数量
            def 更新进度_callback():
                更新进度(当前完成, 总数, 成功数量, 失败数量)
            root.after(0, 更新进度_callback)

    # 完成
    正在运行 = False
    停止标志 = False

    root.after(0, lambda: 执行提取按钮.config(state=tk.NORMAL, text="开始提取"))
    root.after(0, lambda: 停止按钮.config(state=tk.DISABLED))

    当前完成 = 成功数量 + 失败数量
    更新进度(当前完成, 总数, 成功数量, 失败数量)

    # 确保进度条显示100%
    root.after(0, lambda: 进度条.config(value=100))

    最终状态 = f"完成！成功：{成功数量} | 失败：{失败数量}"
    root.after(0, lambda: 状态标签.config(text=最终状态))
    root.after(100, lambda: messagebox.showinfo("完成", 最终状态))

def 开始提取():
    """开始批量提取"""
    global 正在运行, 停止标志, 成功数量, 失败数量

    if 视频文件列表.size() == 0:
        messagebox.showerror("错误", "请先添加视频文件！")
        return

    if 正在运行:
        return

    正在运行 = True
    停止标志 = False
    成功数量 = 0
    失败数量 = 0

    执行提取按钮.config(state=tk.DISABLED, text="处理中...")
    停止按钮.config(state=tk.NORMAL)

    # 启动后台工作线程
    thread = threading.Thread(target=提取音频工作线程, daemon=True)
    thread.start()

def 停止提取():
    """停止提取"""
    global 停止标志
    停止标志 = True
    状态标签.config(text="正在停止...")

# 按钮容器
按钮容器2 = tk.Frame(tab2)
按钮容器2.pack(pady=10)

执行提取按钮 = tk.Button(按钮容器2,text="开始提取",font=("微软雅黑",10,"bold"),bg="#3ECACF",fg="white",width=15,height=2,command=开始提取)
执行提取按钮.pack(side=tk.LEFT, padx=10)

停止按钮 = tk.Button(按钮容器2,text="停止",font=("微软雅黑",10,"bold"),bg="#FF6B6B",fg="white",width=10,height=2,command=停止提取, state=tk.DISABLED)
停止按钮.pack(side=tk.LEFT, padx=10)

# 提示信息
提示 = tk.Label(tab2,text="提示：\n1. 支持同时选择多个视频文件\n2. 提取后的MP3文件将保存在视频文件的同一目录下\n3. 使用多线程处理，界面不会卡顿",font=("微软雅黑",8),fg="gray",justify=tk.LEFT)
提示.pack(pady=5)

# ============ 版权信息 ============
版权 = tk.Label(root,text="© 2026 耶y 版权所有",font=("微软雅黑",7,"bold"),fg="gray",pady=0)
版权.pack()

root.mainloop()