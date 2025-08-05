## md5_compare
A lightweight GUI tool to verify that each sample’s MD5 file matches a master MD5 list.

This tool is specifically designed to ensure maximum compatibility with the NOVEGENE pipeline.

Case-Sensitive Extension: The file extension match is case-sensitive, so the extension must be exactly MD5.txt to be recognized.

## Installation  
### Running on macOS

When a security warning pops up while trying to open the app, with a message <"MD5 Compare" Not opened>,
click "Done" or "Cancel" to close the warning dialog.
Go to System Settings > Privacy & Security.
Scroll down — you’ll see a message like “[App Name] was blocked from use because it is not from an identified developer.”
Click the "Open Anyway" button, and authenticate.

1. Once it is downloaded properly, unzip the file.  
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






