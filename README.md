# 🌐 Advanced IP Subnet Calculator

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

A comprehensive, full-stack web application for IP subnetting calculations. Supports IPv4, IPv6, VLSM (Variable Length Subnet Mask), and CIDR conversion with an intuitive tabbed interface.

## ✨ Features

### 📡 IPv4 Subnet Calculator
- **IP Class Detection** - Automatically identifies Class A, B, C, D, E
- **Network Information** - Network address, broadcast address, subnet mask
- **Host Range** - First and last usable host addresses
- **CIDR Support** - Handles CIDR notation (e.g., 192.168.1.0/24)

### 📐 VLSM Calculator
- **Dynamic Requirements** - Add multiple subnet requirements
- **Automatic Allocation** - Calculates optimal subnet sizes
- **Space Visualization** - Shows remaining address space
- **Detailed Output** - Each subnet with network/broadcast addresses

### 🌍 IPv6 Calculator
- **Full 128-bit Support** - Handles complete IPv6 address space
- **Prefix Calculations** - Custom prefix lengths
- **Subnet Generation** - Create multiple IPv6 subnets

### 🔄 CIDR Converter
- **CIDR → Subnet Mask** - Convert CIDR notation to dotted decimal
- **Subnet Mask → CIDR** - Convert subnet mask to CIDR notation
- **Real-time Conversion** - Instant results with validation



## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Adventurw/ip-subnet-calculator.git
cd ip-subnet-calculator
```
2. **Create and activate virtual environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```
3. **Install dependencies**
```bash
pip install flask flask-cors
```
4. **Run the application**
```bash
python app.py
```
5. **Open in Browser**
```bash
http://localhost:5000
```
