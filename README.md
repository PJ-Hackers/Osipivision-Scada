Got it! Since the original README used triple backticks for both code and markdown, it conflicted visually. Here's the revised `README.md` written **cleanly without syntax conflicts**, so you can copy and paste it directly into your repo:

---

### ✅ `README.md`

# PI Web API Monitor

A GUI tool built using Python's Tkinter for monitoring PI System tags via the PI Web API. The app allows you to configure thresholds for tag values, log alerts, and send syslog messages if values exceed set limits. It includes dark mode support, logging, import/export settings, and real-time updates.

---

## 🔧 Features

* Monitor PI System tags in real time
* Define min/max threshold values per tag
* Send alerts via syslog (UDP)
* Blinking red alerts for exceeded values
* Light/Dark theme toggle with animation
* Import/Export tag configurations (JSON)
* Editable tag priority and custom messages
* Scrollable, sortable tag list with timestamps

---

## 🛠 Requirements

* Python 3.9 or newer
* The following Python packages:

```
pip install requests requests_ntlm
```

---

## ⚙️ Configuration

Before running the script, update the following variables in the code:

* `PI_SERVER` – your PI Web API server hostname or IP
* `USERNAME` / `PASSWORD` – PI Web API credentials
* `SYSLOG_HOST` / `SYSLOG_PORT` – destination for syslog alerts
* `POINTS_URL` – formatted URL with your PI Web API server’s key

Example:

```python
PI_SERVER = "192.168.1.10"
USERNAME = "DOMAIN\\Username"
PASSWORD = "yourpassword"
SYSLOG_HOST = "192.168.1.99"
SYSLOG_PORT = 514
POINTS_URL = f"https://{PI_SERVER}/piwebapi/dataservers/{your_key}/points"
```

---

## ▶️ How to Run

Run the script using:

```
python pi_webapi_monitor.py
```

Replace the filename with your actual script filename.

---

## 🖥 How to Use

1. Launch the application.
2. Select a tag from the table.
3. Set threshold values (`Min`, `Max`) and messages.
4. Click **"Apply Settings"**.
5. Alerts will blink red if thresholds are violated and send syslog messages.
6. Use **"Export Settings"** to save configurations.
7. Use **"Import Settings"** to load previous configurations.
8. Toggle between light/dark themes with **"Toggle Theme"**.

---

## 📤 Syslog Format Example

Messages sent over UDP to the syslog server in JSON format:

```json
{
  "Tag": "TemperatureSensor01",
  "Value": 110.5,
  "Timestamp": "2025-06-13 15:30:45",
  "Severity": "Critical",
  "Condition": "Above Max",
  "Threshold": 100,
  "Message": "Temperature too high!",
  "Priority": "High"
}
```

---

## 📁 Import / Export Settings

* **Export** saves tag threshold configs to a `.json` file.
* **Import** restores settings for all tags from a `.json`.

---

## 🌙 Theme Support

* Toggle between light and dark themes
* Animated transition between colors
* Auto blinking of alert rows in red

---

## 📌 Notes

* Tags with GUID-style names are ignored
* The app fetches values every 10 seconds in the background
* Works with PI Web API supporting NTLM authentication
* Keep your credentials safe (do not commit to public repos)

---

## 📜 License

MIT License – free to use, modify, and distribute.

---

## 🙋 Support & Contributions

Feel free to open an issue or a pull request with improvements or fixes.

---

Let me know if you'd like:

* A sample `.json` settings file
* `.gitignore` or `requirements.txt` auto-generated
* Screenshot or GIF embed
* Packaging instructions (e.g., PyInstaller for `.exe`)
