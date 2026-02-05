import os, json, sqlite3, shutil
from pathlib import Path

def get_profile_path():
    base = Path(os.getenv("LOCALAPPDATA")) / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default"
    return base if base.exists() else None

def copy_db(src):
    temp = Path(os.getenv("TEMP")) / f"{src.name}.copy"
    shutil.copy2(src, temp)
    return temp

def extract_history(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 200")
    rows = cursor.fetchall()
    conn.close()
    return [{"url": r[0], "title": r[1], "visits": r[2], "timestamp": r[3]} for r in rows]

def extract_autofill(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, value, count FROM autofill ORDER BY count DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [{"field": r[0], "value": r[1], "count": r[2]} for r in rows]

def extract_logins(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, date_created FROM logins ORDER BY date_created DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [{"site": r[0], "username": r[1], "created": r[2]} for r in rows]

def main():
    profile = get_profile_path()
    if not profile:
        print("❌ Brave profile not found.")
        return

    output = {}

    try:
        hist_db = copy_db(profile / "History")
        output["history"] = extract_history(hist_db)
    except Exception as e:
        output["history"] = f"error: {e}"

    try:
        autofill_db = copy_db(profile / "Web Data")
        output["autofill"] = extract_autofill(autofill_db)
    except Exception as e:
        output["autofill"] = f"error: {e}"

    try:
        login_db = copy_db(profile / "Login Data")
        output["logins"] = extract_logins(login_db)
    except Exception as e:
        output["logins"] = f"error: {e}"

    out_path = Path(os.getenv("TEMP")) / "brave_behavior.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print(f"✅ Extract complete. Output saved to: {out_path}")

if __name__ == "__main__":
    main()
