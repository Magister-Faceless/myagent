### Overview of CORE API v3 Capabilities
The CORE API v3 provides machine-readable access to a vast collection of open access research papers, aggregating metadata and full texts from thousands of data providers worldwide. Key resources include:

- **Works**: Represent research outputs (e.g., papers, articles) with deduplicated and enriched data, including metadata (title, authors, abstract, DOI, publication date) and full text when available.
- **Outputs**: Individual versions of research items from specific data providers.
- **Journals**: Information on journals, sourced from directories like DOAJ and Crossref.
- **Data Providers**: Details on repositories, journals, and other sources feeding into CORE.

Main features:
- Search functionality via GET and POST methods, supporting a query language similar to Elasticsearch (e.g., boolean operators, field-specific searches like title or fullText, filters for year, existence of full text).
- Retrieval of individual entities by ID.
- Advanced querying for large datasets.
- Authentication via API key (register at https://core.ac.uk/api-keys/register).
- Rate limits vary by user profile (e.g., limited for free individual users, higher for institutional/enterprise).

Endpoints (based on documentation and examples):
- GET/POST /v3/search/works: Search for works with query parameters or JSON payload for advanced filters.
- GET /v3/works/{id}: Retrieve a specific work by identifier (e.g., CORE ID or DOI).
- GET/POST /v3/search/journals: Search for journals.
- GET /v3/journals/{id}: Retrieve a specific journal.
- GET/POST /v3/search/data-providers: Search for data providers.
- GET /v3/data-providers/{id}: Retrieve a specific data provider.
- GET/POST /v3/search/outputs: Search for outputs.
- GET /v3/outputs/{id}: Retrieve a specific output.
- Additional features like full-text search (e.g., /v3/search/fulltext/{query}) and large query handling.

This API is ideal for building tools in a multi-agent system for scientific researchers, as it enables efficient data gathering for literature reviews, proposal generation, and meta-analyses by providing access to millions of papers.

### Proposed Agents and Tools for Multi-Agent AI System
Based on the CORE API's capabilities, the following agents and tools can be built. Each performs one specific function, wrapping a CORE API endpoint or feature to support the use case of enabling researchers to generate research proposals, conduct literature reviews, and automate meta-analyses with minimal prompts. In the multi-agent system, these can be called by higher-level agents (e.g., a ProposalGeneratorAgent that chains multiple tools to compile data).

Tools focus on atomic operations (e.g., search or retrieve), while agents can orchestrate simple workflows using one primary function. All require the API key for authentication.

| Name | Type | Specific Function | CORE API Usage | Relevance to Use Case |
|------|------|-------------------|----------------|-----------------------|
| LiteratureSearchTool | Tool | Performs a keyword-based search for relevant research works, returning a list of metadata (titles, authors, abstracts, DOIs). | Uses GET/POST /v3/search/works with query parameters (e.g., q="machine learning" AND year>2020) or JSON for filters like _exists_:fullText. Supports pagination via page and pageSize params. | Enables comprehensive literature reviews by fetching initial paper lists for a topic; agents can summarize or cite them in proposals/meta-analyses. |
| FullTextRetrievalTool | Tool | Retrieves the full text of a specific research work if available. | Uses GET /v3/works/{id} and extracts the fullText field or download URL from the response. | Supports in-depth analysis for meta-analyses or proposals by providing complete paper content for extraction of methods, results, or data. |
| JournalSearchTool | Tool | Searches for journals matching criteria (e.g., by name, subject, or ISSN). | Uses GET/POST /v3/search/journals with query (e.g., q="computer science") and filters like publisher or country. | Helps in research proposals by identifying suitable journals for submission; useful for literature reviews to filter high-impact sources. |
| JournalDetailsTool | Tool | Fetches detailed information on a specific journal (e.g., publisher, ISSN, metrics). | Uses GET /v3/journals/{id} to retrieve journal metadata. | Aids meta-analyses by providing context on journal quality/reliability when evaluating studies. |
| DataProviderSearchTool | Tool | Searches for data providers (e.g., repositories like arXiv or PubMed) based on name, type, or location. | Uses GET/POST /v3/search/data-providers with query (e.g., q="arXiv") and filters like oaiEndpoint or country. | Supports literature reviews by targeting specific trusted sources; useful for meta-analyses requiring data from particular repositories. |
| DataProviderDetailsTool | Tool | Retrieves details on a specific data provider (e.g., metadata quality, content volume). | Uses GET /v3/data-providers/{id} to get provider info. | Enhances proposal generation by verifying source credibility for cited works. |
| OutputSearchTool | Tool | Searches for specific output versions of works from individual providers. | Uses GET/POST /v3/search/outputs with query and filters (e.g., linked to a work ID). | Useful for meta-analyses needing multiple versions of a study (e.g., preprints vs. published) to assess evolution or consistency. |
| OutputDetailsTool | Tool | Fetches a specific output's metadata and content. | Uses GET /v3/outputs/{id} to retrieve raw output data. | Provides granular access for detailed reviews or extractions in proposals/meta-analyses. |
| AdvancedQueryAgent | Agent | Executes a complex, structured search query for large-scale data retrieval (e.g., all papers on a topic within a date range with full text). | Uses POST /v3/search/works with JSON payload for advanced query language (e.g., {"query": "(title: covid) AND year >= 2020 AND _exists_:fullText", "limit": 100}). Handles large queries via scrolling or batching as per docs. | Automates comprehensive literature reviews or meta-analysis data collection with a single refined prompt. |
| WorkDetailsAgent | Agent | Retrieves and compiles complete details for a single work, including linked outputs and full text. | Uses GET /v3/works/{id}, then optionally follows links to /v3/outputs for associated versions. | Supports proposal generation by pulling detailed paper info for citations; aids meta-analyses by gathering study specifics.