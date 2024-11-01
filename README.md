# pktAnalyzer

The pkAnalyzer repository by IvanGranero is a powerful tool for logging and analyzing CAN bus and Ethernet data. It supports various file formats, provides real-time analysis capabilities, and leverages AI for advanced data analysis.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [File Formats Supported](#file-formats-supported)
- [Contributing](#contributing)
- [License](#license)

### Features

- AI analysis to enhance its functionality.
- Real-time CAN bus data logging.
- Support for various file formats (log, pcap, csv, parquet).
- Multi-threaded data processing for efficiency.
- Strings search
- Data visualization and analysis.

AI enhanced filtering and analysis
![image](https://github.com/user-attachments/assets/b618dba8-6ced-47a8-a173-3fc9a7252989)

Strings search
![image](https://github.com/user-attachments/assets/9ed06d14-3901-4eef-adb5-d2f529d32d7b)
AI enhanced search
![image](https://github.com/user-attachments/assets/8b412d4b-969c-4ef5-8e68-b85298b46024)
![image](https://github.com/user-attachments/assets/374f9195-b49d-4703-b5a3-18dc2af2ccfe)

Data visualization
![image](https://github.com/user-attachments/assets/e0021675-13c9-4b75-81b6-7429601d8b45)


### Prerequisites

- Python 3.x
- `scapy` library
- `pandas` library
- `cuDF` library (optional, if you use GPU-accelerated DataFrames)

### Installation

Clone the repository:
```bash
git clone https://github.com/IvanGranero/pktAnalyzer.git
cd pktAnalyzer
```
Install the required libraries:
```bash
pip install -r requirements.txt
```

### Usage
Run the main logging script:
```bash
python pktAnalyzer.py
```

### File Formats Supported

    log: CAN log files with detailed timestamps and flags.
    
    pcap: supports reading pcap files, making it easier to analyze pre-captured traffic.
    
    CSV: Comma-separated values for structured data logging.

    Parquet: Efficient columnar storage file format.


### Contributing
Feel free to submit issues and pull requests. For major changes, please open an issue first to discuss what you would like to change.

### License
This project is licensed under the MIT License.
