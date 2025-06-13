import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from requests_ntlm import HttpNtlmAuth
import urllib3
import socket
import threading
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import re
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
PI_SERVER = "172.16.0.133"
USERNAME = "Administrator"
PASSWORD = "OsaiPI$321"
SYSLOG_HOST = "172.16.0.126"
SYSLOG_PORT = 5514
POINTS_URL = f"https://{PI_SERVER}/piwebapi/dataservers/F1DSdkt6A8VuUE6PK_yW6WufqAT1NJUEk/points"
auth = HttpNtlmAuth(USERNAME, PASSWORD)

# Globals
point_data = {}
tag_settings = {}
groups = {}
blink_state = False
dark_mode = False
user_editing = False
log_messages = []

columns = ("Tag", "Value", "Timestamp", "Min", "Max", "Min Msg", "Max Msg", "Priority")

def set_editing(state):
    global user_editing
    user_editing = state

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_messages.append(f"[{timestamp}] {message}")
    if len(log_messages) > 1000:
        log_messages.pop(0)
    log_text.config(state="normal")
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "\n".join(log_messages[-100:]))
    log_text.config(state="disabled")

def send_syslog(message: dict):
    try:
        full_msg = json.dumps(message)
        syslog_data = f"<10>{full_msg}"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(syslog_data.encode(), (SYSLOG_HOST, SYSLOG_PORT))
        log(f"Sent syslog: {full_msg}")
    except Exception as e:
        log(f"Syslog error: {e}")

def parse_timestamp_to_ist(utc_timestamp: str) -> str:
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(utc_timestamp, fmt)
            dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Kolkata"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return utc_timestamp

def get_point_value(value_url):
    try:
        response = requests.get(value_url, auth=auth, verify=False, timeout=5)
        response.raise_for_status()
        data = response.json()
        val = data.get("Value", data)
        timestamp = parse_timestamp_to_ist(data.get("Timestamp", "")) if "Timestamp" in data else ""
        return val.get("Value") if isinstance(val, dict) else val, timestamp
    except Exception as e:
        return f"Error: {e}", ""

def get_all_points():
    try:
        r = requests.get(POINTS_URL, auth=auth, verify=False, timeout=10)
        r.raise_for_status()
        return r.json().get("Items", [])
    except Exception as e:
        log(f"Error getting points: {e}")
        return []

def fetch_and_update():
    global point_data
    points = get_all_points()
    for point in points:
        name = point.get("Name", "")
        if re.match(r"^[0-9a-f\-]{36}$", name, re.IGNORECASE):  # Skip GUIDs
            continue
        value_url = point.get("Links", {}).get("Value", "")
        value, timestamp = get_point_value(value_url)

        point_data[name] = {"value": value, "timestamp": timestamp}
        settings = tag_settings.get(name, {})

        min_val = settings.get("min")
        max_val = settings.get("max")
        min_msg = settings.get("min_msg", "")
        max_msg = settings.get("max_msg", "")
        priority = settings.get("priority", "High")

        try:
            if isinstance(value, (int, float)):
                if min_val is not None and value < min_val:
                    send_syslog({
                        "Tag": name, "Value": value, "Timestamp": timestamp,
                        "Severity": "Critical", "Condition": "Below Min",
                        "Threshold": min_val, "Message": min_msg, "Priority": priority
                    })
                elif max_val is not None and value > max_val:
                    send_syslog({
                        "Tag": name, "Value": value, "Timestamp": timestamp,
                        "Severity": "Critical", "Condition": "Above Max",
                        "Threshold": max_val, "Message": max_msg, "Priority": priority
                    })
        except Exception as e:
            log(f"Alert error: {e}")

    root.after(0, refresh_treeview)
    root.after(10000, lambda: threading.Thread(target=fetch_and_update, daemon=True).start())

root = tk.Tk()
root.title("PI Web API Monitor")
root.geometry("1300x750")

style = ttk.Style(root)
style.theme_use("clam")

tree = ttk.Treeview(root, columns=columns, show="headings", height=18)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=120)
tree.pack(fill="both", expand=True, padx=10, pady=10)
tree.bind("<<TreeviewSelect>>", lambda e: populate_settings_from_selection())

frame_main = tk.Frame(root)
frame_main.pack(fill="x", padx=10, pady=5)

frame_inputs = tk.Frame(frame_main)
frame_inputs.pack(side="left", padx=5)

tk.Label(frame_inputs, text="Min:").grid(row=0, column=0, sticky="e")
min_entry = tk.Entry(frame_inputs, width=10)
min_entry.grid(row=0, column=1)

tk.Label(frame_inputs, text="Max:").grid(row=0, column=2, sticky="e")
max_entry = tk.Entry(frame_inputs, width=10)
max_entry.grid(row=0, column=3)

tk.Label(frame_inputs, text="Min Msg:").grid(row=1, column=0, sticky="e")
min_msg_entry = tk.Entry(frame_inputs, width=40)
min_msg_entry.grid(row=1, column=1, columnspan=3)

tk.Label(frame_inputs, text="Max Msg:").grid(row=2, column=0, sticky="e")
max_msg_entry = tk.Entry(frame_inputs, width=40)
max_msg_entry.grid(row=2, column=1, columnspan=3)

tk.Label(frame_inputs, text="Priority:").grid(row=3, column=0, sticky="e")
priority_entry = ttk.Combobox(frame_inputs, values=["Critical", "High", "Medium", "Low"], state="readonly", width=10)
priority_entry.current(1)
priority_entry.grid(row=3, column=1, sticky="w")

