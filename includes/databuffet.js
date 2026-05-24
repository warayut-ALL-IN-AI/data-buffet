const variables = require("./controller/variables.json")
const cdcConfig = require("./controller/cdc-config.json")
const sqlHelpers = require("./sql-helpers")


module.exports = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    ...variables,
    cdcConfig,
    ...sqlHelpers,
}