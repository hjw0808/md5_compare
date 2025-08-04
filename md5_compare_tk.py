import re
from pathlib import Path
from collections import defaultdict
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ===== MD5 파서 (두 포맷 지원) =====
PAT_HASH_SPACE = re.compile(r"^\s*([0-9a-fA-F]{32})\s+\*?\s*(.+?)\s*$")
PAT_BSD = re.compile(r"^\s*MD5\s*\((.+?)\)\s*=\s*([0-9a-fA-F]{32})\s*$")

def parse_md5_line(line: str):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    m = PAT_HASH_SPACE.match(line)
    if m:
        h, fn = m.group(1).lower(), m.group(2)
        return (Path(fn).name, h)
    m = PAT_BSD.match(line)
    if m:
        fn, h = m.group(1), m.group(2).lower()
        return (Path(fn).name, h)
    return None

def read_md5_file(p: Path):
    recs = []
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        for ln, line in enumerate(f, 1):
            parsed = parse_md5_line(line)
            if parsed:
                recs.append((ln, parsed[0], parsed[1]))
    return recs

def collect_master(master_path: Path):
    by_name = defaultdict(list)
    for _, fname, md5 in read_md5_file(master_path):
        by_name[fname].append(md5)
    return by_name

def collect_raw(raw_root: Path, log_fn=lambda *_: None):
    by_name = defaultdict(list)
    source = defaultdict(list)
    md5_files = list(raw_root.rglob("MD5.txt"))
    for i, md5_file in enumerate(md5_files, 1):
        log_fn(f"[scan] {i}/{len(md5_files)} {md5_file}")
        for _, fname, md5 in read_md5_file(md5_file):
            key = Path(fname).name
            by_name[key].append(md5)
            source[key].append(str(md5_file.parent))
    return by_name, source

def compare(master_map, raw_map):
    all_names = set(master_map) | set(raw_map)
    rows = []
    for name in sorted(all_names):
        m_hashes = list(dict.fromkeys(master_map.get(name, [])))
        r_hashes = list(dict.fromkeys(raw_map.get(name, [])))
        status = ""
        if name in master_map and name in raw_map:
            if len(m_hashes) > 1 or len(r_hashes) > 1:
                status = ("DUPLICATE_IN_MASTER" if len(m_hashes) > 1 else "") + \
                         (";" if len(m_hashes) > 1 and len(r_hashes) > 1 else "") + \
                         ("DUPLICATE_IN_RAW" if len(r_hashes) > 1 else "")
            if not status:
                status = "MATCH" if (m_hashes and r_hashes and m_hashes[0] == r_hashes[0]) else "MISMATCH"
        elif name in master_map:
            status = "ONLY_IN_MASTER"
        else:
            status = "ONLY_IN_RAW"
        rows.append((name, status, ",".join(m_hashes), ",".join(r_hashes)))
    return rows

