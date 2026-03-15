import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import random
import subprocess
import os, sys
import threading
import pyautogui
import time
import ctypes

root = tk.Tk()
root.title("耶y工具箱")
canvas = tk.Canvas(root,width=0,height=0,bg='white')
canvas.pack()

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both', padx=10, pady=10)
文本标签 = ttk.Frame(notebook)
notebook.add(文本标签, text='文本编辑')
功能标签 = ttk.Frame(notebook)
notebook.add(功能标签, text='功能')
日志标签 = ttk.Frame(notebook)
notebook.add(日志标签, text='日志')

notebook.bind("<<NotebookTabChanged>>", lambda e: root.title("耶y工具箱 - " + notebook.tab(notebook.select(),"text")))

APP_ID = "耶y工具箱_1.5.1.0000"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
try:
    root.iconbitmap("E:\\Python\\工具箱图标.ico")
    图标方式 = 1
except:
    try:
        临时目录 = sys._MEIPASS
        图标路径 = os.path.join(临时目录, "工具箱图标.ico\\工具箱图标.ico")
        root.iconbitmap(图标路径)
        图标方式 = 2
    except:
        print("图标加载失败")
        图标方式 = 0

label_frame = tk.Frame(文本标签)
label_frame.pack()

label = tk.Label(label_frame,text="欢迎使用耶y工具箱",font=("微软雅黑",10,"bold"),fg="black",pady=0)
label.pack()

text_frame = tk.Frame(文本标签)
text_frame.pack()

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text = tk.Text(text_frame,font=("Consolas",12),width=50,height=10,bg="#f0f0f0",fg="black",padx=10,pady=10,yscrollcommand=scrollbar.set)
text.pack(fill=tk.X,padx=20,pady=5,expand=True)
root.geometry("530x401+500+270")
text.tag_configure("red",foreground="red")
text.tag_configure("浅蓝色",foreground="#5A96DB")
scrollbar.config(command=text.yview)

日志容器 = tk.Frame(日志标签)
日志容器.pack()
日志条 = tk.Scrollbar(日志容器)
日志条.pack(side=tk.RIGHT, fill=tk.Y)
日志文本 = tk.Text(日志容器,width=62,height=23,bg="#f0f0f0",fg="black",padx=10,pady=10,yscrollcommand=日志条.set)
日志文本.pack(fill=tk.X,padx=20,pady=5,expand=True)
日志条.config(command=日志文本.yview)

记录 = {"记录": "","状态": 0,"随机数": {0:"",1:""},"添符": "","替换": {0:"",1:""},"合成": "","Unicode":"","utf8":"","显示":0,"关机":{"方式":"","时间":0,"强制":False,"直接":""},"小窗":False}
def 恢复():
    global 记录
    记录["状态"] = 0
    记录["随机数"] = {0:"",1:""}
    记录["添符"] = ""
    记录["替换"] = {0:"",1:""}
    记录["合成"] = ""
    记录["Unicode"] = ""
    记录["utf8"] = ""
    记录["关机"] = {"方式":"","时间":0,"强制":False,"直接":""}
    label.config(text="欢迎使用耶y工具箱",font=("微软雅黑",10,"bold"),fg="black",bg="#f0f0f0")
    随机数按钮.config(fg="black")
    添符按钮.config(fg="black")
    替换按钮.config(fg="black")
    合成按钮.config(fg="black")
    Unicode按钮.config(fg="black")
    utf8按钮.config(fg="black")
    关机按钮.config(fg="black")
def 运行命令(命令,callback,任务名称="任务"):
    开始时间 = time.time()
    磁盘清理按钮.config(state=tk.DISABLED)
    清理临时文件按钮.config(state=tk.DISABLED)
    查看磁盘按钮.config(state=tk.DISABLED)
    查看存储按钮.config(state=tk.DISABLED)
    关机按钮.config(state=tk.DISABLED)
    查看附近ip按钮.config(state=tk.DISABLED)
    激活win按钮.config(state=tk.DISABLED)
    暂停更新按钮.config(state=tk.DISABLED)
    if 命令 == "irm https://get.activated.win | iex":
        超时 = 1000
    else:
        超时 = 30
    def worker():
        global 记录
        try:
            result = subprocess.run(
                ["powershell","-Command",命令],capture_output=True,
                text=True,
                encoding='gbk',
                errors='ignore',
                timeout=超时
            )
            结束时间 = time.time()
            耗时 = 结束时间 - 开始时间
            日志信息 = f"[{time.strftime('%H:%M:%S')}] {任务名称} (耗时: {耗时:.3f}秒)\n"
            日志文本.after(0, lambda: 添加日志(日志信息))
            root.after(0, callback, result.stdout, result.returncode, None)
        except subprocess.TimeoutExpired as e:
            error_msg = f"[{time.strftime('%H:%M:%S')}] 错误: 命令执行超时 {任务名称} - {str(e)}\n"
            日志文本.after(0, lambda: 添加日志(error_msg))
            root.after(0, callback, "", 1, "命令执行超时")
        except Exception as e:
            error_msg = f"[{time.strftime('%H:%M:%S')}] 错误: [{e}] {任务名称} - {str(e)}\n"
            日志文本.after(0, lambda: 添加日志(error_msg))
            root.after(0, callback, "", 1, f"错误: {str(e)}")
        finally:
            root.after(0, 启用按钮)
    def 启用按钮():
        磁盘清理按钮.config(state=tk.NORMAL)
        清理临时文件按钮.config(state=tk.NORMAL)
        查看磁盘按钮.config(state=tk.NORMAL)
        查看存储按钮.config(state=tk.NORMAL)
        关机按钮.config(state=tk.NORMAL)
        查看附近ip按钮.config(state=tk.NORMAL)
        激活win按钮.config(state=tk.NORMAL)
        暂停更新按钮.config(state=tk.NORMAL)
    threading.Thread(target=worker, daemon=True).start()

