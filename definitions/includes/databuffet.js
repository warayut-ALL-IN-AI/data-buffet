const variables = require("./controller/variables.json")
const primaryKeys = require("./controller/primary-keys.json")

ObjectDatabuffet = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    ...variables,
    primaryKeys,
}

global.databuffet = ObjectDatabuffet