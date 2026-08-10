const variables = require("./controller/variables.json")
const cdcConfig = require("./controller/cdc-config.json")
const functionData = require("./controller/function-data")


module.exports = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    MDS_BACKFILL_DAYS: dataform.projectConfig.vars.MDS_BACKFILL_DAYS,
    // fallback "1": ถ้า workspace ไหนยังไม่มี var นี้ใน workflow_settings.yaml
    // จะได้ไม่ interpolate เป็น undefined แล้วทำ SQL พังทั้ง validated/curated 74 จุด
    BACKFILL_DAYS: dataform.projectConfig.vars.BACKFILL_DAYS || "1",
    ...variables,
    cdcConfig,
    functionData,
}