def 提取():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    记录["记录"] = 文本
    text.delete("1.0",tk.END)
    for symbol in 文本:
        text.insert(tk.END,str(symbol) + "\n")
def 清空():
    global 记录
    文本 = text.get("1.0",tk.END)
    记录["记录"] = 文本
    text.delete("1.0",tk.END)
    恢复()
def 撤销():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    text.delete("1.0",tk.END)
    text.insert(tk.END,记录["记录"])
    记录["记录"] = 文本
def 随机数():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    if 记录["状态"] == 0:
        记录["记录"] = 文本
        随机数按钮.config(fg="#6168D1")
    记录["状态"] += 1
    if 记录["状态"] == 1:
        label.config(text="随机数生成：请输入第一个数字，再按一次按钮",bg="#6168D1")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 2:
        记录["随机数"][0] = 文本
        label.config(text="随机数生成：请输入第二个数字，再按一次按钮",bg="#6168D1")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 3:
        记录["随机数"][1] = 文本
        label.config(text="随机数生成：请输入1:随机整数2:随机小数，再按一次按钮",bg="#6168D1")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 4:
        try:
            随机数 = 记录["随机数"]
            if 文本.strip() == "1":
                if int(随机数[0]) <= int(随机数[1]):
                    数字 = random.randint(int(随机数[0]),int(随机数[1]))
                else:
                    数字 = random.randint(int(随机数[1]),int(随机数[0]))
            elif 文本.strip() == "2":
                if float(随机数[0]) <= float(随机数[1]):
                    数字 = random.uniform(float(随机数[0]),float(随机数[1]))
                else:
                    数字 = random.uniform(float(随机数[1]),float(随机数[0]))
            else:
                raise ValueError ("请检查输入内容是否正确")
            text.delete("1.0",tk.END)
            text.insert(tk.END,f"随机数生成：{随机数[0]}~{随机数[1]}\n{数字}","浅蓝色")
            恢复()
        except Exception as e:
            恢复()
            label.config(text=f"错误：{str(e)}",bg="red")
            text.delete("1.0",tk.END)
            text.insert(tk.END,f"错误：{str(e)}","red")
    else:
        text.delete("1.0",tk.END)
        text.insert(tk.END,"当前处于其他状态，已取消，请再按一次按钮")
        恢复()
def 添符():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    if 记录["状态"] == 0:
        记录["记录"] = 文本
        记录["状态"] = 4
        添符按钮.config(fg="#4B8F14")
    记录["状态"] += 1
    if 记录["状态"] == 5:
        label.config(text="添符：请输入原文本，然后再按一次按钮",bg="#91DF51")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 6:
        label.config(text="添符：请输入要添加的符号，再按一次按钮完成",bg="#91DF51")
        记录["添符"] = 文本
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 7:
        text.delete("1.0",tk.END)
        for i in range(len(记录["添符"])):
            text.insert(tk.END,f"{记录['添符'][i]}{文本}","浅蓝色")
        恢复()
    else:
        text.delete("1.0",tk.END)
        text.insert(tk.END,"当前处于其他状态，已取消，请再按一次按钮")
        恢复()
def 替换():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    if 记录["状态"] == 0:
        记录["状态"] = 7
        记录["记录"] = 文本
        替换按钮.config(fg="#671C85")
    记录["状态"] += 1
    if 记录["状态"] == 8:
        label.config(text="替换：请输入原文本，然后再按一次按钮",bg="#A63DCF")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 9:
        label.config(text="替换：请输入要替换的内容，然后再按一次按钮",bg="#A63DCF")
        text.delete("1.0",tk.END)
        记录["替换"][0] = 文本
    elif 记录["状态"] == 10:
        label.config(text="替换：请输入替换成的内容，然后再按一次按钮",bg="#A63DCF")
        text.delete("1.0",tk.END)
        记录["替换"][1] = 文本
    elif 记录["状态"] == 11:
        text.delete("1.0",tk.END)
        替换内容 = 记录["替换"]
        被改内容表 = list(替换内容[1])
        新词 = ""
        for 字符 in 替换内容[0]:
            if 字符 in 被改内容表:
                新词 += 文本
            else:
                新词 += 字符
        text.insert(tk.END,f"{新词}","浅蓝色")
        恢复()
    else:
        text.delete("1.0",tk.END)
        text.insert(tk.END,"当前处于其他状态，已取消，请再按一次按钮")
        恢复()
def 合成():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    if 记录["状态"] == 0:
        记录["状态"] = 11
        记录["记录"] = 文本
        合成按钮.config(fg="#858D10")
    记录["状态"] += 1
    if 记录["状态"] == 12:
        label.config(text="合成：请输入原文本，然后再按一次按钮(用法：输入Z和 ̀ ̄ ̂ ̐等 → Z̥͉͍̈́́̀̀̄̂̐̌̇͂͊͋̋̓̂̄)",bg="#BAC519")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 13:
        label.config(text="合成：请输入多个内容，然后再按一次按钮",bg="#BAC519")
        text.delete("1.0",tk.END)
        记录["合成"] = 文本
    elif 记录["状态"] == 14:
        text.delete("1.0",tk.END)
        合成列表 = []
        合成列表.extend(文本.split())
        结果 = f'{记录["合成"]}' + ''.join(合成列表)
        text.insert(tk.END,f"{结果}","浅蓝色")
        恢复()
    else:
        text.delete("1.0",tk.END)
        text.insert(tk.END,"当前处于其他状态，已取消，请再按一次按钮")
        恢复()
