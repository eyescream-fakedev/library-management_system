# Library Management System (LMS)

A professional CLI-based library system built using **Test-Driven Development (TDD)** and **Layered Architecture**.

## 🚀 Features
- **Books**: Add, search (by title/author), and track availability.
- **Users**: Secure registration with `bcrypt` password hashing.
- **Loans**: Borrow and return books with full referential integrity.
- **Librarian Tools**: Inventory status and user management.

## 🛠 Tech Stack
- **Language**: Python 3.14+
- **Database**: SQLite3 (with Foreign Keys & Joins)
- **Security**: Bcrypt for password encryption
- **Testing**: Python `unittest` framework

## 🚦 Getting Started

### Prerequisites
- Python 3.14+
- `pip`

### Installation
1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
4. Running the App
   ```bash
   python src/lms/main.py
5. Running Tests
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)/src
   python -m unittest discover tests
