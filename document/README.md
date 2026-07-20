# Data-Buffet Documentation

เอกสารทั้งหมดของโปรเจกต์ แบ่งเป็น 2 ส่วน:
- **เอกสารสอน developer** (ไทย) — getting-started, architecture, coding-standards, how-to, operations
- **LLM Wiki** (อังกฤษ) — `project_wiki/` สำหรับทั้งคนและ AI agent ที่ทำงานกับ repo

สร้างจากการสแกนโค้ดทั้งโปรเจกต์เมื่อ **2026-07-10** — ถ้าโค้ดกับเอกสารขัดกัน
ให้เชื่อโค้ดแล้วอัปเดตเอกสาร

## เริ่มต้นที่นี่

| ลำดับ | เอกสาร | สำหรับ |
|---|---|---|
| 1 | [getting-started/onboarding.md](getting-started/onboarding.md) | developer ใหม่ — โปรเจกต์คืออะไร รันยังไง |
| 2 | [getting-started/glossary.md](getting-started/glossary.md) | คำศัพท์: SK, MdsID, medallion, QUALIFY, ... |
| 3 | [architecture/overview.md](architecture/overview.md) | ภาพรวมชั้นข้อมูล + จุดออกแบบสำคัญ |

## มาตรฐานการเขียนโค้ด

| เอกสาร | เนื้อหา |
|---|---|
| [coding-standards/sqlx-coding-standard.md](coding-standards/sqlx-coding-standard.md) | โครงไฟล์ .sqlx, config, helper, timezone, สิ่งที่ห้ามทำ |
| [coding-standards/naming-conventions.md](coding-standards/naming-conventions.md) | ชื่อไฟล์/dataset/คอลัมน์/SK/alias/tag |

## How-to (ทีละขั้น)

| งาน | เอกสาร |
|---|---|
| เพิ่มตาราง validated | [how-to/add-validated-table.md](how-to/add-validated-table.md) |
| เพิ่มตาราง curated | [how-to/add-curated-table.md](how-to/add-curated-table.md) |
| เพิ่ม dimension (mds MERGE) | [how-to/add-dimension.md](how-to/add-dimension.md) |
| เพิ่ม fact table | [how-to/add-fact-table.md](how-to/add-fact-table.md) |
| รัน / debug | [how-to/run-and-debug.md](how-to/run-and-debug.md) |

## Operations

| เอกสาร | เนื้อหา |
|---|---|
| [operations/known-issues.md](operations/known-issues.md) | คำผิดที่ห้ามแก้, พฤติกรรมตั้งใจ, หนี้เทคนิค |

## LLM Wiki — `project_wiki/`

Entry point: [project_wiki/README.md](project_wiki/README.md) (มี routing table ตามงาน)

```
project_wiki/
├── overview/      architecture.md · source-systems.md
├── includes/      databuffet-js.md · variables.md · function-data.md · cdc-config.md
├── initial/       initial-layer.md
├── validated/     validated-layer.md · source-inventory.md
├── curated/       curated-layer.md
├── dimension/     dimension-layer.md · merge-sk-pattern.md · mds-delete-pattern.md
│                  · inventory.md · special-cases.md
├── fact/          fact-layer.md
├── cdc-process/   cdc.md · process.md
└── operations/    running-and-troubleshooting.md
```

## การดูแลเอกสารชุดนี้

- แก้ pattern ใน layer ไหน → อัปเดตหน้า wiki ของ layer นั้น + how-to ที่เกี่ยว
- เพิ่ม dimension ใหม่ → เพิ่มแถวใน `project_wiki/dimension/inventory.md`
- ตัดสินใจเชิงออกแบบใหม่ (เช่น hard delete 2026-07-10) → บันทึกใน
  `operations/known-issues.md` + หน้า pattern ที่เกี่ยว
- `.claude/` ถูกสร้างใหม่ 2026-07-10 ให้ชี้เข้าเอกสารชุดนี้แล้ว (CLAUDE.md, skills,
  agents) — `knowledge/` เก่าถูกลบ ถ้าแก้ pattern ให้ใช้ skill `/update-docs` ช่วย sync
