#!/usr/bin/env python3
"""
LeaveReport.csv  →  leave_data.json
Isi folder mein LeaveReport.csv rakhein aur run karein:
  python3 convert_leave.py
"""
import json, sys, csv
from pathlib import Path

ROOT = Path(__file__).parent

def find_file():
    for name in ["LeaveReport.csv", "LeaveReport.htm",
                 "LeaveReport.html", "LeaveReport.xls"]:
        p = ROOT / name
        if p.exists():
            return p
    return None

def parse_html_xls(path):
    from bs4 import BeautifulSoup
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")
    data = {}
    for row in rows[3:]:
        cells = [c.get_text(strip=True) for c in row.find_all(["td","th"])]
        if len(cells) >= 17 and cells[3] and cells[3].isdigit():
            eid = cells[3].strip()
            data[eid] = {
                "emp_id": eid, "emp_name": cells[2],
                "position_name": cells[4], "doj": cells[5],
                "casual_allowed": cells[6], "casual_availed": cells[7],
                "casual_deducted": cells[8], "casual_closing": cells[9],
                "sick_allowed": cells[10], "sick_availed": cells[11],
                "sick_deducted": cells[12], "sick_closing": cells[13],
                "annual_allowed": cells[14], "annual_availed": cells[15],
                "annual_deducted": cells[16] if len(cells)>16 else "0",
                "annual_closing": cells[17] if len(cells)>17 else "0",
            }
    return data

def parse_csv(path):
    data = {}
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        rows = list(csv.reader(f))

    header_idx = None
    for i, row in enumerate(rows):
        j = " ".join(row).lower()
        if ("emp id" in j or "empid" in j) and "employee name" in j:
            header_idx = i
            break
    if header_idx is None:
        header_idx = 0

    headers = [h.strip().lower() for h in rows[header_idx]]

    def col(h, row):
        try: return row[headers.index(h)].strip()
        except: return ""

    def lcol(prefix, suffix, row):
        for h in headers:
            if prefix in h and suffix in h:
                try: return row[headers.index(h)].strip()
                except: pass
        return "0"

    for row in rows[header_idx+1:]:
        if not row or len(row) < 5: continue
        eid = col("emp id", row) or col("empid", row) or col("employee id", row)
        if not eid or not eid.isdigit(): continue
        data[eid] = {
            "emp_id": eid,
            "emp_name": col("employee name", row) or col("emp name", row),
            "position_name": col("position name", row) or col("position", row),
            "doj": col("doj", row) or col("date of joining", row),
            "casual_allowed":  lcol("casual","allow",row),
            "casual_availed":  lcol("casual","avail",row),
            "casual_deducted": lcol("casual","ded",row),
            "casual_closing":  lcol("casual","clos",row),
            "sick_allowed":    lcol("sick","allow",row),
            "sick_availed":    lcol("sick","avail",row),
            "sick_deducted":   lcol("sick","ded",row),
            "sick_closing":    lcol("sick","clos",row),
            "annual_allowed":  lcol("annual","allow",row),
            "annual_availed":  lcol("annual","avail",row),
            "annual_deducted": lcol("annual","ded",row),
            "annual_closing":  lcol("annual","clos",row),
        }
    return data

def main():
    f = find_file()
    if not f:
        print("ERROR: LeaveReport.csv not found!")
        sys.exit(1)
    print(f"Processing: {f.name}")
    data = parse_html_xls(f) if f.suffix.lower() != ".csv" else parse_csv(f)
    out = ROOT / "leave_data.json"
    with open(out, "w") as fp:
        json.dump(data, fp, separators=(',', ':'))
    print(f"Done! {len(data)} employees -> leave_data.json")

if __name__ == "__main__":
    main()
