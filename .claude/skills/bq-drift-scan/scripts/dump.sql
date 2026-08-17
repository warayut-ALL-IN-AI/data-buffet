-- Live view + routine definitions, one row per object.
-- Region-level INFORMATION_SCHEMA is permission-denied on this project, so every
-- dataset has to be listed explicitly. Add a dataset here when a new one appears.
SELECT table_schema AS ds, table_name AS nm, 'VIEW' AS kind, view_definition AS body
FROM `databuffet-nonprd.dimension_view`.INFORMATION_SCHEMA.VIEWS
UNION ALL SELECT table_schema, table_name, 'VIEW', view_definition
FROM `databuffet-nonprd.fact_view`.INFORMATION_SCHEMA.VIEWS
UNION ALL SELECT table_schema, table_name, 'VIEW', view_definition
FROM `databuffet-nonprd.bridge_dataset`.INFORMATION_SCHEMA.VIEWS
UNION ALL SELECT table_schema, table_name, 'VIEW', view_definition
FROM `databuffet-nonprd.onetime`.INFORMATION_SCHEMA.VIEWS
UNION ALL SELECT table_schema, table_name, 'VIEW', view_definition
FROM `databuffet-nonprd.process_dataset`.INFORMATION_SCHEMA.VIEWS
UNION ALL SELECT routine_schema, routine_name, routine_type, ddl
FROM `databuffet-nonprd.function_dataset`.INFORMATION_SCHEMA.ROUTINES
ORDER BY ds, nm

-- ---------------------------------------------------------------------------
-- Second query: last-modified per object, newest first. Anything touched after
-- the last commit for that file was edited in the console. Run separately.
-- ---------------------------------------------------------------------------
-- WITH bq AS (
--   SELECT table_schema AS ds, table_name AS nm, 'VIEW' AS kind, view_definition AS body
--   FROM `databuffet-nonprd.dimension_view`.INFORMATION_SCHEMA.VIEWS
--   UNION ALL SELECT table_schema, table_name, 'VIEW', view_definition FROM `databuffet-nonprd.fact_view`.INFORMATION_SCHEMA.VIEWS
--   UNION ALL SELECT table_schema, table_name, 'VIEW', view_definition FROM `databuffet-nonprd.bridge_dataset`.INFORMATION_SCHEMA.VIEWS
--   UNION ALL SELECT table_schema, table_name, 'VIEW', view_definition FROM `databuffet-nonprd.onetime`.INFORMATION_SCHEMA.VIEWS
--   UNION ALL SELECT table_schema, table_name, 'VIEW', view_definition FROM `databuffet-nonprd.process_dataset`.INFORMATION_SCHEMA.VIEWS
--   UNION ALL SELECT routine_schema, routine_name, routine_type, ddl FROM `databuffet-nonprd.function_dataset`.INFORMATION_SCHEMA.ROUTINES
-- ), md AS (
--   SELECT dataset_id AS ds, table_id AS nm, TIMESTAMP_MILLIS(last_modified_time) AS ts FROM `databuffet-nonprd.dimension_view.__TABLES__`
--   UNION ALL SELECT dataset_id, table_id, TIMESTAMP_MILLIS(last_modified_time) FROM `databuffet-nonprd.fact_view.__TABLES__`
--   UNION ALL SELECT dataset_id, table_id, TIMESTAMP_MILLIS(last_modified_time) FROM `databuffet-nonprd.bridge_dataset.__TABLES__`
--   UNION ALL SELECT dataset_id, table_id, TIMESTAMP_MILLIS(last_modified_time) FROM `databuffet-nonprd.onetime.__TABLES__`
--   UNION ALL SELECT dataset_id, table_id, TIMESTAMP_MILLIS(last_modified_time) FROM `databuffet-nonprd.process_dataset.__TABLES__`
--   UNION ALL SELECT routine_schema, routine_name, last_altered FROM `databuffet-nonprd.function_dataset`.INFORMATION_SCHEMA.ROUTINES
-- )
-- SELECT bq.ds, bq.nm, bq.kind, LENGTH(bq.body) AS len,
--        FORMAT_TIMESTAMP('%Y-%m-%d %H:%M', md.ts, 'Asia/Bangkok') AS last_modified
-- FROM bq LEFT JOIN md USING (ds, nm)
-- ORDER BY md.ts DESC
