const variables = require("./controller/variables.json")
const cdcConfig = require("./controller/cdc-config.json")
const functionData = require("./controller/function-data")


module.exports = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    ...variables,
    cdcConfig,
    ...functionData,
}