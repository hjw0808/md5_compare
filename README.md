## md5_compare
A lightweight GUI tool to verify that each sample’s MD5 file matches a master MD5 list.

## Description

This software compares an individual sample’s `MD5.txt` files (one per sample in `01.RawData/*/MD5.txt`) against a single “big” `MD5.txt` (master file) from a root directory. It reports, for each filename:

- **MATCH**: hashes are identical  
- **MISMATCH**: hashes differ  
- **ONLY_IN_MASTER**: listed in master but missing in raw data  
- **ONLY_IN_RAW**: listed in raw but missing in master 
- **DUPLICATE_IN_MASTER / DUPLICATE_IN_RAW**: multiple entries for the same filename  

Results are saved as a TSV report.

## Requirements

- **Python 3.8+** (3.10–3.12 recommended)  
- Standard library only (Tkinter included by default)

## Installation

1. Clone this repository:
   ```bash
   git clone git@github.com:hjw0808/MD5_compare.git
   cd MD5_compare

2. python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
.\.venv\Scripts\activate    # Windows PowerShell

3. Command-line (no GUI)
If you prefer a purely CLI workflow, use the companion script:

```
python md5_compare.py \
  --master /path/to/master/MD5.txt \
  --raw-root /path/to/01.RawData \
  --out /path/to/md5_report.tsv