def Unicode():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    if 记录["状态"] == 0:
        记录["状态"] = 14
        记录["记录"] = 文本
        Unicode按钮.config(fg="#5F108D")
    记录["状态"] += 1
    if 记录["状态"] == 15:
        label.config(text="Unicode转化：请输入1:文本→Uni,2:Uni→文本，然后再按一次按钮",bg="#9D3CD6")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 16:
        label.config(text="Unicode转化：请输入要转化的内容，然后再按一次按钮",bg="#9D3CD6")
        text.delete("1.0",tk.END)
        if 文本 == "1" or 文本 == "2":
            记录["Unicode"] = 文本
        else:
            恢复()
            text.delete("1.0",tk.END)
            text.insert(tk.END,"错误：请输入1或2","red")
    elif 记录["状态"] == 17:
        text.delete("1.0",tk.END)
        if 记录["Unicode"] == "1":
            结果 = ""
            for c in 文本:
                code = ord(c)
                if code <= 0xFFFF:
                    结果 += fr'\u{code:04X}'
                else:
                    结果 += fr'\U{code:08X}'
            text.insert(tk.END,f"{结果}","浅蓝色")
        else:
            unicode_str = r''.join(文本)
            try:
                decoded = bytes(unicode_str, 'utf-8').decode('unicode-escape')
                text.insert(tk.END,f"{decoded}","浅蓝色")
            except UnicodeDecodeError:
                text.insert(tk.END,"转换失败：请输入正确的Unicode格式(如\\u4F60或\\U0001F602)","red")
                恢复()
        恢复()
    else:
        text.delete("1.0",tk.END)
        text.insert(tk.END,"当前处于其他状态，已取消，请再按一次按钮")
        恢复()
def utf8():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    if 记录["状态"] == 0:
        记录["状态"] = 17
        记录["记录"] = 文本
        utf8按钮.config(fg="#8D1063")
    记录["状态"] += 1
    if 记录["状态"] == 18:
        label.config(text="utf-8转化：请输入1:文本→utf-8,2:utf-8→文本，然后再按一次按钮",bg="#D8219B")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 19:
        label.config(text="utf-8转化：请输入要转化的内容，然后再按一次按钮",bg="#D8219B")
        text.delete("1.0",tk.END)
        if 文本 == "1" or 文本 == "2":
            记录["utf8"] = 文本
        else:
            恢复()
            text.delete("1.0",tk.END)
            text.insert(tk.END,"错误：请输入1或2","red")
    elif 记录["状态"] == 20:
        try:
            text.delete("1.0",tk.END)
            if 记录["utf8"] == "1":
                结果 = 文本.encode("utf-8")
                text.insert(tk.END,f"{结果}","浅蓝色")
            else:
                if 文本.startswith("b'") or 文本.startswith('b"'):
                    byte_data = eval(文本)
                    if not isinstance(byte_data, bytes):
                        raise ValueError("输入的不是有效的字节表示")
                    结果 = byte_data.decode('utf-8')
                    text.insert(tk.END,f"{结果}","浅蓝色")
                elif all(c in '0123456789abcdefxABCDEFX\\' for c in 文本):
                    clean_input = 文本.replace('\\x', '').replace('\\', '')
                    byte_data = bytes.fromhex(clean_input)
                    结果 = byte_data.decode('utf-8')
                    text.insert(tk.END,f"{结果}","浅蓝色")
                else:
                    text.insert(tk.END,"错误：输入格式无效。请使用以下格式：\n1. 带 b 前缀的字节表示：b'\\xe3\\x80\\x82'\n2. 十六进制代码：e38082","red")
            恢复()
        except ValueError as e:
            text.insert(tk.END,f"错误：{str(e)}","red")
            恢复()
        except UnicodeDecodeError:
            text.insert(tk.END,"错误：请输入正确utf-8格式","red")
            恢复()
        except Exception as e:
            text.insert(tk.END,f"错误：{str(e)}","red")
            恢复()
    else:
        text.delete("1.0",tk.END)
        text.insert(tk.END,"当前处于其他状态，已取消，请再按一次按钮")
        恢复()
def 获取字数():
    列表 = []
    文本 = text.get("1.0",tk.END)
    for i in 文本:
        列表.append(i)
    换行空格数,字数 = -1,0
    for i in 文本:
        if i == "\n" or i == " ":
            换行空格数 += 1
        else:
            字数 += 1
    label.config(text=f"字数获取：共{字数}字,换行符+空格{换行空格数}个",bg="#D6683C")

def 清理临时文件():
    回答 = messagebox.askyesno("提示","是否清理临时文件？\n（Temp内的所有文件）")
    if not 回答:
        return
    命令 = r"""
    Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "C:\Users\ye\AppData\Local\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
    """
    def 清理回调(输出, 返回码, 错误=None):
        if 输出.strip() == "" and not 错误:
            返回码 = 0
        if 错误:
            messagebox.showerror("错误", f"清理失败：{错误}")
        elif 返回码 == 0:
            messagebox.showinfo("清理临时文件", "临时文件清理成功~")
        else:
            messagebox.showwarning("警告",f"清理完成，但有警告：\n{输出}")
    运行命令(命令, 清理回调, "清理临时文件")
def 查看磁盘使用情况():
    def 磁盘回调(输出, 返回码, 错误=None):
        if 错误:
            messagebox.showerror("错误", f"获取失败：{错误}")
        else:
            messagebox.showinfo("查看磁盘使用情况", f"{输出}")
    运行命令("Get-PSDrive -PSProvider FileSystem", 磁盘回调, "查看磁盘使用")
def 查看存储():
    def 存储回调(输出, 返回码, 错误=None):
        if 错误:
            messagebox.showerror("错误", f"打开失败：{错误}")
    运行命令("start ms-settings:storagesense", 存储回调, "查看存储")
