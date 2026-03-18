import tkinter as tk
from tkinter import ttk, messagebox, Text, simpledialog
import subprocess
import ctypes
import sys
import threading
import re
import json
import os
import webbrowser

LANG_DATA = {
    "RU": {
        "tab_dns":"   DNS Менеджер   ",
        "tab_reset":"   Сброс Сети   ",
        "tab_about":"   Справка   ",
        "lbl_adapter":"Активное подключение:",
        "lbl_presets":"Быстрые пресеты:",
        "btn_apply":"✅ ПРИМЕНИТЬ",
        "btn_reset_auto":"🔄 ВЕРНУТЬ АВТО",
        "msg_wait":"Подождите завершения операции",
        "msg_success":"Успех",
        "msg_error_adapter":"Выберите сетевой адаптер",
        "msg_done_dns":"DNS адреса применены",
        "msg_done_auto":"Сброс DNS в автоматический режим (По умолчанию)",
        "msg_done_reset":"Сброс сетевых настроек завершен. Перезагрузите ПК",
        "tip_apply":"Эти команды будут выполнены:\nnetsh interface ip set dns\nnetsh interface ip add dns\nipconfig /flushdns",
        "tip_reset_auto":"Сбросить DNS на DHCP (По умолчанию)\nКоманда:\nnetsh interface ip set dns source=dhcp",
        "tip_google":"Google DNS\nОсновной: 8.8.8.8\nАльтернативный: 8.8.4.4",
        "tip_cloudflare":"Cloudflare DNS\nОсновной: 1.1.1.1\nАльтернативный: 1.0.0.1",
        "tip_comss":"DNS Comss.one. Обход блокировок сайтов ИИ и прочее\nОсновной: 83.220.169.155\nАльтернативный: 212.109.195.93",
        "tip_xbox":"XBOX DNS (xbox-dns.ru)\nОбход игровых блокировок, доступ к играм\nНовые адреса:\n111.88.96.50\n111.88.96.51\nСтарые адреса XBOX:\n176.99.11.77\n80.78.247.254",
        "log_dns_title":" Журнал DNS ",
        "log_reset_title":" Журнал сетевых операций "
    }
}

class CreateToolTip:
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tw = None

    def update_text(self, new_text):
        self.text = new_text

    def enter(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw,
            text=self.text,
            justify="left",
            background="white",
            relief="solid",
            borderwidth=1,
            wraplength=300,
            padx=8,
            pady=5
        )
        label.pack()

    def leave(self, event=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        " ".join(sys.argv),
        None,
        1
    )
    sys.exit()

def validate_ip(ip):
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if not re.match(pattern, ip):
        return False
    parts = ip.split(".")
    for p in parts:
        if int(p) > 255:
            return False
    return True

