/*
 * Tool for searching the CORE API
 *
 * This module defines a Vercel‑compatible tool that allows a language
 * model to query the CORE API. The tool adheres to the CORE API v3
 * documentation as well as the conventions described in Vercel’s tool
 * calling guidelines.  It exposes a single function call that accepts
 * parameters for the entity type (works, outputs, data‑providers or
 * journals), a search query written in the CORE query language and
 * optional pagination flags.  When invoked, it performs a GET request
 * against the appropriate CORE API endpoint and returns the JSON
 * response.
 *
 * The input schema is defined using a plain JSON Schema object.  This
 * avoids requiring external dependencies such as Zod while still
 * providing structured input validation for the LLM.  Required fields
 * and allowed values mirror those defined in the CORE API
 * documentation.  Optional fields have sensible defaults applied in
 * the execute function.  All string parameters are URL encoded before
 * being appended to the request to prevent injection of unintended
 * query language constructs.
 *
 * Example usage (inside a Vercel AI SDK call):
 *
 * ```js
 * import { generateText, tool } from 'ai';
 * import searchCoreTool from './core-search-tool';
 *
 * const result = await generateText({
 *   model: 'openai/gpt-4o',
 *   tools: { searchCore: searchCoreTool },
 *   prompt: 'Find recent works about machine learning in astronomy.',
 * });
 * ```
 */

const { tool } = require('ai');

/**
 * A tool for querying the CORE API search endpoint.
 *
 * The tool accepts an object with the following properties:
 *  - `entityType` (required): one of "works", "outputs", "data-providers", or
 *    "journals".  This corresponds to the entity collections defined by
 *    CORE.  See the CORE API documentation for details on each entity.
 *  - `query` (required): a string expressed using the CORE API query
 *    language.  You may use field lookups, boolean operators, range
 *    queries and grouping as described in the CORE API documentation.
 *  - `offset` (optional): a non‑negative integer indicating the starting
 *    index of the results.  Defaults to 0 if omitted.
 *  - `limit` (optional): a positive integer indicating how many
 *    results to return.  The CORE API defaults to 10 and supports
 *    reasonable values up to 100.  Values outside of this range will
 *    be coerced to the nearest valid bound.
 *  - `scroll` (optional): a boolean flag indicating whether to use
 *    scroll pagination.  When true the CORE API returns a `scroll_id`
 *    that can be used in subsequent requests.  See the CORE API
 *    documentation for details.  Defaults to false.
 *  - `stats` (optional): a boolean flag indicating whether to include
 *    search statistics in the response.  Including statistics can slow
 *    down the response.  Defaults to false.
 */
