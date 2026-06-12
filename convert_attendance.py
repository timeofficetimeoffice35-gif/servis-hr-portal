#!/usr/bin/env python3
"""
AttendanceReport.csv  →  attendance_data.json
Isi folder mein AttendanceReport.csv rakhein aur run karein:
  python3 convert_attendance.py
"""
import json, sys, csv
from pathlib import Path

ROOT = Path(__file__).parent

def find_file():
    for name in ["AttendanceReport.csv", "AttendanceReport.htm",
                 "AttendanceReport.html", "AttendanceReport.xls"]:
        p = ROOT / name
        if p.exists():
            return p
    return None

def parse_html_xls(path):
    from bs4 import BeautifulSoup
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    table = soup.find_all("table")[0]
    rows = table.find_all("tr")
    data = {}
    for row in rows:
        cells = [c.get_text(strip=True) for c in row.find_all(["td","th"])]
        if len(cells) >= 23 and cells[3] and cells[3].isdigit():
            eid = cells[3].strip()
            if eid not in data:
                data[eid] = {"n": cells[4], "p": cells[5], "d": cells[6], "r": []}
            data[eid]["r"].append([cells[1], cells[12], cells[14], cells[16], cells[20], cells[22]])
    return data

def parse_csv(path):
    data = {}
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        rows = list(csv.reader(f))

    header_idx = 0
    for i, row in enumerate(rows):
        j = " ".join(row).lower()
        if ("emp id" in j or "empid" in j) and "date" in j:
            header_idx = i
            break

    headers = [h.strip().lower() for h in rows[header_idx]]

    def col_any(names, row):
        for nm in names:
            for h in headers:
                if nm in h:
                    try:
                        v = row[headers.index(h)].strip()
                        if v: return v
                    except: pass
        return ""

    for row in rows[header_idx+1:]:
        if not row or len(row) < 5: continue
        eid = col_any(["emp id","empid","employee id"], row)
        if not eid or not eid.isdigit(): continue
        emp_name = col_any(["employee name","emp name"], row)
        position = col_any(["position"], row)
        dept     = col_any(["department"], row)
        date     = col_any(["attendance date","date"], row)
        emp_in   = col_any(["emp in","in time","time in"], row)
        emp_out  = col_any(["emp out","out time","time out"], row)
        hrs      = col_any(["actual work","actual hours","work hours"], row)
        ot       = col_any(["calculated over","calc over","overtime"], row)
        remarks  = col_any(["remarks","remark"], row)

        if eid not in data:
            data[eid] = {"n": emp_name, "p": position, "d": dept, "r": []}
        data[eid]["r"].append([date, emp_in, emp_out, hrs, ot, remarks])
    return data

def main():
    f = find_file()
    if not f:
        print("ERROR: AttendanceReport.csv not found!")
        sys.exit(1)
    print(f"Processing: {f.name}")
    data = parse_html_xls(f) if f.suffix.lower() != ".csv" else parse_csv(f)
    out = ROOT / "attendance_data.json"
    with open(out, "w") as fp:
        json.dump(data, fp, separators=(',', ':'))
    print(f"Done! {len(data)} employees -> attendance_data.json")

if __name__ == "__main__":
    main()