def 关机():
    global 记录
    文本 = text.get("1.0",tk.END).strip()
    if 记录["状态"] == 0:
        记录["状态"] = 20
        记录["记录"] = 文本
        关机按钮.config(fg="#46108D")
    记录["状态"] += 1
    if 记录["状态"] == 21:
        label.config(text="关机/重启：请输入1:关机2:重启3:取消4:取消其他电脑，然后再按一次按钮",bg="#6F1FD8")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 22:
        if 文本 == "3":
            subprocess.run("shutdown -a")
            text.delete("1.0",tk.END)
            text.insert(tk.END,"成功取消关机~","浅蓝色")
            恢复()
        elif 文本 == "1":
            记录["关机"]["方式"] = "关机"
            label.config(text="关机/重启：是否强制关机/重启？1：是，其他：否",bg="#6F1FD8")
            text.delete("1.0",tk.END)
        elif 文本 == "2":
            记录["关机"]["方式"] = "重启"
            label.config(text="关机/重启：是否强制关机/重启？1：是，其他：否",bg="#6F1FD8")
            text.delete("1.0",tk.END)
        elif 文本 == "4":
            记录["关机"]["方式"] = "取消"
            label.config(text="关机/重启：请输入电脑名称，然后再按一次按钮（取消）",bg="#6F1FD8")
            text.delete("1.0",tk.END)
            记录["状态"] = 24
        else:
            text.delete("1.0",tk.END)
            text.insert(tk.END,"请选择其中一个","red")
            恢复()
    elif 记录['状态'] == 23:
        if 文本 == "1":
            记录["关机"]['强制'] = True
        label.config(text="关机/重启：请输入关机时间(整数)（0是直接关机），然后再按一次按钮",bg="#6F1FD8")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 24:
        try:
            时间 = int(文本)
            if 时间 < 0:
                raise ValueError ("请输入大于等于0的整数")
            记录["关机"]["时间"] = 时间
            label.config(text="关机/重启：请输入1:直接关机，电脑名称:指定电脑关机，然后再按一次按钮",bg="#6F1FD8")
            text.delete("1.0",tk.END)
        except ValueError as e:
            text.delete("1.0",tk.END)
            text.insert(tk.END,f"错误：{str(e)}","red")
            恢复()
    elif 记录["状态"] == 25:
        if 文本 == "1":
            记录["关机"]["直接"] = "1"
        label.config(text="关机/重启：请输入附带的提示消息（不输入就无）",bg="#6F1FD8")
        text.delete("1.0",tk.END)
    elif 记录["状态"] == 26:
        try:
            text.delete("1.0",tk.END)
            if 文本 == "":
                信息 = ""
            else:
                信息 = f' /c "{文本}"'
            if 记录["关机"]["方式"] == "取消":
                命令 = f"shutdown /a /m \\\\{文本}{信息}"
                结果 = subprocess.run(
                    ["powershell","-Command",命令],capture_output=True,
                    text=True,
                    encoding='gbk',
                    errors='ignore'
                )
                if 结果.stdout.strip() == "":
                    text.insert(tk.END,f"执行结果：\n{结果.stderr}","red")
                else:
                    text.insert(tk.END,f"执行结果：\n{结果.stdout}","浅蓝色")
            else:
                其他 = " "
                if 记录["关机"]['强制'] == True:
                    其他 = " /f "
                时间 = 记录["关机"]["时间"]
                if 记录["关机"]["直接"] == "1":
                    if 记录["关机"]["方式"] == "关机":
                        subprocess.run(f"shutdown /s{其他}/t {时间}{信息}")
                    elif 记录["关机"]["方式"] == "重启":
                        subprocess.run(f"shutdown /r{其他}/t {时间}{信息}")
                    text.insert(tk.END,"已执行shutdown命令","浅蓝色")
                else:
                    if 记录["关机"]["方式"] == "关机":
                        临时记录 = "s"
                    elif 记录["关机"]["方式"] == "重启":
                        临时记录 = "r"
                    命令 = f"shutdown /{临时记录} /m \\\\{文本}{其他}/t {时间}{信息}"
                    结果 = subprocess.run(
                        ["powershell","-Command",命令],capture_output=True,
                        text=True,
                        encoding='gbk',
                        errors='ignore'
                    )
                    if 结果.stdout.strip() == "":
                        text.insert(tk.END,f"执行结果：\n{结果.stderr}","red")
                    else:
                        text.insert(tk.END,f"执行结果：\n{结果.stdout}","浅蓝色")
            恢复()
        except Exception as e:
            text.delete("1.0",tk.END)
            text.insert(tk.END,f"错误：{str(e)}","red")
            messagebox.showerror("错误",f"关机/重启失败\n{str(e)}")
            恢复()
    else:
        text.delete("1.0",tk.END)
        text.insert(tk.END,"当前处于其他状态，已取消，请再按一次按钮")
        恢复()
def 复制():
    global 记录,图标方式
    文本 = text.get("1.0", tk.END).strip()
    root.clipboard_clear()
    root.clipboard_append(文本)
    小窗 = tk.Toplevel(root)
    小窗.title("耶y工具箱")
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    x = root_x + 100
    y = root_y + 100
    小窗.geometry(f"150x60+{x}+{y}")
    小窗.resizable(False, False)
    小窗文本 = tk.Label(小窗,text="复制成功~")
    小窗文本.pack()
    if 图标方式 == 1:
        小窗.iconbitmap("E:\\Python\\工具箱图标.ico")
    elif 图标方式 == 2:
        临时目录 = sys._MEIPASS
        图标路径 = os.path.join(临时目录, "工具箱图标.ico\\工具箱图标.ico")
        小窗.iconbitmap(图标路径)
    root.after(500, 小窗.destroy)
