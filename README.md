# 🔗 LANLink

A simple LAN-based chat application that lets devices connected to the same network communicate and share files in real time.

LANLink started as an experiment with socket programming and is being built into a lightweight local messaging app.

---

## ✨ Features

💬 **Real-time Chat**  
Send and receive messages instantly between multiple users on the same network.

👥 **Multi-user Support**  
Multiple clients can join the same chat room and communicate together.

📁 **File Sharing**  
Transfer files directly between connected users over LAN.

🟢 **Online Users**  
View currently connected users in real time.

🌙 **Desktop Interface**  
Clean dark-themed GUI built with PyQt6.

---

## 🛠️ Built With

- Python
- PyQt6
- TCP Sockets
- Multithreading
- JSON-based communication protocol

---

## ⚙️ How It Works

```
             LANLink Server
                   |
        -----------------------
        |                     |
     Client A              Client B

     Message  ------------> Message
     File     ------------> File
```

The server manages connected clients and routes messages/files between them using TCP sockets.

---

## 🚀 Getting Started

### 1. Run the server

```bash
python server.py
```

### 2. Start LANLink

```bash
python gui.py
```

Enter:

- Your username
- Server IP address

and start chatting.

---

## 📌 Current Progress

Completed:

- ✅ LAN messaging
- ✅ Multiple users
- ✅ User presence
- ✅ File transfer
- ✅ Desktop GUI

Coming next:

- 🔒 Private messaging
- 👥 Custom chat groups
- 🔍 Automatic LAN discovery
- 📦 Desktop app packaging

---

## 🎯 Goal

The goal of LANLink is to create a simple local network messenger where users can create rooms, discover nearby devices, chat, and share files without depending on an internet connection.