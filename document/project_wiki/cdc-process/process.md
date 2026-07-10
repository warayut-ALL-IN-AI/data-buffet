# Process Layer — `definitions/process/deb_address_data.sqlx`

> **LLM context**: 1 file. AI-powered Thai address parsing, gated on CDC so only
> *changed* addresses are re-parsed each day. Writes to `process_dataset.deb_address_data`;
> the companion view `process_dataset.view_deb_address_data` is what `fact_transcation`
> and `dim_customer` consume for Province/District/SubDistrict SKs.

## Config

- `type: "incremental"`, schema `process_dataset`, tag `process`
- `uniqueKey: ["company_id", "debcode"]`, `clusterBy` same (partition commented out)
- No declared `dependencies`, but **functionally gated on `cdc_dataset.cdc_change_log`**

## What it does

1. Reads `validated_mac5.deb`, concatenates `debadd1at + debadd2at + debadd3at`
   into `raw_address`.
2. Calls BigQuery **`AI.GENERATE(...)`** with model endpoint `gemini-2.5-flash`
   (temperature 0.1) and a Thai "Expert Thai Geographic Data Extractor" prompt.
3. Output struct `info`: `SubDistrictTH, SubDistrictEN, DistrictTH, DistrictEN,
   ProvinceTH, ProvinceEN`.

## CDC gating (the cost control)

```sql
WHERE EXISTS (
  SELECT 1 FROM cdc_dataset.cdc_change_log
  WHERE source_system = 'mac5'
    AND source_schema = 'validated_mac5'
    AND source_table  = 'deb'
    AND asatdate = CURRENT_DATE('Asia/Bangkok')
    AND JSON_VALUE(pk_fields, '$.debcode') = deb.debcode
    AND IFNULL(JSON_VALUE(pk_fields, '$.company_id'), 'ag01') = deb.company_id
)
```

Only customers whose address changed **today** (per CDC) hit the LLM — everything
else keeps its previously parsed value. Blank addresses are skipped.

## Why this matters

`AI.GENERATE` costs per call. Without CDC gating, every daily run would re-parse the
entire customer master. This is the reference example for "expensive derivation +
CDC gate" — reuse this pattern for any future LLM/UDF-heavy enrichment.
