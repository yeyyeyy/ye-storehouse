import tkinter as tk
import webbrowser
import os, sys

class EmailOpener:
    def __init__(self, root):
        self.root = root
        self.root.title("邮箱打开工具")
        self.root.geometry("450x500")  # 增加窗口高度
        
        # 设置窗口图标（如果有的话）
        try:
            self.临时目录 = sys._MEIPASS
            self.图标路径 = os.path.join(self.临时目录, "邮箱图标.ico\\邮箱图标.ico")
            self.root.iconbitmap(self.图标路径)
        except:
            pass
        
        # 创建主框架
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # 标题标签
        title_label = tk.Label(main_frame, text="邮箱打开器", font=("微软雅黑", 18, "bold"))
        title_label.pack(pady=(0, 15))
        
        # 说明标签
        desc_label = tk.Label(main_frame, text="点击按钮在默认浏览器中打开对应邮箱", font=("微软雅黑", 10))
        desc_label.pack(pady=(0, 25))
        
        # 按钮框架 - 使用Canvas实现滚动
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(expand=True, fill=tk.BOTH)
        
        # 创建Canvas和滚动条
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 邮箱按钮数据
        emails = [
            ("QQ邮箱", "https://mail.qq.com", "#12B7F5"),
            ("网易邮箱", "https://mail.163.com", "#D32F2F"),
            ("Gmail", "https://mail.google.com", "#EA4335"),
            ("Outlook", "https://outlook.live.com", "#0078D4"),
            ("新浪邮箱", "https://mail.sina.com.cn", "#FF6D00"),
            ("搜狐邮箱", "https://mail.sohu.com", "#FF9800"),
            ("雅虎邮箱", "https://mail.yahoo.com", "#720E9E"),
            ("腾讯企业邮箱", "https://exmail.qq.com", "#0088CC")
        ]
        
        # 创建按钮 - 使用3列布局
        self.buttons = []
        for i, (name, url, color) in enumerate(emails):
            row = i // 3
            col = i % 3
            
            btn = tk.Button(
                scrollable_frame,
                text=name,
                font=("微软雅黑", 10),
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief=tk.RAISED,
                borderwidth=2,
                padx=15,
                pady=8,
                cursor="hand2",
                command=lambda u=url: self.open_email(u)
            )
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.buttons.append(btn)
            
            # 绑定鼠标悬停事件
            btn.bind("<Enter>", lambda e, b=btn: self.on_enter(e, b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_leave(e, b))
        
        # 设置网格权重
        for col in range(3):
            scrollable_frame.grid_columnconfigure(col, weight=1, minsize=120)
        
        # 布局Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 底部信息
        info_label = tk.Label(main_frame, text="程序将在默认浏览器中打开邮箱网站", font=("微软雅黑", 9), fg="gray")
        info_label.pack(pady=(15, 5))
        
        # 版权信息
        copyright_label = tk.Label(main_frame, text="© 2025 邮箱打开器", font=("微软雅黑", 8), fg="gray")
        copyright_label.pack(pady=(5, 0))
    
    def on_enter(self, event, button):
        """鼠标进入按钮时的效果"""
        button.config(relief=tk.SUNKEN)
    
    def on_leave(self, event, button):
        """鼠标离开按钮时的效果"""
        button.config(relief=tk.RAISED)
    
    def open_email(self, url):
        """打开邮箱网站"""
        try:
            webbrowser.open(url)
            print(f"正在打开: {url}")
        except Exception as e:
            print(f"打开失败: {e}")
            # 显示错误消息
            error_window = tk.Toplevel(self.root)
            error_window.title("错误")
            error_window.geometry("300x100")
            
            error_label = tk.Label(error_window, text=f"无法打开链接:\n{url}", font=("微软雅黑", 10), fg="red")
            error_label.pack(pady=20)
            
            ok_btn = tk.Button(error_window, text="确定", command=error_window.destroy)
            ok_btn.pack()

def main():
    root = tk.Tk()
    app = EmailOpener(root)
    root.mainloop()

if __name__ == "__main__":
    main()