def 查看附近ip():
    text.delete("1.0",tk.END)
    text.insert(tk.END,"正在查看附近ip...(时间较长)","浅蓝色")
    def 存储回调(输出, 返回码, 错误=None):
        if 错误:
            messagebox.showerror("错误", f"查看失败：{错误}")
            text.delete("1.0", tk.END)
            text.insert(tk.END, f"错误信息：{错误}", "red")
        else:
            text.delete("1.0", tk.END)
            text.insert(tk.END, f"附件ip：{输出}", "浅蓝色")
            小窗 = tk.Toplevel()
            小窗.title("查看附近ip")
            小窗.geometry("450x400")
            条 = tk.Scrollbar(小窗)
            条.pack(side=tk.RIGHT, fill=tk.Y)
            提示 = tk.Text(小窗,width=450,height=400,yscrollcommand=条.set)
            提示.pack()
            提示.insert(tk.END,f"{输出}")
            if 图标方式 == 1:
                小窗.iconbitmap("E:\\Python\\图标.ico")
            elif 图标方式 == 2:
                临时目录 = sys._MEIPASS
                图标路径 = os.path.join(临时目录, "图标.ico\\图标.ico")
                小窗.iconbitmap(图标路径)
            条.config(command=提示.yview)
    命令 = """
    ping 192.168.1.255
    arp -a
    """
    运行命令(命令, 存储回调, "查看附近ip")
def 窗口控制台函数():
    global 记录
    添加日志(f"[{time.strftime('%H:%M:%S')}] 打开了 窗口控制台")
    窗口控制台 = tk.Toplevel()
    窗口控制台.title("窗口控制台")
    窗口控制台.geometry("400x300")
    if 图标方式 == 1:
        窗口控制台.iconbitmap("E:\\Python\\图标.ico")
    elif 图标方式 == 2:
        临时目录 = sys._MEIPASS
        图标路径 = os.path.join(临时目录, "图标.ico\\图标.ico")
        窗口控制台.iconbitmap(图标路径)
    文本 = tk.Label(窗口控制台,text="窗口控制台",font=("微软雅黑",10,"bold"),fg="black",pady=0)
    文本.pack()
    文本框框架 = tk.Frame(窗口控制台)
    文本框框架.pack()
    条子 = tk.Scrollbar(文本框框架)
    条子.pack(side=tk.RIGHT, fill=tk.Y)
    文本框 = tk.Text(文本框框架,width=50,height=5,yscrollcommand=条子.set)
    文本框.pack(pady=10)
    条子.config(command=文本框.yview)
    框架 = tk.Frame(窗口控制台,pady=10)
    框架.pack()
    窗口状态 = False
    def 创建窗口():
        global 窗口
        nonlocal 窗口状态
        if 窗口状态 == False:
            窗口 = tk.Toplevel(窗口控制台)
            窗口.title("自定义窗口")
            窗口.geometry("200x200")
            def 窗口关闭事件(event):
                nonlocal 窗口状态
                窗口状态 = False
            窗口.bind("<Destroy>", 窗口关闭事件)
            窗口状态 = True
        else:
            messagebox.showerror("错误", "窗口已创建")
    def 设置标题():
        nonlocal 窗口状态
        if 窗口状态 == True:
            标题 = 文本框.get("1.0",tk.END).strip()
            窗口.title(标题)
        else:
            messagebox.showerror("错误","窗口还未创建")
    def 设置大小():
        nonlocal 窗口状态
        try:
            if 窗口状态 == True:
                大小 = 文本框.get("1.0",tk.END).strip()
                窗口.geometry(大小)
            else:
                messagebox.showerror("错误","窗口还未创建")
        except Exception as e:
            messagebox.showerror("错误",f"格式：数字x数字\n{str(e)}")
    def 运行py代码():
        try:
            输入 = 文本框.get("1.0",tk.END).strip()
            exec(输入)
        except Exception as e:
            messagebox.showerror("错误",e)
    创建窗口按钮 = tk.Button(框架,text="创建窗口",width=10,fg="black",command=创建窗口)
    创建窗口按钮.pack(side=tk.LEFT,padx=5)
    设置标题按钮 = tk.Button(框架,text="设置标题",width=10,fg="black",command=设置标题)
    设置标题按钮.pack(side=tk.LEFT,padx=5)
    设置大小按钮 = tk.Button(框架,text="设置窗口大小",width=10,fg="black",command=设置大小)
    设置大小按钮.pack(side=tk.LEFT,padx=5)
    运行代码按钮 = tk.Button(框架,text="运行py代码",width=10,fg="black",command=运行py代码)
    运行代码按钮.pack(side=tk.LEFT,padx=5)
    框架1 = tk.Frame(窗口控制台,pady=10)
    框架1.pack()
    def 清空文字():
        文本框.delete("1.0", tk.END)
    def 帮助():
        帮助窗口 = tk.Toplevel(窗口控制台)
        帮助窗口.title("帮助")
        帮助窗口.geometry("400x400")
        if 图标方式 == 1:
            帮助窗口.iconbitmap("E:\\Python\\图标.ico")
        elif 图标方式 == 2:
            临时目录 = sys._MEIPASS
            图标路径 = os.path.join(临时目录, "图标.ico\\图标.ico")
            帮助窗口.iconbitmap(图标路径)
        条 = tk.Scrollbar(帮助窗口)
        条.pack(side=tk.RIGHT, fill=tk.Y)
        帮助提示 = tk.Text(帮助窗口,width=400,height=400,yscrollcommand=条.set)
        帮助提示.pack()
        帮助提示.tag_configure("浅蓝色",foreground="#5A96DB")
        帮助提示.tag_configure("orange",foreground="orange")
        帮助提示.insert(tk.END,"\n变量：窗口\n\n创建文本：\n")
        帮助提示.insert(tk.END,'global 文本\n文本 = tk.Label(窗口,text="文本默认内容",font=("微软雅黑",10,"bold"),fg="black",pady=0)\n文本.pack()\n',"浅蓝色")
        帮助提示.insert(tk.END,"\n更改文本内容：\n")
        帮助提示.insert(tk.END,'文本.config(text="更改后的内容")\n',"浅蓝色")
        帮助提示.insert(tk.END,"\n创建文本框：\n")
        帮助提示.insert(tk.END,'global 文本框\n文本框 = tk.Text(窗口,fg="black",width=宽度,height=高度)\n文本框.pack(padx=左右间距,pady=上下间距)\n',"浅蓝色")
        帮助提示.insert(tk.END,"\n创建按钮：\n")
        帮助提示.insert(tk.END,'global 按钮,执行操作\ndef 执行操作():\n    执行的操作（如修改文本）\n按钮 = tk.Button(窗口,text="按钮上的文本",command=执行操作)\n按钮.pack()\n',"浅蓝色")
        帮助提示.insert(tk.END,"\n\n按钮介绍：\n 创建窗口：创建一个窗口（只控制最后创建的那个窗口，建议只创建一个）\n 设置标题：在文本框内输入标题，然后按按钮\n 设置窗口大小：在文本框输入axb（中间的是字母x），然后按一次按钮\n 运行py代码：在文本框内输入python代码，然后按按钮执行（不会可以叫ai或查资料，记得使用global）\n 创建框架：在文本框内输入要创建的框架名，然后按一次按钮一键生成Frame\n","orange")
        条.config(command=帮助提示.yview)
    def 创建框架():
        nonlocal 窗口状态
        try:
            if 窗口状态 == True:
                框架名 = 文本框.get("1.0",tk.END).strip()
                exec(f'global {框架名}\n{框架名} = tk.Frame(窗口)\n{框架名}.pack()')
            else:
                messagebox.showerror("错误","窗口还未创建")
        except Exception as e:
            if str(e) == "invalid syntax (<string>, line 1)":
                e = "请在文本框内输入框架名\n" + str(e)
            messagebox.showerror("错误",e)
    def 设置图标():
        nonlocal 窗口状态
        if 窗口状态 == True:
            图标文件 = filedialog.askopenfilename(
                title="选择图标文件",
                filetypes=[
                    ("图片文件", "*.ico *.png"),
                ]
            )
            if 图标文件:
                print("成功选择图标文件")
                try:
                    窗口.iconbitmap(图标文件)
                except Exception as e:
                    messagebox.showerror("错误",f"图标文件未找到/窗口未创建\n{e}")
        else:
            messagebox.showerror("错误","你还未创建窗口")
    清空文字按钮 = tk.Button(框架1,text="清空",width=10,fg="red",command=清空文字)
    清空文字按钮.pack(side=tk.LEFT,padx=5)
    帮助按钮 = tk.Button(框架1,text="帮助",width=10,fg="orange",command=帮助)
    帮助按钮.pack(side=tk.LEFT,padx=5)
    信息 = tk.Label(窗口控制台,text="变量：\n窗口：tk.Toplevel",font=("微软雅黑",10,"bold"),fg="orange",pady=0)
    信息.pack()
    创建框架按钮 = tk.Button(框架1,text="创建框架",width=10,fg="black",command=创建框架)
    创建框架按钮.pack(side=tk.LEFT,padx=5)
    设置图标按钮 = tk.Button(框架1,text="设置图标",width=10,fg="black",command=设置图标)
    设置图标按钮.pack(side=tk.LEFT,padx=5)
