````markdown
# 🎵 Discord **JunixMusicBOT**

Ein einfacher Musikbot für Discord mit klassischen `!`-Befehlen, um Musik über YouTube abzuspielen. Perfekt für private Server, Freunde oder Communities.

---

## 📥 Installation

1. Stelle sicher, dass Python **3.8+** installiert ist.  
2. Installiere die Abhängigkeiten mit folgendem Befehl:

```bash
pip install -U discord.py
pip install -U yt-dlp
pip install -U ffmpeg-python
pip install -U pynacl
pip install -U python-dotenv
````

3. Stelle sicher, dass **FFmpeg** auf deinem System installiert ist:

* **Linux (Ubuntu/Debian):**

  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```

---

## ⚙️ Discord Bot-Einstellungen (Wichtig!)

Damit der Bot richtig funktioniert, müssen im [Discord Developer Portal](https://discord.com/developers/applications) folgende Einstellungen aktiviert sein:

### ✅ Erforderliche Privilegierte Gateway-Intents:

* `✔️ PRESENCE INTENT`
* `✔️ SERVER MEMBERS INTENT`
* `✔️ MESSAGE CONTENT INTENT`

📸 Beispiel:
![Bot Einstellungen Screenshot](https://i.imgur.com/5Ijbm61.png)

---

## 🚀 Befehle

### 🎵 Musik-Befehle

| Befehl            | Beschreibung                                      |
| ----------------- | ------------------------------------------------- |
| `!play <ID/URL>`  | Spielt Musik von YouTube ab                       |
| `!pause`          | Pausiert die Wiedergabe                           |
| `!resume`         | Setzt die Wiedergabe fort                         |
| `!stop`           | Stoppt die Wiedergabe und leert die Warteschlange |
| `!skip`           | Überspringt das aktuelle Lied                     |
| `!volume <0-100>` | Ändert die Lautstärke                             |
| `!queue`          | Zeigt die aktuelle Warteschlange                  |
| `!list`           | Zeigt alle gespeicherten lokalen Sounds           |
| `!clear`          | Leert die Warteschlange                           |

### ⚙️ Allgemeine Befehle

| Befehl   | Beschreibung                     |
| -------- | -------------------------------- |
| `!join`  | Bot tritt deinem Sprachkanal bei |
| `!leave` | Bot verlässt den Sprachkanal     |
| `!ping`  | Zeigt die aktuelle Bot-Latenz    |

---

## 🔗 Bot Invite

👉 Nutze diesen Link, um den Bot zu deinem Server hinzuzufügen:
**[Hier klicken](https://discord.com/oauth2/authorize?client_id=DEIN_CLIENT_ID&permissions=3147776&scope=bot)**
*(Ersetze `DEIN_CLIENT_ID` mit der tatsächlichen Client-ID deines Bots)*

---

## 📧 Support

**Braucht ihr Hilfe? Kein Problem!**

📨 E-Mail: [hilfe@junixfx.de](mailto:hilfe@junixfx.de)
🌐 Discord-Server: [https://discord.gg/ESp2cJSYQz](https://discord.gg/ESp2cJSYQz)

---

## 🛠️ Hinweise für Entwickler

Du kannst die GitHub-Repository-Funktionen deaktivieren oder die Version manuell ändern. Oder lösche einfach diesen Block, wenn du das nicht brauchst 😄

---

## 🧾 Lizenz

```
Copyright 2025 by @junixcodingfx aka @Jonathan.T

Alle Rechte vorbehalten. Änderung nur mit Genehmigung.
```

```
