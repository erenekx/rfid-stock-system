# MediStock — RFID Medicine Inventory System

A clean, minimal desktop application for real-time pharmaceutical inventory management using RFID technology. Built as a Software Engineering graduation project at Istanbul Okan University.

---

## Features

- **Minimal UI** — Dark-themed, distraction-free interface with clean typography and consistent spacing
- **RFID Scanning** — Hardware-agnostic architecture with EPC tag simulation for dispense and return operations
- **Real-Time Inventory** — SQLite-backed stock tracking with live updates on quantity, expiry, and batch info
- **Role-Based Access** — Separate dashboards for Administrator and Staff roles
- **Transaction Logs** — Timestamped audit trail for all inventory movements (dispense / return / add)
- **System Settings** — Configurable low-stock threshold and expiry warning period

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| GUI Framework | CustomTkinter |
| Database | SQLite3 |
| Design System | `theme.py` (centralized color palette & typography) |

## Installation

```bash
git clone https://github.com/erenekx/rfid-stock-system.git
cd rfid-stock-system
pip install -r requirements.txt
python app.py
```

## Demo Credentials

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Staff | `staff` | `staff123` |

## Design

The interface follows a minimal dark design language — pure black backgrounds, semantic accent colors, clean sans-serif typography, and subtle card-based layouts. No decorative elements; every UI element serves a function.

## License

This project is licensed under the [MIT License](LICENSE).

> This license applies to all versions and commits of this project from its inception.