def 激活win():
    回答 = messagebox.askyesno("提示","是否激活windows？\n加载时如果询问请选“是”\n加载好后输入1激活windows~")
    if not 回答:
        return
    def 存储回调(输出, 返回码, 错误=None):
        if 错误:
            messagebox.showerror("错误", f"打开失败：{错误}")
    命令 = "irm https://get.activated.win | iex"
    运行命令(命令, 存储回调, "激活windows")

def 下一页():
    global 记录
    if 记录["显示"] == 0:
        提取按钮.pack_forget()
        随机数按钮.pack_forget()
        添符按钮.pack_forget()
        替换按钮.pack_forget()
        合成按钮.pack_forget()
        获取字数按钮.pack_forget()
        Unicode按钮.pack(side=tk.LEFT,padx=5)
        utf8按钮.pack(side=tk.LEFT,padx=5)
        下一页按钮.config(text="上一页")
        下一页按钮.pack_forget()
        下一页按钮.pack(side=tk.LEFT,padx=5)
        关机按钮.pack(side=tk.LEFT,padx=5)
        记录["显示"] = 1
    elif 记录["显示"] == 1:
        提取按钮.pack(side=tk.LEFT,padx=5)
        随机数按钮.pack(side=tk.LEFT,padx=5)
        添符按钮.pack(side=tk.LEFT,padx=5)
        替换按钮.pack(side=tk.LEFT,padx=5)
        合成按钮.pack(side=tk.LEFT,padx=5)
        获取字数按钮.pack(side=tk.LEFT,padx=5)
        Unicode按钮.pack_forget()
        utf8按钮.pack_forget()
        关机按钮.pack_forget()
        下一页按钮.pack_forget()
        下一页按钮.pack(side=tk.LEFT,padx=5)
        下一页按钮.config(text="下一页")
        记录["显示"] = 0
