const variables = require("./controller/variables.json")
const primaryKeys = require("./controller/primary-keys.json")
const dependencies = require("./controller/dependencies.json")


ObjectDatabuffet = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    ...variables,
    primaryKeys,
    dependencies,
}

global.databuffet = ObjectDatabuffet