class NetworkManagerApp:
    PRESETS_FILE = os.path.join(os.path.dirname(sys.argv[0]), "dns_presets.json")
    DEFAULT_PRESETS = [
        {"name": "Google", "d1": "8.8.8.8", "d2": "8.8.4.4", "tip_key": "tip_google"},
        {"name": "Cloudflare", "d1": "1.1.1.1", "d2": "1.0.0.1", "tip_key": "tip_cloudflare"},
        {"name": "Comss", "d1": "83.220.169.155", "d2": "212.109.195.93", "tip_key": "tip_comss"},
        {"name": "Xbox", "d1": "111.88.96.50", "d2": "111.88.96.51", "tip_key": "tip_xbox"}
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер сети 1.1")
        self.root.geometry("640x760")
        self.root.resizable(False, False)
        self.tooltips = {}
        self.is_running = False
        self.presets = []

        self.tab_control = ttk.Notebook(root)
        self.tab_dns = ttk.Frame(self.tab_control)
        self.tab_reset = ttk.Frame(self.tab_control)
        self.tab_about = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_dns)
        self.tab_control.add(self.tab_reset)
        self.tab_control.add(self.tab_about)
        self.tab_control.pack(expand=1, fill="both")

        self.load_presets()
        self.setup_dns_tab()
        self.setup_reset_tab()
        self.setup_about_tab()
        self.update_texts()

    def T(self, key):
        return LANG_DATA["RU"].get(key, key)

    def load_presets(self):
        if os.path.exists(self.PRESETS_FILE):
            try:
                self.presets = json.load(open(self.PRESETS_FILE, "r", encoding="utf-8"))
            except:
                self.presets = self.DEFAULT_PRESETS.copy()
        else:
            self.presets = self.DEFAULT_PRESETS.copy()
        self.save_presets()

    def save_presets(self):
        json.dump(self.presets, open(self.PRESETS_FILE, "w", encoding="utf-8"), indent=4)

    def update_texts(self):
        self.tab_control.tab(0, text=self.T("tab_dns"))
        self.tab_control.tab(1, text=self.T("tab_reset"))
        self.tab_control.tab(2, text=self.T("tab_about"))
        self.lbl_adapter.config(text=self.T("lbl_adapter"))
        self.lbl_presets.config(text=self.T("lbl_presets"))
        self.btn_apply.config(text=self.T("btn_apply"))
        self.btn_reset_auto.config(text=self.T("btn_reset_auto"))
        for preset, btn in zip(self.presets, self.preset_buttons):
            tip_text = self.T(preset.get("tip_key", "")) if "tip_key" in preset else ""
            self.tooltips[btn].update_text(tip_text)
        self.tooltips["apply"].update_text(self.T("tip_apply"))
        self.tooltips["auto"].update_text(self.T("tip_reset_auto"))

    def setup_dns_tab(self):
        frame = self.tab_dns
        self.lbl_adapter = ttk.Label(frame)
        self.lbl_adapter.pack(anchor="w", padx=20, pady=10)
        self.adapter_combo = ttk.Combobox(frame, width=60, state="readonly")
        self.adapter_combo.pack(padx=20)
        self.refresh_adapters()
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=10)
        ttk.Label(input_frame, text="DNS1").grid(row=0, column=0, padx=5, pady=4, sticky="e")
        self.dns1_entry = ttk.Entry(input_frame, width=28)
        self.dns1_entry.grid(row=0, column=1, padx=5, pady=4)
        ttk.Label(input_frame, text="DNS2").grid(row=1, column=0, padx=5, pady=4, sticky="e")
        self.dns2_entry = ttk.Entry(input_frame, width=28)
        self.dns2_entry.grid(row=1, column=1, padx=5, pady=4)

        self.lbl_presets = ttk.Label(frame)
        self.lbl_presets.pack(pady=6)
        self.btn_frame = ttk.Frame(frame)
        self.btn_frame.pack(pady=4)
        self.preset_buttons = []

        def redraw_preset_buttons():
            for widget in self.btn_frame.winfo_children():
                widget.destroy()
            self.preset_buttons.clear()
            for idx, preset in enumerate(self.presets):
                btn = ttk.Button(
                    self.btn_frame,
                    text=preset["name"],
                    width=12,
                    command=lambda d1=preset["d1"], d2=preset["d2"]: self.set_preset(d1, d2)
                )
                btn.grid(row=0, column=idx, padx=3, pady=2)
                self.preset_buttons.append(btn)
                self.tooltips[btn] = CreateToolTip(btn, self.T(preset.get("tip_key", "")))
                menu = tk.Menu(btn, tearoff=0)
                menu.add_command(label="Удалить", command=lambda i=idx: self.delete_preset(i))
                def show_menu(e, m=menu):
                    try: m.tk_popup(e.x_root, e.y_root)
                    finally: m.grab_release()
                btn.bind("<Button-3>", show_menu)

        self.redraw_preset_buttons = redraw_preset_buttons
        redraw_preset_buttons()
        add_btn = ttk.Button(frame, text="+", width=3, command=self.add_custom_preset)
        add_btn.pack(pady=5)

        act_frame = ttk.Frame(frame)
        act_frame.pack(pady=18)
        self.btn_apply = ttk.Button(act_frame, command=self.task_apply_dns)
        self.btn_apply.pack(side="left", padx=10)
        self.btn_reset_auto = ttk.Button(act_frame, command=self.task_reset_dns)
        self.btn_reset_auto.pack(side="right", padx=10)
        self.tooltips["apply"] = CreateToolTip(self.btn_apply, self.T("tip_apply"))
        self.tooltips["auto"] = CreateToolTip(self.btn_reset_auto, self.T("tip_reset_auto"))

        self.log_dns_frame = ttk.LabelFrame(frame, text=self.T("log_dns_title"))
        self.log_dns_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.dns_log = Text(self.log_dns_frame, state="disabled", height=10)
        self.dns_log.pack(fill="both", expand=True)

    def add_custom_preset(self):
        name = simpledialog.askstring("Имя пресета", "Введите имя пресета:", parent=self.root)
        if not name: return
        d1 = simpledialog.askstring("DNS1", "Введите основной DNS:", parent=self.root)
        if not d1 or not validate_ip(d1): messagebox.showerror("ОШИБКА", "НЕВЕРНЫЙ DNS"); return
        d2 = simpledialog.askstring("DNS2 (optional)", "Введите резервный DNS:", parent=self.root)
        if d2 and not validate_ip(d2): messagebox.showerror("ОШИБКА", "НЕВЕРНЫЙ DNS"); return
        self.presets.append({"name": name, "d1": d1, "d2": d2})
        self.save_presets()
        self.redraw_preset_buttons()

    def delete_preset(self, idx):
        if messagebox.askyesno("Удалить пресет", "Удалить этот пресет?"):
            self.presets.pop(idx)
            self.save_presets()
            self.redraw_preset_buttons()

    def set_preset(self, d1, d2):
        self.dns1_entry.delete(0, tk.END)
        self.dns1_entry.insert(0, d1)
        self.dns2_entry.delete(0, tk.END)
        self.dns2_entry.insert(0, d2)

    def log_dns(self, text):
        self.dns_log.config(state="normal")
        self.dns_log.insert(tk.END, text + "\n")
        self.dns_log.see(tk.END)
        self.dns_log.config(state="disabled")

    def log_reset(self, text):
        self.reset_log.config(state="normal")
        self.reset_log.insert(tk.END, text + "\n")
        self.reset_log.see(tk.END)
        self.reset_log.config(state="disabled")

    def get_active_adapters(self):
        try:
            cmd = 'powershell "Get-NetAdapter | Where Status -eq Up | Select -Expand Name"'
            output = subprocess.check_output(cmd, shell=True).decode("cp866", errors="ignore")
            adapters = [line.strip() for line in output.splitlines() if line.strip()]
            return adapters
        except Exception as e:
            self.log_dns("Ошибка адаптера: " + str(e))
            return []

    def refresh_adapters(self):
        adapters = self.get_active_adapters()
        if adapters:
            self.adapter_combo["values"] = adapters
            self.adapter_combo.current(0)
        else:
            self.adapter_combo["values"] = []

    def run_command(self, command, log_func):
        try:
            result = subprocess.run(command, shell=True, capture_output=True)
            if result.stdout:
                # Декодируем вывод консоли Windows для исключения иероглифов
                msg = result.stdout.decode("cp866", errors="replace").strip()
                log_func(msg)
            if result.stderr:
                msg = result.stderr.decode("cp866", errors="replace").strip()
                log_func("SYSTEM: " + msg)
        except Exception as e:
            log_func("Command error: " + str(e))

    def apply_dns_worker(self, iface, d1, d2):
        self.log_dns("Сброс настроек DNS интерфейса...")
        # Сначала сбросим на DHCP, чтобы очистить старые записи
        subprocess.run(f'netsh interface ip set dns name="{iface}" source=dhcp', shell=True, capture_output=True)
        
        self.log_dns(f"Setting DNS1: {d1}")
        cmd1 = f'netsh interface ip set dns name="{iface}" static {d1}'
        self.run_command(cmd1, self.log_dns)
        
        if d2:
            self.log_dns(f"Adding DNS2: {d2}")
            cmd2 = f'netsh interface ip add dns name="{iface}" {d2} index=2'
            self.run_command(cmd2, self.log_dns)
            
        self.run_command("ipconfig /flushdns", self.log_dns)
        self.log_dns("Обновление DNS завершено..")
        messagebox.showinfo("Успех", "DNS применён")
        self.is_running = False

    def task_apply_dns(self):
        if self.is_running:
            messagebox.showwarning("", "Дождитесь завершения операции")
            return
        iface = self.adapter_combo.get()
        d1 = self.dns1_entry.get().strip()
        d2 = self.dns2_entry.get().strip()
        if not iface:
            messagebox.showwarning("", "Выберите сетевой адаптер")
            return
        if not validate_ip(d1):
            messagebox.showwarning("", "DNS1 неверный")
            return
        if d2 and not validate_ip(d2):
            messagebox.showwarning("", "DNS2 неверный")
            return
        self.is_running = True
        threading.Thread(target=self.apply_dns_worker, args=(iface, d1, d2)).start()

    def reset_dns_worker(self, iface):
        self.log_dns("Сброс DNS в автоматический режим (DHCP)...")
        cmd = f'netsh interface ip set dns name="{iface}" source=dhcp'
        self.run_command(cmd, self.log_dns)
        self.run_command("ipconfig /flushdns", self.log_dns)
        self.log_dns("Сброс DNS на автоматический режим завершен..")
        messagebox.showinfo("Успех", "Сброс DNS в автоматический режим.")
        self.is_running = False

    def task_reset_dns(self):
        if self.is_running:
            messagebox.showwarning("", "Дождитесь завершения операции")
            return
        iface = self.adapter_combo.get()
        if not iface:
            messagebox.showwarning("", "Выберите сетевой адаптер")
            return
        self.is_running = True
        threading.Thread(target=self.reset_dns_worker, args=(iface,)).start()

    def setup_reset_tab(self):
        frame = self.tab_reset
        title = tk.Label(frame, text="Инструменты для сброса сети", font=("Segoe UI", 12))
        title.pack(pady=20)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        btn_flush = ttk.Button(btn_frame, text="Сброс DNS - ipconfig /flushdns", width=33, command=lambda: self.run_command("ipconfig /flushdns", self.log_reset))
        btn_flush.grid(row=0, column=0, padx=5, pady=5)
        self.tooltips[btn_flush] = CreateToolTip(btn_flush, "Сброс кэша DNS\nCommand: ipconfig /flushdns")

        btn_release = ttk.Button(btn_frame, text="Освободить IP - ipconfig /release", width=33, command=lambda: self.run_command("ipconfig /release", self.log_reset))
        btn_release.grid(row=0, column=1, padx=5, pady=5)
        self.tooltips[btn_release] = CreateToolTip(btn_release, "Освободить IP address\nCommand: ipconfig /release")

        btn_renew = ttk.Button(btn_frame, text="Новый IP - ipconfig /renew", width=33, command=lambda: self.run_command("ipconfig /renew", self.log_reset))
        btn_renew.grid(row=1, column=0, padx=5, pady=5)
        self.tooltips[btn_renew] = CreateToolTip(btn_renew, "Новый IP адрес\nCommand: ipconfig /renew")

        btn_winsock = ttk.Button(btn_frame, text="Сброс Winsock - netsh winsock reset", width=33, command=lambda: self.run_command("netsh winsock reset", self.log_reset))
        btn_winsock.grid(row=1, column=1, padx=5, pady=5)
        self.tooltips[btn_winsock] = CreateToolTip(btn_winsock, "Сброс каталога Winsock\nКоманда: netsh winsock reset")

        btn_tcpip = ttk.Button(btn_frame, text="Сброс TCP/IP - netsh int ip reset", width=33, command=lambda: self.run_command("netsh int ip reset", self.log_reset))
        btn_tcpip.grid(row=2, column=0, padx=5, pady=5)
        self.tooltips[btn_tcpip] = CreateToolTip(btn_tcpip, "Сброс TCP/IP stack\nКоманда: netsh int ip reset")

        self.log_reset_frame = ttk.LabelFrame(frame, text=self.T("log_reset_title"))
        self.log_reset_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.reset_log = Text(self.log_reset_frame, state="disabled", height=10)
        self.reset_log.pack(fill="both", expand=True)

    def setup_about_tab(self):
        frame = self.tab_about
        lbl = tk.Label(frame, text="Менеджер сети — графический инструмент для Windows\n"
        "Версия 1.1\n"
        "Автор: Solar Svarga\n\n"
        "Возможности:\n"
        "• DNS Менеджер с предустановленными пресетами (Google, Cloudflare, Comss, Xbox)\n"
        "• Добавление, удаление и применение собственных DNS-пресетов\n"
        "• Инструменты сброса сети: flush DNS, release/renew IP, сброс Winsock/TCP-IP\n"
        "• Журналы операций DNS и сети\n"
        "• Файл с пресетами создаётся рядом с программой\n"
        "• Всплывающие подсказки с описанием команд\n\n"
        "Требуется запуск от имени администратора\n\n"
        "*Если случайно удалили стандартный пресет,\n то рядом с программой удалите файл dns_presets.json\n"
        "Все действия выполняются локально; данные\n на внешние серверы не передаются", font=("Segoe UI", 12))
        lbl.pack(pady=40)
        link = tk.Label(frame, text="GitHub", fg="blue", cursor="hand2", font=("Segoe UI", 21))
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/solarsvarga"))

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkManagerApp(root)
    root.mainloop()