const searchCoreTool = tool({
  description:
    'Searches the CORE API for works, outputs, data‑providers or journals.  ' +
    'Use the CORE query language in the `query` field to specify search terms.  ' +
    'Supports optional pagination and statistics flags.  Returns the raw JSON ' +
    'response from the CORE API.  See https://api.core.ac.uk/v3/docs for details.',
  // JSON schema describing the tool inputs.  This schema follows the
  // conventions outlined in the Vercel AI SDK documentation and closely
  // matches the fields accepted by the CORE API search endpoint.  The
  // `required` array ensures that both entityType and query are supplied
  // when the tool is invoked.  Enumerated values restrict entityType to
  // valid CORE entities.
  inputSchema: {
    type: 'object',
    properties: {
      entityType: {
        type: 'string',
        description:
          'The type of entity to search. Must be one of: works, outputs, data-providers, journals.',
        enum: ['works', 'outputs', 'data-providers', 'journals'],
      },
      query: {
        type: 'string',
        description:
          'Search query expressed in the CORE API query language. For example: title:"Machine Learning" AND yearPublished>=2018.',
        minLength: 1,
      },
      offset: {
        type: 'integer',
        description:
          'The result offset for pagination. Must be a non-negative integer. Defaults to 0.',
        minimum: 0,
        default: 0,
      },
      limit: {
        type: 'integer',
        description:
          'Number of results to return. Must be at least 1 and at most 100. Defaults to 10.',
        minimum: 1,
        maximum: 100,
        default: 10,
      },
      scroll: {
        type: 'boolean',
        description:
          'Whether to enable scroll pagination for large result sets. Defaults to false.',
        default: false,
      },
      stats: {
        type: 'boolean',
        description:
          'Include search statistics such as term frequencies. Note that enabling this may slow down the response. Defaults to false.',
        default: false,
      },
    },
    required: ['entityType', 'query'],
    additionalProperties: false,
  },
  /**
   * Executes a search against the CORE API.
   *
   * The function constructs a query string from the provided arguments,
   * validates and coerces optional parameters to within accepted ranges
   * and performs a GET request to the API.  If the API returns a non‑OK
   * status, an exception is thrown so that the calling agent can
   * incorporate error handling logic.  The response body is parsed as
   * JSON and returned directly.
   *
   * @param {Object} args The validated arguments passed from the tool call.
   * @param {string} args.entityType One of 'works', 'outputs', 'data-providers', or 'journals'.
   * @param {string} args.query The search query using the CORE query language.
   * @param {number} [args.offset] Optional offset for pagination.
   * @param {number} [args.limit] Optional number of results to return.
   * @param {boolean} [args.scroll] Optional flag to enable scroll pagination.
   * @param {boolean} [args.stats] Optional flag to include search statistics.
   * @param {Object} options Execution context provided by the AI SDK.  It may
   * include an abort signal used to cancel the fetch request.
   * @param {AbortSignal} [options.abortSignal] Optional abort signal forwarded
   * from generateText/streamText.  The signal is passed through to fetch.
   * @returns {Promise<any>} A promise that resolves with the JSON response from the CORE API.
   */
  async execute(
    {
      entityType,
      query,
      offset = 0,
      limit = 10,
      scroll = false,
      stats = false,
    },
    { abortSignal } = {},
  ) {
    // Ensure that optional parameters fall within documented bounds.  The CORE
    // API defaults to 10 results and may impose maximum limits on the
    // number of results returned.  Coerce values outside of these bounds to
    // the nearest valid value.
    const safeOffset = Number.isFinite(offset) && offset >= 0 ? offset : 0;
    let safeLimit = Number.isFinite(limit) && limit >= 1 ? limit : 10;
    // Hard cap the limit at 100 to avoid inadvertently requesting huge
    // responses.  The CORE API might support higher values but typical
    // usage patterns favour smaller pages.
    if (safeLimit > 100) safeLimit = 100;

    // Build query string using URLSearchParams to handle encoding.
    const params = new URLSearchParams();
    params.append('q', query);
    if (safeOffset) params.append('offset', String(safeOffset));
    params.append('limit', String(safeLimit));
    if (scroll) params.append('scroll', String(scroll));
    if (stats) params.append('stats', String(stats));

    const url = `https://api.core.ac.uk/v3/search/${encodeURIComponent(
      entityType,
    )}?${params.toString()}`;

    // Perform the HTTP GET request.  The global fetch API is available in
    // recent versions of Node.js.  AbortSignal, if provided, will abort
    // the request when triggered.  No additional headers are set here
    // because the CORE API is publicly accessible; if you have an API key
    // you can add it via an Authorization header or query parameter.
    const response = await fetch(url, {
      method: 'GET',
      signal: abortSignal,
    });

    if (!response.ok) {
      // Throw an error to ensure the caller sees a meaningful message and
      // can decide how to handle it.  Include the status code and text
      // because the CORE API returns descriptive error messages on
      // failure (e.g. rate limiting, invalid query).
      throw new Error(
        `CORE API request failed: ${response.status} ${response.statusText}`,
      );
    }

    // Attempt to parse the JSON response.  If parsing fails (which
    // indicates an unexpected response), propagate the error to the caller.
    const data = await response.json();
    return data;
  },
});

module.exports = searchCoreTool;