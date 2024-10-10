# pktLogger

The pktLogger repository by IvanGranero is a tool for logging and analyzing network packets. It uses the `scapy` library to capture and inspect packets on a network interface. The repository includes several Python scripts, each handling different aspects of packet logging and analysis:

- **`ethernetPkts.py`**: Handles Ethernet packet capture and processing.
- **`converterTool.py`**: Converts packet data into a different format.
- **`cudfPkts.py`**: Uses cuDF (a GPU-accelerated DataFrame library) for packet analysis.
- **`logThread.py`**: Manages logging of packet data in a separate thread.
- **`pktLogger.py`**: The main script that orchestrates packet capture and logging.
- **`aiPrompt.py`**: Likely handles some form of AI-based analysis or prompt generation.
- **`canPkts.py`**: Handles CAN (Controller Area Network) packets.

## Getting Started

### Prerequisites

- Python 3.x
- `scapy` library
- `pandas` library (optional, if you use DataFrame operations)
- `cuDF` library (optional, if you use GPU-accelerated DataFrames)

### Installation

Clone the repository:
```bash
git clone https://github.com/IvanGranero/pktLogger.git
cd pktLogger
```
Install the required libraries:
```bash
pip install -r requirements.txt
```

### Usage
Run the main logging script:
```bash
python pktLogger.py
```
Additional scripts can be run individually based on your specific needs:
```bash
python ethernetPkts.py
python converterTool.py
python cudfPkts.py
```

### Contributing
Feel free to submit issues and pull requests. For major changes, please open an issue first to discuss what you would like to change.

### License
This project is licensed under the MIT License - see the LICENSE file for details.
