/**
 * @param {string} col - column name or expression
 * @returns {string} GoogleSQL expression to cast, trim, and nullify empty string
 */
function cleanString(col) {
    return `NULLIF(CAST(TRIM(${col}) AS STRING), '')`
}

/**
 * @param {string} col - column name or expression
 * @param {string} [pattern=r'[\n\r\t]'] - BigQuery raw string regex pattern to remove
 * @returns {string} GoogleSQL expression to regexp-replace, trim, cast, and nullify empty string
 */
function cleanCode(col, pattern = `r'[\\n\\r\\t]'`) {
    return `NULLIF(CAST(TRIM(REGEXP_REPLACE(${col}, ${pattern}, '')) AS STRING), '')`
}

/**
 * @param {string} col - column name containing datetime string
 * @returns {string} GoogleSQL expression that parses both '%b %d %Y %I:%M%p' and '%Y-%m-%d %H:%M:%S' formats
 */
function parseFlexibleDatetime(col) {
    return `COALESCE(
    SAFE.PARSE_DATETIME('%b %d %Y %I:%M%p', SUBSTR(${col}, 1, 19)),
    SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', SUBSTR(${col}, 1, 19))
  )`
}

/**
 * @returns {string} GoogleSQL expression to parse ASATDATE column (YYYYMMDD format) to DATE
 */
function parseAsatDate() {
    return `PARSE_DATE('%Y%m%d', ASATDATE)`
}

/**
 * @param {string} col - column name or expression
 * @returns {string} GoogleSQL expression to cast column to INT64
 */
function castInt64(col) {
    return `CAST(${col} AS INT64)`
}

/**
 * @param {string} col - column name or expression
 * @returns {string} GoogleSQL expression to cast column to FLOAT64
 */
function castFloat64(col) {
    return `CAST(${col} AS FLOAT64)`
}

module.exports = {
    cleanString,
    cleanCode,
    parseFlexibleDatetime,
    parseAsatDate,
    castInt64,
    castFloat64,
}