def write_report(rows, source, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as w:
        w.write("filename\tstatus\tmaster_md5\traw_md5\traw_locations\n")
        for name, status, m_md5, r_md5 in rows:
            locs = ",".join(sorted(set(source.get(name, []))))
            w.write(f"{name}\t{status}\t{m_md5}\t{r_md5}\t{locs}\n")

def summarize(rows):
    counts = defaultdict(int)
    for _, status, *_ in rows:
        for s in status.split(";"):
            if s:
                counts[s] += 1
    order = ["MATCH", "MISMATCH", "ONLY_IN_MASTER", "ONLY_IN_RAW", "DUPLICATE_IN_MASTER", "DUPLICATE_IN_RAW"]
    return ", ".join([f"{k}:{counts.get(k,0)}" for k in order])

# ===== Tkinter GUI =====
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MD5 Compare (Master vs 01.RawData)")
        self.geometry("760x520")

        # Paths
        self.master_var = tk.StringVar()
        self.rawroot_var = tk.StringVar()
        self.out_var = tk.StringVar()

        # Widgets
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # Master
        row = 0
        ttk.Label(frm, text="Master MD5.txt").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.master_var, width=70).grid(row=row, column=1, padx=6, sticky="we")
        ttk.Button(frm, text="Browse", command=self.pick_master).grid(row=row, column=2)
        row += 1

        # Raw root
        ttk.Label(frm, text="Raw Root (contains 01.RawData/*/MD5.txt)").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.rawroot_var, width=70).grid(row=row, column=1, padx=6, sticky="we")
        ttk.Button(frm, text="Browse", command=self.pick_rawroot).grid(row=row, column=2)
        row += 1

        # Output
        ttk.Label(frm, text="Output report (.tsv)").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.out_var, width=70).grid(row=row, column=1, padx=6, sticky="we")
        ttk.Button(frm, text="Save As", command=self.pick_out).grid(row=row, column=2)
        row += 1

        # Run + Progress
        self.run_btn = ttk.Button(frm, text="Run Compare", command=self.on_run)
        self.run_btn.grid(row=row, column=0, pady=8, sticky="w")
        self.pb = ttk.Progressbar(frm, orient="horizontal", mode="determinate", length=400, maximum=100)
        self.pb.grid(row=row, column=1, columnspan=2, sticky="we")
        row += 1

        # Log
        self.log = tk.Text(frm, height=20)
        self.log.grid(row=row, column=0, columnspan=3, sticky="nsew")
        frm.grid_rowconfigure(row, weight=1)
        frm.grid_columnconfigure(1, weight=1)

    def pick_master(self):
        p = filedialog.askopenfilename(title="Select Master MD5.txt", filetypes=[("Text", "*.txt"), ("All","*.*")])
        if p: self.master_var.set(p)

    def pick_rawroot(self):
        d = filedialog.askdirectory(title="Select Raw Root (root containing 01.RawData)")
        if d: self.rawroot_var.set(d)

    def pick_out(self):
        p = filedialog.asksaveasfilename(title="Save report (.tsv)", defaultextension=".tsv", filetypes=[("TSV","*.tsv")])
        if p: self.out_var.set(p)

    def log_write(self, msg):
        self.log.insert("end", str(msg) + "\n")
        self.log.see("end")
        self.update_idletasks()

    def set_progress(self, val):
        self.pb["value"] = val
        self.update_idletasks()

    def on_run(self):
        master = Path(self.master_var.get()) if self.master_var.get() else None
        rawroot = Path(self.rawroot_var.get()) if self.rawroot_var.get() else None
        out = self.out_var.get()
        if not master or not master.exists():
            messagebox.showerror("Error", "Master MD5.txt 경로를 확인하세요."); return
        if not rawroot or not rawroot.exists():
            messagebox.showerror("Error", "Raw Root 폴더 경로를 확인하세요."); return
        if not out:
            out = str(master.parent / "md5_report.tsv")
            self.out_var.set(out)

        self.run_btn.config(state="disabled")
        self.pb["value"] = 0
        self.log.delete("1.0", "end")

        def job():
            try:
                self.set_progress(5); self.log_write(f"[1/4] Reading master: {master}")
                master_map = collect_master(master)

                self.set_progress(35); self.log_write(f"[2/4] Scanning raw: {rawroot}")
                raw_map, source = collect_raw(rawroot, log_fn=self.log_write)

                self.set_progress(65); self.log_write("[3/4] Comparing…")
                rows = compare(master_map, raw_map)
                summ = summarize(rows)
                self.log_write(f"Summary -> {summ}")

                out_path = Path(out)
                self.set_progress(85); self.log_write(f"[4/4] Writing report: {out_path}")
                write_report(rows, source, out_path)

                self.set_progress(100); self.log_write("[DONE] Completed.")
                messagebox.showinfo("Done", f"Report saved:\n{out_path}\n\n{summ}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.run_btn.config(state="normal")

        threading.Thread(target=job, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()


