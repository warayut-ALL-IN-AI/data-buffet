[33mcommit 45731bbeb75e9cc5af5a751a928ad17543069119[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mnonprod[m[33m, [m[1;31morigin/nonprod[m[33m, [m[1;31morigin/dev[m[33m, [m[1;31morigin/HEAD[m[33m)[m
Author: Warayut All in ai <warayut@dos.co.th>
Date:   Mon Dec 15 11:02:36 2025 +0000

    version 0.1.5

[1mdiff --git a/definitions/includes/controller/dependencies.json b/definitions/includes/controller/dependencies.json[m
[1mnew file mode 100644[m
[1mindex 0000000..6df3661[m
[1m--- /dev/null[m
[1m+++ b/definitions/includes/controller/dependencies.json[m
[36m@@ -0,0 +1,4 @@[m
[32m+[m[32m{[m[41m[m
[32m+[m[32m    "validated_mac5": ["validated_schema_mac5"],[m[41m[m
[32m+[m[32m    "validated_mastersku": ["validated_schema_mastersku"][m[41m[m
[32m+[m[32m}[m
\ No newline at end of file[m
[1mdiff --git a/definitions/includes/databuffet.js b/definitions/includes/databuffet.js[m
[1mindex 4317cb5..5677c37 100644[m
[1m--- a/definitions/includes/databuffet.js[m
[1m+++ b/definitions/includes/databuffet.js[m
[36m@@ -1,5 +1,7 @@[m
 const variables = require("./controller/variables.json")[m
 const primaryKeys = require("./controller/primary-keys.json")[m
[32m+[m[32mconst dependencies = require("./controller/dependencies.json")[m
[32m+[m
 [m
 ObjectDatabuffet = {[m
     DATABASE: dataform.projectConfig.defaultDatabase,[m
[36m@@ -7,6 +9,7 @@[m [mObjectDatabuffet = {[m
     REGION: dataform.projectConfig.defaultLocation,[m
     ...variables,[m
     primaryKeys,[m
[32m+[m[32m    dependencies,[m
 }[m
 [m
 global.databuffet = ObjectDatabuffet[m
\ No newline at end of file[m
[1mdiff --git a/definitions/validated_mac5/ap_s.sqlx b/definitions/validated_mac5/ap_s.sqlx[m
[1mindex 9e603e3..e5396a7 100644[m
[1m--- a/definitions/validated_mac5/ap_s.sqlx[m
[1m+++ b/definitions/validated_mac5/ap_s.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "table",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MAC5,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MAC5]],[m[41m[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MAC5]["ap_s"],[m
     bigquery: {[m
[36m@@ -18,17 +18,15 @@[m [mjs {[m
 }[m
 [m
 SELECT[m
[31m-    CAST(ap_scode AS INT64) as ap_scode,[m
[31m-    CAST(ap_snamet AS STRING) as ap_snamet,[m
[31m-    CAST(ap_snamee AS STRING) as ap_snamee,[m
[31m-    CAST(ap_scolf AS INT64) as ap_scolf,[m
[31m-    CAST(ap_scolb AS INT64) as ap_scolb,[m
[31m-    CAST(rowguid AS STRING) as rowguid[m
[31m-  [m
[32m+[m[32m  CAST(ap_scode AS INT64) AS ap_scode,[m[41m[m
[32m+[m[32m  CAST(ap_snamet AS STRING) AS ap_snamet,[m[41m[m
[32m+[m[32m  CAST(ap_snamee AS STRING) AS ap_snamee,[m[41m[m
[32m+[m[32m  CAST(ap_scolf AS INT64) AS ap_scolf,[m[41m[m
[32m+[m[32m  CAST(ap_scolb AS INT64) AS ap_scolb,[m[41m[m
[32m+[m[32m  CAST(rowguid AS STRING) AS rowguid[m[41m[m
 FROM[m
   `${project_id}.${dataset_id}.${table_id}`[m
 QUALIFY[m
[31m-  ROW_NUMBER() OVER(PARTITION BY ${pk_key} ORDER BY ap_snamet desc, ap_snamee desc) = 1[m
[31m-[m
[32m+[m[32m  ROW_NUMBER() OVER(PARTITION BY ${pk_key} ORDER BY ap_snamet DESC, ap_snamee DESC) = 1[m[41m[m
   -- pre_operations {}[m
   -- post_operations {}[m
[1mdiff --git a/definitions/validated_mac5/validate_schema_mac5.sqlx b/definitions/validated_mac5/validated_schema_mac5.sqlx[m
[1msimilarity index 60%[m
[1mrename from definitions/validated_mac5/validate_schema_mac5.sqlx[m
[1mrename to definitions/validated_mac5/validated_schema_mac5.sqlx[m
[1mindex 3bd06f5..0d8beb1 100644[m
[1m--- a/definitions/validated_mac5/validate_schema_mac5.sqlx[m
[1m+++ b/definitions/validated_mac5/validated_schema_mac5.sqlx[m
[36m@@ -1,7 +1,6 @@[m
 config {[m
[31m-  type: "operations",[m
[31m-  tags: [databuffet.TAG_VALIDATED],[m
[32m+[m[32m    type: "operations",[m[41m[m
[32m+[m[32m    tags: [databuffet.TAG_VALIDATED],[m[41m[m
 }[m
 [m
[31m-CREATE SCHEMA IF NOT EXISTS `${databuffet.DATABASE}.${databuffet.VALIDATED_SCHEMA}_${databuffet.SOURCE_MAC5}` OPTIONS(location="${databuffet.REGION}")[m
[31m-;[m
[32m+[m[32mCREATE SCHEMA IF NOT EXISTS `${databuffet.DATABASE}.${databuffet.VALIDATED_SCHEMA}_${databuffet.SOURCE_MAC5}` OPTIONS(location="${databuffet.REGION}") ;[m[41m[m
[1mdiff --git a/definitions/validated_mastersku/brand.sqlx b/definitions/validated_mastersku/brand.sqlx[m
[1mindex 599bdac..5b5db44 100644[m
[1m--- a/definitions/validated_mastersku/brand.sqlx[m
[1m+++ b/definitions/validated_mastersku/brand.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "incremental",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU]],[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MASTERSKU]["brand"],[m
     bigquery: {[m
[36m@@ -39,6 +39,5 @@[m [mWHERE[m
   ASATDATE >= FORMAT_DATE("%Y%m%d", CURRENT_DATE('Asia/Bangkok')-1)[m
 QUALIFY[m
   ROW_NUMBER() OVER(PARTITION BY ${pk_key} ORDER BY ASATDATE DESC) = 1[m
[31m-  [m
   -- pre_operations {}[m
   -- post_operations {}[m
[1mdiff --git a/definitions/validated_mastersku/category.sqlx b/definitions/validated_mastersku/category.sqlx[m
[1mindex e82483a..81b1225 100644[m
[1m--- a/definitions/validated_mastersku/category.sqlx[m
[1m+++ b/definitions/validated_mastersku/category.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "incremental",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU]],[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MASTERSKU]["category"],[m
     bigquery: {[m
[1mdiff --git a/definitions/validated_mastersku/product.sqlx b/definitions/validated_mastersku/product.sqlx[m
[1mindex 6010cb9..fbedd17 100644[m
[1m--- a/definitions/validated_mastersku/product.sqlx[m
[1m+++ b/definitions/validated_mastersku/product.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "incremental",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU]],[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MASTERSKU]["product"],[m
     bigquery: {[m
[1mdiff --git a/definitions/validated_mastersku/product_category.sqlx b/definitions/validated_mastersku/product_category.sqlx[m
[1mindex 31ca540..1c8a5fa 100644[m
[1m--- a/definitions/validated_mastersku/product_category.sqlx[m
[1m+++ b/definitions/validated_mastersku/product_category.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "incremental",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU]],[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MASTERSKU]["product_category"],[m
     bigquery: {[m
[1mdiff --git a/definitions/validated_mastersku/product_detail.sqlx b/definitions/validated_mastersku/product_detail.sqlx[m
[1mindex 639f8b0..17de55c 100644[m
[1m--- a/definitions/validated_mastersku/product_detail.sqlx[m
[1m+++ b/definitions/validated_mastersku/product_detail.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "incremental",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU]],[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MASTERSKU]["product_detail"],[m
     bigquery: {[m
[1mdiff --git a/definitions/validated_mastersku/product_group.sqlx b/definitions/validated_mastersku/product_group.sqlx[m
[1mindex 2c53a4c..5c57f67 100644[m
[1m--- a/definitions/validated_mastersku/product_group.sqlx[m
[1m+++ b/definitions/validated_mastersku/product_group.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "incremental",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU]],[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MASTERSKU]["product_group"],[m
     bigquery: {[m
[1mdiff --git a/definitions/validated_mastersku/product_group_cost_group.sqlx b/definitions/validated_mastersku/product_group_cost_group.sqlx[m
[1mindex 5c6ef8c..1027ae9 100644[m
[1m--- a/definitions/validated_mastersku/product_group_cost_group.sqlx[m
[1m+++ b/definitions/validated_mastersku/product_group_cost_group.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "incremental",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU]],[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MASTERSKU]["product_group_cost_group"],[m
     bigquery: {[m
[1mdiff --git a/definitions/validated_mastersku/validate_schema_mastersku.sqlx b/definitions/validated_mastersku/validated_schema_mastersku.sqlx[m
[1msimilarity index 100%[m
[1mrename from definitions/validated_mastersku/validate_schema_mastersku.sqlx[m
[1mrename to definitions/validated_mastersku/validated_schema_mastersku.sqlx[m
[1mdiff --git a/definitions/validated_mastersku/vendor.sqlx b/definitions/validated_mastersku/vendor.sqlx[m
[1mindex a2dad1d..67ad473 100644[m
[1m--- a/definitions/validated_mastersku/vendor.sqlx[m
[1m+++ b/definitions/validated_mastersku/vendor.sqlx[m
[36m@@ -1,7 +1,7 @@[m
 config {[m
     type: "incremental",[m
     schema: databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU,[m
[31m-    dependencies: [],[m
[32m+[m[32m    dependencies: [...databuffet.dependencies[databuffet.VALIDATED_SCHEMA + "_" + databuffet.SOURCE_MASTERSKU]],[m
     tags: [databuffet.TAG_VALIDATED],[m
     uniqueKey: databuffet.primaryKeys[databuffet.SOURCE_MASTERSKU]["vendor"],[m
     bigquery: {[m
