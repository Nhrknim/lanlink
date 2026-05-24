# LANLink

LANLink is a LAN-based real-time chat application developed using Python, PyQt6, TCP sockets, and multithreading. The application implements a client-server architecture, enabling multiple users connected to the same local network to communicate through a modern graphical interface.

The server manages concurrent client connections using dedicated threads and facilitates real-time message broadcasting between connected users. The client application provides a user-friendly interface for connecting to a server, exchanging messages, and viewing active participants through a dynamically updated online users panel.

This project demonstrates practical implementation of computer networking concepts including TCP/IP communication, socket programming, concurrent connection handling, message broadcasting, real-time data exchange, and application-layer protocol design, while also showcasing desktop application development using PyQt6.

## How to Run

### Start the Server

```bash
python server.py
```

### Start the Client

```bash
python gui.py
```

Enter a username and the server IP address, then click **Connect**.

## Current Status

### Implemented

- Real-time LAN chat
- Multi-client support
- Username-based communication
- Online users panel
- Join/leave notifications
- PyQt6 graphical interface
- Dark theme

### Planned

- File sharing
- JSON-based messaging protocol
- Private messaging
- Message encryption