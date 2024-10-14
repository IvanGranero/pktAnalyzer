# pktLogger

The pktLogger repository by IvanGranero is a tool for logging and analyzing network packets. It uses the `scapy` library to capture and inspect packets on a network interface. The repository includes several Python scripts, each handling different aspects of packet logging and analysis:
# pktLogger

pktLogger is a tool for logging and analyzing CAN bus data efficiently. This project supports various file formats and provides real-time analysis capabilities.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [File Formats Supported](#file-formats-supported)
- [Contributing](#contributing)
- [License](#license)

### Features

- Real-time CAN bus data logging.
- Support for various file formats (log, CSV, Parquet).
- Multi-threaded data processing for efficiency.
- Data visualization and analysis.

### Prerequisites

- Python 3.x
- `scapy` library
- `pandas` library
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