def 打开系统程序(命令, 程序名称="程序"):
    开始时间 = time.time()
    def worker():
        try:
            if os.name == 'nt':
                subprocess.Popen(命令, shell=True, startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW, wShowWindow=subprocess.SW_HIDE), creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(命令, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            结束时间 = time.time()
            耗时 = 结束时间 - 开始时间
            日志信息 = f"[{time.strftime('%H:%M:%S')}] 打开了 {程序名称} (耗时: {耗时:.3f}秒)\n"
            日志文本.after(0, lambda: 添加日志(日志信息))
        except Exception as e:
            error_msg = f"[{time.strftime('%H:%M:%S')}] 错误: 无法打开 {程序名称} - {str(e)}\n"
            日志文本.after(0, lambda: 添加日志(error_msg))
            messagebox.showerror("错误",e)
    threading.Thread(target=worker, daemon=True).start()
def 暂停更新():
    回答 = messagebox.askyesno("提示","是否暂停win更新100年？")
    if not 回答:
        return
    def 存储回调(输出, 返回码, 错误=None):
        if 错误:
            messagebox.showerror("错误", f"暂停失败：{错误}")
        elif 返回码 == 0:
            messagebox.showinfo("成功", "成功暂停win更新100年")
            回答 = messagebox.askyesno("提示","是否打开设置查看？")
            if 回答:
                threading.Thread(target=lambda: subprocess.Popen('powershell.exe -Command "Start-Process ms-settings:windowsupdate"', shell=True,startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW,wShowWindow=subprocess.SW_HIDE), creationflags=subprocess.CREATE_NO_WINDOW), daemon=True).start()
        else:
            messagebox.showerror("错误", f"暂停失败，返回码：{返回码}")
    命令 = '$currentValue = Get-ItemPropertyValue "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings" -Name "PauseUpdatesExpiryTime"\n$year = [int]$currentValue.Substring(0,4) + 100\n$newValue = "$year" + $currentValue.Substring(4)\nSet-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings" -Name "PauseUpdatesExpiryTime" -Value $newValue'
    运行命令(命令, 存储回调, "暂停win更新")
def 添加日志(信息):
    日志文本.insert(tk.END, 信息)
    日志文本.see(tk.END)
    日志文本.update_idletasks()


frame = tk.Frame(文本标签)
frame.pack(padx=10,pady=10)

清空按钮 = tk.Button(frame,text="清空",width=10,fg="red",command=清空)
清空按钮.pack(side=tk.LEFT,padx=5)

撤销按钮 = tk.Button(frame,text="撤销",width=10,fg="orange",command=撤销)
撤销按钮.pack(side=tk.LEFT,padx=5)

复制按钮 = tk.Button(frame,text="复制",width=10,fg="blue",command=复制)
复制按钮.pack(side=tk.LEFT,padx=5)

提取按钮 = tk.Button(frame,text="提取分离",width=10,fg="black",command=提取)
提取按钮.pack(side=tk.LEFT,padx=5)

随机数按钮 = tk.Button(frame,text="生成随机数",width=10,fg="black",command=随机数)
随机数按钮.pack(side=tk.LEFT,padx=5)

frame1 = tk.Frame(文本标签)
frame1.pack(padx=10,pady=5)

添符按钮 = tk.Button(frame1,text="添符",width=10,fg="black",command=添符)
添符按钮.pack(side=tk.LEFT,padx=5)

替换按钮 = tk.Button(frame1,text="替换",width=10,fg="black",command=替换)
替换按钮.pack(side=tk.LEFT,padx=5)

合成按钮 = tk.Button(frame1,text="合成",width=10,fg="black",command=合成)
合成按钮.pack(side=tk.LEFT,padx=5)

获取字数按钮 = tk.Button(frame1,text="获取字数",width=10,fg="black",command=获取字数)
获取字数按钮.pack(side=tk.LEFT,padx=5)

下一页按钮 = tk.Button(frame1,text="下一页",width=10,fg="#288BA3",command=下一页)
下一页按钮.pack(side=tk.LEFT,padx=5)

Unicode按钮 = tk.Button(frame,text="Unicode转化",width=10,fg="black",command=Unicode)

utf8按钮 = tk.Button(frame,text="utf-8转化",width=10,fg="black",command=utf8)

关机按钮 = tk.Button(frame1,text="关机/重启",width=10,fg="black",command=关机)

功能标题 = tk.Label(功能标签,text="功能大全",font=("微软雅黑",10,"bold"),fg="black",pady=0)
功能标题.pack()

功能标签页 = ttk.Notebook(功能标签)
功能标签页.pack(expand=True, fill='both', padx=10, pady=10)

系统功能标签 = ttk.Frame(功能标签页)
功能标签页.add(系统功能标签, text='系统功能')

打开功能标签 = ttk.Frame(功能标签页)
功能标签页.add(打开功能标签, text='打开功能')

其他功能标签 = ttk.Frame(功能标签页)
功能标签页.add(其他功能标签, text='其他功能')

系统功能容器 = tk.Frame(系统功能标签)
系统功能容器.pack(pady=10)
系统功能容器1 = tk.Frame(系统功能标签)
系统功能容器1.pack(pady=10)

其他功能容器 = tk.Frame(其他功能标签)
其他功能容器.pack(pady=10)

清理临时文件按钮 = tk.Button(系统功能容器,text="清理临时文件",width=10,fg="black",command=清理临时文件)
清理临时文件按钮.pack(side=tk.LEFT,padx=5)

查看磁盘按钮 = tk.Button(系统功能容器,text="查看磁盘使用",width=10,fg="black",command=查看磁盘使用情况)
查看磁盘按钮.pack(side=tk.LEFT,padx=5)

查看存储按钮 = tk.Button(系统功能容器,text="查看存储",width=10,fg="black",command=查看存储)
查看存储按钮.pack(side=tk.LEFT,padx=5)

查看附近ip按钮 = tk.Button(其他功能容器,text="查看附近ip",width=10,fg="black",command=查看附近ip)
查看附近ip按钮.pack(side=tk.LEFT,padx=5)

自定义窗口按钮 = tk.Button(其他功能容器,text="小窗",width=10,fg="black",command=窗口控制台函数)
自定义窗口按钮.pack(side=tk.LEFT,padx=5)

激活win按钮 = tk.Button(系统功能容器,text="激活win",width=10,fg="black",command=激活win)
激活win按钮.pack(side=tk.LEFT,padx=5)

暂停更新按钮 = tk.Button(系统功能容器,text="win暂停更新",width=10,fg="black",command=暂停更新)
暂停更新按钮.pack(side=tk.LEFT,padx=5)

