---

# 📊 Osipivision-Scada – PI Web API Monitor

A modern Python GUI application to monitor **PI System tags** in real time using the **PI Web API**. Built with `Tkinter`, this SCADA-lite tool provides a sleek interface to track data points, define alert thresholds, and send syslog alerts when thresholds are breached.

---


## 🚀 Features

* ✨ **Real-Time Monitoring**:
  Continuously fetches and displays live data from PI Web API tags.

* 🔔 **Custom Alerts with Syslog Integration**:
  Sends alerts to a syslog server when tag values cross thresholds.

* 🌗 **Animated Dark/Light Theme Toggle**:
  Switch themes on-the-fly with smooth transitions.

* ⚙️ **Per-Tag Min/Max Settings**: 
  Configure thresholds, messages, and priority individually for each tag.

* 📝 **Export/Import Tag Configurations (JSON)**:
  Save or load settings to and from `.json` files.

* 🧠 **Built-in Logging System (viewable in GUI)**:
  View recent events, errors, and status updates directly in the app.

* 🧪 **Blinking Alerts for Out-of-Range Values**:
  Visually highlight rows that exceed defined limits with blinking red alerts.

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PJ-Hackers/Osipivision-Scada.git
cd Osipivision-Scada
```

### 2. Install Dependencies

```bash
pip install requests requests_ntlm
```

> 🐍 Python 3.9+ is recommended.
> 🧰 `tkinter` is typically bundled with Python. If not, install it based on your OS.

---

## 🛠️ Configuration

Open `main.py` and edit the following variables near the top:

```python
PI_SERVER = "your-pi-server.com"
USERNAME = "DOMAIN\\Username"
PASSWORD = "YourPassword"
SYSLOG_HOST = "192.168.1.10"
SYSLOG_PORT = 5514
POINTS_URL = f"https://{PI_SERVER}/piwebapi/dataservers/{your_key}/points"
```

🔐 **Important:** Never commit sensitive credentials to public repos.

---

## ▶️ How to Run

```bash
python main.py
```

This will launch a GUI window.

---

## 🖱️ How to Use

1. Monitor PI tags in the main table view.
2. Click on a tag to configure:

   * Minimum and maximum thresholds
   * Custom messages for alerts
   * Priority level (Critical, High, Medium, Low)
3. Click `Apply Settings` to save per-tag preferences.
4. If a tag breaches its limits:

   * It blinks red in the table.
   * A JSON-formatted syslog message is sent.
5. Use `Export`/`Import` to save and reuse settings.
6. Toggle between light and dark mode anytime.

---

## 📨 Sample Syslog Format

Syslog messages are sent over **UDP** in JSON format:

```json
{
  "Tag": "Pump1_Speed",
  "Value": 120.0,
  "Timestamp": "2025-06-13 14:30:00",
  "Severity": "Critical",
  "Condition": "Above Max",
  "Threshold": 100,
  "Message": "Pump speed too high!",
  "Priority": "High"
}
```

Make sure your syslog listener is set up to receive JSON over UDP on the specified port.

---

## 💾 Settings Import/Export

Use the `Export Settings` and `Import Settings` buttons to save/load tag configurations in `.json` format — useful for backing up or sharing threshold setups.

---

## 🌓 Theme Support

Click `Toggle Theme` to switch between **light** and **dark** modes, with smooth color transitions and GUI adaptation.

---

## 📋 Roadmap & Ideas

* [ ] Multi-user support
* [ ] Encrypted credential storage
* [ ] Email notifications
* [ ] Scheduled reports
* [ ] Better syslog customization

Want to contribute? Submit a pull request or open an issue!

---
## 🖼️ Preview

![Screenshot 2025-06-13 161944](https://github.com/user-attachments/assets/bf39c964-69eb-46e1-89ea-35dd65dbd56d)

- Syslog in ELK
![image](https://github.com/user-attachments/assets/b940a288-2e3c-4c44-8143-42ed1c2886c2)



---

## 📄 License

This software is licensed for **personal and internal use only** under a custom license.

- ❌ Commercial use, redistribution, sublicensing, and resale are **not allowed**
- ✅ You may modify and use it privately or within your organization
- ⚠️ All rights are reserved by the author

For commercial licensing or permission to redistribute, please contact: pranavdave51@gmail.com


---

## 🙌 Credits

Developed and maintained by [PJ-Hackers](https://github.com/PJ-Hackers).
Special thanks to the open-source community and OSIsoft’s PI Web API.

