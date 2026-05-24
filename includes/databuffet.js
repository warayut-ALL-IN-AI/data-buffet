const variables = require("./controller/variables.json")
const cdcConfig = require("./controller/cdc-config.json")


module.exports = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    ...variables,
    cdcConfig,

    // SQL generation helpers
    cleanString: (col) =>
        `NULLIF(CAST(TRIM(${col}) AS STRING), '')`,

    cleanCode: (col, pattern = `r'[\\n\\r\\t]'`) =>
        `NULLIF(CAST(TRIM(REGEXP_REPLACE(${col}, ${pattern}, '')) AS STRING), '')`,

    parseFlexibleDatetime: (col) =>
        `COALESCE(\n    SAFE.PARSE_DATETIME('%b %d %Y %I:%M%p', SUBSTR(${col}, 1, 19)),\n    SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', SUBSTR(${col}, 1, 19))\n  )`,

    parseAsatDate: () =>
        `PARSE_DATE('%Y%m%d', ASATDATE)`,

    castInt64: (col) =>
        `CAST(${col} AS INT64)`,

    castFloat64: (col) =>
        `CAST(${col} AS FLOAT64)`,
}