const variables = require("./controller/variables.json")
const primaryKeys = require("./controller/primary-keys.json")


module.exports = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    ...variables,
    primaryKeys,
}