打开功能容器 = tk.Frame(打开功能标签)
打开功能容器.pack(pady=10)
打开功能容器1 = tk.Frame(打开功能标签)
打开功能容器1.pack(pady=10)
打开功能容器2 = tk.Frame(打开功能标签)
打开功能容器2.pack(pady=10)
打开功能容器3 = tk.Frame(打开功能标签)
打开功能容器3.pack(pady=10)

任务管理器按钮 = tk.Button(打开功能容器,text="任务管理器",width=10,fg="black",command=lambda: 打开系统程序("taskmgr", "任务管理器"))
任务管理器按钮.pack(side=tk.LEFT,padx=5)

打开cmd按钮 = tk.Button(打开功能容器,text="命令提示符",width=10,fg="black",command=lambda: 打开系统程序("start cmd", "命令提示符"))
打开cmd按钮.pack(side=tk.LEFT,padx=5)

打开pow按钮 = tk.Button(打开功能容器,text="powershell",width=10,fg="black",command=lambda: 打开系统程序("start powershell", "powershell"))
打开pow按钮.pack(side=tk.LEFT,padx=5)

打开资源管理按钮 = tk.Button(打开功能容器,text="资源管理器",width=10,fg="black",command=lambda: 打开系统程序("explorer", "资源管理器"))
打开资源管理按钮.pack(side=tk.LEFT,padx=5)

控制面板按钮 = tk.Button(打开功能容器,text="控制面板",width=10,fg="black",command=lambda: 打开系统程序("control", "控制面板"))
控制面板按钮.pack(side=tk.LEFT,padx=5)

系统配置按钮 = tk.Button(打开功能容器1,text="系统配置",width=10,fg="black",command=lambda: 打开系统程序("msconfig", "系统配置"))
系统配置按钮.pack(side=tk.LEFT,padx=5)

服务管理按钮 = tk.Button(打开功能容器1,text="服务管理",width=10,fg="black",command=lambda: 打开系统程序("services.msc", "服务管理"))
服务管理按钮.pack(side=tk.LEFT,padx=5)

计算机管理按钮 = tk.Button(打开功能容器1,text="计算机管理",width=10,fg="black",command=lambda: 打开系统程序("compmgmt.msc", "计算机管理"))
计算机管理按钮.pack(side=tk.LEFT,padx=5)

设备管理按钮 = tk.Button(打开功能容器1,text="设备管理器",width=10,fg="black",command=lambda: 打开系统程序("devmgmt.msc", "设备管理器"))
设备管理按钮.pack(side=tk.LEFT,padx=5)

磁盘管理按钮 = tk.Button(打开功能容器1,text="磁盘管理",width=10,fg="black",command=lambda: 打开系统程序("diskmgmt.msc", "磁盘管理"))
磁盘管理按钮.pack(side=tk.LEFT,padx=5)

事件查看按钮 = tk.Button(打开功能容器2,text="事件查看器",width=10,fg="black",command=lambda: 打开系统程序("eventvwr.msc", "事件查看器"))
事件查看按钮.pack(side=tk.LEFT,padx=5)

任务计划按钮 = tk.Button(打开功能容器2,text="任务计划程序",width=10,fg="black",command=lambda: 打开系统程序("taskschd.msc", "任务计划程序"))
任务计划按钮.pack(side=tk.LEFT,padx=5)

用户管理按钮 = tk.Button(打开功能容器2,text="本地用户和组",width=10,fg="black",command=lambda: 打开系统程序("lusrmgr.msc", "本地用户和组"))
用户管理按钮.pack(side=tk.LEFT,padx=5)

安全策略按钮 = tk.Button(打开功能容器2,text="本地安全策略",width=10,fg="black",command=lambda: 打开系统程序("secpol.msc", "本地安全策略"))
安全策略按钮.pack(side=tk.LEFT,padx=5)

组策略按钮 = tk.Button(打开功能容器2,text="组策略编辑器",width=10,fg="black",command=lambda: 打开系统程序("gpedit.msc", "组策略编辑器"))
组策略按钮.pack(side=tk.LEFT,padx=5)

注册表按钮 = tk.Button(打开功能容器3,text="注册表编辑器",width=10,fg="black",command=lambda: 打开系统程序("regedit", "注册表编辑器"))
注册表按钮.pack(side=tk.LEFT,padx=5)

数据源按钮 = tk.Button(打开功能容器3,text="数据源管理器",width=10,fg="black",command=lambda: 打开系统程序("odbcad32", "数据源管理器"))
数据源按钮.pack(side=tk.LEFT,padx=5)

临时文件夹按钮 = tk.Button(打开功能容器3,text="临时文件夹",width=10,fg="black",command=lambda: 打开系统程序("start %temp%", "临时文件夹"))
临时文件夹按钮.pack(side=tk.LEFT,padx=5)

运行按钮 = tk.Button(打开功能容器3,text="运行对话框",width=10,fg="black",command=lambda: (threading.Thread(target=pyautogui.hotkey,args=('win', 'r'),daemon=True).start(), 添加日志(f"[{time.strftime('%H:%M:%S')}] 打开了 运行对话框\n")))
运行按钮.pack(side=tk.LEFT,padx=5)

磁盘清理按钮 = tk.Button(打开功能容器3,text="磁盘清理",width=10,fg="black",command=lambda: 打开系统程序("cleanmgr", "磁盘清理"))
磁盘清理按钮.pack(side=tk.LEFT,padx=5)

版权 = tk.Label(root,text="© 2026 耶y 版权所有",font=("微软雅黑",7,"bold"),fg="gray",pady=0)
版权.pack()

#检测系统
import platform
if sys.platform != "win32" or sys.getwindowsversion().major < 8:
    messagebox.showwarning("警告","由于win版本低于win8或不是win，不能使用部分功能\n部分功能需要powershell\n已禁用相关高级功能")
    功能标签页.tab(0, state="disabled")
    查看附近ip按钮.config(state="disabled")

root.mainloop()