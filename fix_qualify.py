import re
import sys
from pathlib import Path

def fix_sqlx_file(file_path):
    """แก้ไขไฟล์ .sqlx ให้ใช้ partition_statement แทน QUALIFY clause"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # ตรวจสอบว่ามี QUALIFY หรือไม่
    if 'QUALIFY' not in content:
        return False

    # ตรวจสอบว่ามี partition_statement อยู่แล้วหรือไม่
    if 'partition_statement' in content:
        print(f"SKIP {file_path.name} (has partition_statement)")
        return False

    # หา QUALIFY clause แบบหลายบรรทัดได้
    qualify_pattern = r'QUALIFY\s+ROW_NUMBER\(\)\s+OVER\((.*?)\)\s*=\s*1'
    qualify_match = re.search(qualify_pattern, content, re.DOTALL)

    if not qualify_match:
        print(f"WARN: No QUALIFY clause in {file_path.name}")
        return False

    qualify_clause = qualify_match.group(0)
    over_content = qualify_match.group(1).strip()

    # ดึง ORDER BY ออกมา (เก็บทั้ง ORDER BY clause)
    order_by_pattern = r'(ORDER\s+BY\s+.+?)(?=\s*\)|\s*$)'
    order_by_match = re.search(order_by_pattern, over_content, re.IGNORECASE | re.DOTALL)

    if not order_by_match:
        print(f"WARN: No ORDER BY in {file_path.name}")
        return False

    order_by_clause = order_by_match.group(1).strip()
    # ลบ newline และ whitespace ส่วนเกินออก
    order_by_clause = ' '.join(order_by_clause.split())

    # หา js block และเพิ่ม partition_statement
    js_block_pattern = r'(js\s*{[^}]*const\s+pk_key\s*=\s*[^\n]+\n)'
    js_match = re.search(js_block_pattern, content, re.DOTALL)

    if not js_match:
        print(f"WARN: No js block in {file_path.name}")
        return False

    # สร้าง partition_statement ใหม่
    partition_code = f'''
    // สร้าง partition clause เฉพาะเมื่อมี pk_key
    const partition_statement = pk_key && pk_key.length > 0
        ? `QUALIFY ROW_NUMBER() OVER(PARTITION BY ${{pk_key}} {order_by_clause}) = 1`
        : ""
'''

    # แทนที่ js block
    new_js_block = js_match.group(1) + partition_code
    content = content.replace(js_match.group(0), new_js_block)

    # แทนที่ QUALIFY clause ด้วย ${partition_statement}
    content = content.replace(qualify_clause, '${partition_statement}')

    # เขียนกลับไปที่ไฟล์
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"OK: Fixed {file_path.name}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_qualify.py <folder_path>")
        sys.exit(1)

    folder_path = Path(sys.argv[1])

    if not folder_path.exists():
        print(f"ERROR: Folder not found {folder_path}")
        sys.exit(1)

    sqlx_files = list(folder_path.glob("*.sqlx"))

    if not sqlx_files:
        print(f"WARN: No .sqlx files in {folder_path}")
        sys.exit(1)

    print(f"\nFound {len(sqlx_files)} files in {folder_path}\n")

    success_count = 0
    for file_path in sqlx_files:
        if fix_sqlx_file(file_path):
            success_count += 1

    print(f"\nDone: {success_count}/{len(sqlx_files)} files fixed")

if __name__ == "__main__":
    main()