def apply_settings():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a tag first.")
        return
    try:
        tag_settings[selected] = {
            "min": float(min_entry.get()) if min_entry.get() else None,
            "max": float(max_entry.get()) if max_entry.get() else None,
            "min_msg": min_msg_entry.get(),
            "max_msg": max_msg_entry.get(),
            "priority": priority_entry.get()
        }
        log(f"Settings applied to {selected}")
        refresh_treeview()
    except ValueError:
        messagebox.showerror("Input Error", "Invalid min/max values.")

ttk.Button(frame_inputs, text="Apply Settings", command=apply_settings).grid(row=3, column=3)

# Log Viewer
log_frame = tk.Frame(frame_main)
log_frame.pack(side="right", fill="both", expand=True)
tk.Label(log_frame, text="Logs").pack(anchor="w")
log_text = tk.Text(log_frame, height=12, width=60, state="disabled", bg="#f0f0f0")
log_text.pack(fill="both", expand=True)

def refresh_treeview():
    selected_tag = tree.focus()
    tree.delete(*tree.get_children())
    for tag, data in point_data.items():
        settings = tag_settings.get(tag, {})
        row_values = (
            tag, data.get("value", ""), data.get("timestamp", ""),
            str(settings.get("min", "")), str(settings.get("max", "")),
            settings.get("min_msg", ""), settings.get("max_msg", ""),
            settings.get("priority", "High")
        )
        alert = False
        try:
            v = data.get("value", 0)
            if isinstance(v, (int, float)) and (
                (settings.get("min") is not None and v < settings["min"]) or
                (settings.get("max") is not None and v > settings["max"])
            ):
                alert = True
        except:
            pass
        tree.insert("", "end", iid=tag, values=row_values, tags=("alert_row",) if alert else ())

    if selected_tag and tree.exists(selected_tag):
        tree.selection_set(selected_tag)
        tree.focus(selected_tag)

def populate_settings_from_selection():
    selected = tree.focus()
    if not selected:
        return
    settings = tag_settings.get(selected, {})
    min_entry.delete(0, tk.END)
    max_entry.delete(0, tk.END)
    min_msg_entry.delete(0, tk.END)
    max_msg_entry.delete(0, tk.END)
    priority_entry.set(settings.get("priority", "High"))
    if settings.get("min") is not None:
        min_entry.insert(0, str(settings["min"]))
    if settings.get("max") is not None:
        max_entry.insert(0, str(settings["max"]))
    min_msg_entry.insert(0, settings.get("min_msg", ""))
    max_msg_entry.insert(0, settings.get("max_msg", ""))

def hex_color_blend(color1, color2, blend_factor):
    """Blend two hex colors based on blend_factor (0.0 to 1.0)"""
    c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
    c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
    blended = [int(c1[i] + (c2[i] - c1[i]) * blend_factor) for i in range(3)]
    return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"

def animate_theme(start_bg, end_bg, steps=10, delay=30):
    for step in range(steps + 1):
        blend = step / steps
        new_bg = hex_color_blend(start_bg, end_bg, blend)
        root.configure(bg=new_bg)
        for frame in [frame_main, frame_inputs, log_frame, frame_buttons]:
            try:
                frame.configure(bg=new_bg)
            except:
                pass
        log_text.configure(state="normal")
        try:
            log_text.configure(bg=new_bg)
        except:
            pass
        log_text.configure(state="disabled")
        root.update()
        time.sleep(delay / 1000)

def toggle_theme():
    global dark_mode
    start_bg = "#121212" if dark_mode else "#FFFFFF"
    end_bg = "#FFFFFF" if dark_mode else "#121212"
    dark_mode = not dark_mode
    fg = "#FFFFFF" if dark_mode else "#000000"

    # Animate background
    animate_theme(start_bg, end_bg)

    style.configure("Treeview", background=end_bg, foreground=fg, fieldbackground=end_bg)

    widgets = [min_entry, max_entry, min_msg_entry, max_msg_entry, log_text]

    for widget in widgets:
        try:
            widget.configure(bg=end_bg, fg=fg, insertbackground=fg)
        except tk.TclError:
            pass

    for label in frame_inputs.winfo_children():
        if isinstance(label, tk.Label):
            try:
                label.configure(bg=end_bg, fg=fg)
            except tk.TclError:
                pass

    # ttk combobox style
    style.map('TCombobox', fieldbackground=[('readonly', end_bg)], foreground=[('readonly', fg)])
    style.configure('TCombobox', fieldbackground=end_bg, foreground=fg)

    refresh_treeview()


def blink_rows():
    global blink_state
    blink_state = not blink_state
    tree.tag_configure("alert_row", background="#FF5555" if blink_state else ("#121212" if dark_mode else "#FFFFFF"))
    root.after(500, blink_rows)

def export_settings():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if not file_path: return
    with open(file_path, "w") as f:
        json.dump(tag_settings, f, indent=2)
    log("Settings exported")

def import_settings():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path: return
    with open(file_path, "r") as f:
        tag_settings.update(json.load(f))
    refresh_treeview()
    log("Settings imported")

def bounce_button(button, times=3, distance=2, delay=60):
    original_pad = button.pack_info().get('padx', 5)
    for i in range(times):
        button.pack_configure(padx=original_pad + distance)
        root.update()
        time.sleep(delay / 1000)
        button.pack_configure(padx=original_pad - distance)
        root.update()
        time.sleep(delay / 1000)
    button.pack_configure(padx=original_pad)


frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)
ttk.Button(frame_buttons, text="Export Settings", command=export_settings).pack(side="left", padx=5)
ttk.Button(frame_buttons, text="Import Settings", command=import_settings).pack(side="left", padx=5)

btn_toggle = ttk.Button(frame_buttons, text="Toggle Theme", command=lambda: [bounce_button(btn_toggle), toggle_theme()])
btn_toggle.pack(side="left", padx=5)

blink_rows()
threading.Thread(target=fetch_and_update, daemon=True).start()
root.mainloop()
