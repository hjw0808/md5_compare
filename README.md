## md5_compare
A lightweight GUI tool to verify that each sample’s MD5 file matches a master MD5 list.

This tool is specifically designed to ensure maximum compatibility with the NOVEGENE pipeline.

Case-Sensitive Extension: The file extension match is case-sensitive, so the extension must be exactly MD5.txt to be recognized.

## Installation  
### Running on macOS

1. Download and unzip the ZIP.  
2. Open the `dist` folder.  
3. Double-click **MD5 Compare.app** to launch the program.  

*(Optional: Drag **MD5 Compare.app** into your Applications folder for easier access.)*

Or just simply
```python
python md5_compare_tk.py
```

## Result Description

This software compares an individual sample’s `MD5.txt` files (one per sample in `01.RawData/*/MD5.txt`) against a single “big” `MD5.txt` (master file) from a root directory. It reports, for each filename:

- **MATCH**: hashes are identical  
- **MISMATCH**: hashes differ  
- **ONLY_IN_MASTER**: listed in master but missing in raw data  
- **ONLY_IN_RAW**: listed in raw but missing in master 
- **DUPLICATE_IN_MASTER / DUPLICATE_IN_RAW**: multiple entries for the same filename  

Results are saved as a TSV report.





