const variables = require("./controller/variables.json")
const cdcConfig = require("./controller/cdc-config.json")


module.exports = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    ...variables,
    cdcConfig
}