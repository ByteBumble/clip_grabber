import sqlite3

def fix_enum_status(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE downloadjobs SET status=lower(status);")
    conn.commit()
    conn.close()
    print('Status values fixed to lowercase.')

if __name__ == "__main__":
    fix_enum_status("video_downloader.db")
