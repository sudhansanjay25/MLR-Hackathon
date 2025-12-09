import csv
from pathlib import Path

# Input CSV (from dt folder)
INPUT_PATH = Path("student_database.csv")

# Output files per year (written next to input)
OUTPUTS = {
    "1": INPUT_PATH.parent / "year1.csv",
    "2": INPUT_PATH.parent / "year2.csv",
    "3": INPUT_PATH.parent / "year3.csv",
    "4": INPUT_PATH.parent / "year4.csv",
}

def split_by_year(input_csv: Path):
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    with input_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        # Validate expected column presence
        if "Year of Study" not in fieldnames:
            raise ValueError("Missing 'Year of Study' column in input CSV")

        # Prepare writers per year
        writers = {}
        files = {}
        try:
            for year, out_path in OUTPUTS.items():
                out_path.parent.mkdir(parents=True, exist_ok=True)
                fp = out_path.open("w", newline="", encoding="utf-8")
                files[year] = fp
                w = csv.DictWriter(fp, fieldnames=fieldnames)
                w.writeheader()
                writers[year] = w

            # Route rows by year
            for row in reader:
                year_val = (row.get("Year of Study") or "").strip()
                if year_val in writers:
                    writers[year_val].writerow(row)
                else:
                    # Ignore unexpected year values; could log or collect
                    pass
        finally:
            for fp in files.values():
                try:
                    fp.close()
                except Exception:
                    pass

    # Return output paths for convenience
    return OUTPUTS

if __name__ == "__main__":
    outputs = split_by_year(INPUT_PATH)
    total = 0
    counts = {}
    for year, path in outputs.items():
        try:
            with path.open("r", newline="", encoding="utf-8") as f:
                r = csv.reader(f)
                # subtract header
                count = sum(1 for _ in r) - 1
                counts[year] = max(count, 0)
                total += max(count, 0)
        except FileNotFoundError:
            counts[year] = 0
    print(f"Split complete. Rows per year: {counts}, total: {total}")
