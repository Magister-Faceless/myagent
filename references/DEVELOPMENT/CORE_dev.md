# CORE API v3-backed Tools for Scientific Research

This document lists concrete tools that can be implemented directly against CORE API v3. Each tool wraps a single endpoint or a small, well-defined set of endpoints. Subagents are separate from tools and should be narrowly prompted to use one or two of these tools to accomplish a specific research task.

## Works (deduplicated research works)

1. **SearchWorks**
   - What it does: Search works using CORE query language across fields like `title`, `abstract`, `fullText`, `yearPublished`, `authors`, `identifiers.doi`, etc.
   - Endpoint: `GET /v3/search/works` or `POST /v3/search/works`
   - Notes: Supports boolean operators, range queries, `_exists_` filters, `offset/limit`, `scroll`.

2. **GetWorkById**
   - What it does: Fetch one work by CORE ID or other supported identifier forms.
   - Endpoint: `GET /v3/works/{identifier}`

3. **AggregateWorks**
   - What it does: Return counts grouped by fields to support evidence synthesis and scoping (e.g., trend and distribution analysis).
   - Endpoint: `POST /v3/search/works/aggregate`
   - Common fields: `yearPublished`, `authors`, `documentType`, `publishedDate`, `language`, `publisher`, `dataProvider`, `fieldOfStudy`.

4. **ScrollSearchWorks**
   - What it does: Retrieve very large result sets in batches for systematic reviews and meta-analyses.
   - Endpoint: `POST /v3/search/works` with `scroll=true`

5. **FindWorksByDOI**
   - What it does: Convenience wrapper to find works by DOI (or list of DOIs) using field lookup.
   - Endpoint: `GET/POST /v3/search/works` with `q=identifiers.doi:"..."`

6. **FilterWorksWithFullText**
   - What it does: Search only works that have full text available.
   - Endpoint: `GET/POST /v3/search/works` with `_exists_:fullText` (or `fulltext_status` where applicable)

## Outputs (provider-specific manifestations)

7. **SearchOutputs**
   - What it does: Search outputs by title, subjects, documentType, publishedDate, etc.; optionally filtered by linked work.
   - Endpoint: `GET /v3/search/outputs` or `POST /v3/search/outputs`

8. **GetOutputById**
   - What it does: Fetch a single output by ID.
   - Endpoint: `GET /v3/outputs/{identifier}`

9. **AggregateOutputs**
   - What it does: Summarize output distributions for scoping reviews.
   - Endpoint: `POST /v3/search/outputs/aggregate`
   - Common fields: `documentType`, `subjects`, `language`, `publishedDate`, `authors`.

## Journals

10. **SearchJournals**
    - What it does: Find journals by name, subject, ISSN, or publisher.
    - Endpoint: `GET /v3/search/journals` or `POST /v3/search/journals`

11. **GetJournalById**
    - What it does: Fetch details for a single journal (supports `issn:` prefix).
    - Endpoint: `GET /v3/journals/{identifier}`

12. **AggregateJournals**
    - What it does: Summarize journals by supported fields.
    - Endpoint: `POST /v3/search/journals/aggregate`
    - Common fields: `subjects`.

## Data Providers

13. **SearchDataProviders**
    - What it does: Discover repositories and sources (e.g., arXiv, institutional repos) by name, country, OAI endpoint, etc.
    - Endpoint: `GET /v3/search/data-providers` or `POST /v3/search/data-providers`

14. **GetDataProviderById**
    - What it does: Retrieve one data provider by ID.
    - Endpoint: `GET /v3/data-providers/{identifier}`

15. **AggregateDataProviders**
    - What it does: Summarize providers by supported fields (e.g., `software`).
    - Endpoint: `POST /v3/search/data-providers/aggregate`

## Researcher-focused derived utilities (built on the above endpoints)

16. **TimeTrendAnalysis**
    - What it does: Topic trend over time by aggregating `yearPublished` for a given query.
    - Backed by: `AggregateWorks`

17. **SubjectDistribution**
    - What it does: Distribution of subjects for a topic to scope fields and subfields.
    - Backed by: `AggregateWorks` (or `AggregateOutputs` where subjects are richer)

18. **TopVenuesForTopic**
    - What it does: Identify frequent publishers/journals for a query.
    - Backed by: `AggregateWorks` (fields: `publisher`) and `SearchJournals`

19. **AuthorFrequencyForTopic**
    - What it does: Identify prolific authors in a niche for expert mapping and potential case-series builders.
    - Backed by: `AggregateWorks` (field: `authors`)

20. **BatchGetWorksByIds**
    - What it does: Convenience helper to fetch many works sequentially after a scroll run.
    - Backed by: `GetWorkById`

21. **SystematicSearchTemplates**
    - What it does: Prebuilt query composers for common designs (e.g., RCTs, cohort, case-control, case series) using document type/keyword patterns.
    - Backed by: `SearchWorks`, optional `FilterWorksWithFullText`

22. **DeduplicateByDOI**
    - What it does: Post-processing helper to deduplicate results using `identifiers.doi`.
    - Backed by: Fields from `SearchWorks`/`SearchOutputs`

23. **ScrollExportWorks**
    - What it does: End-to-end scroller that pages through results and returns normalized records ready for screening or extraction.
    - Backed by: `ScrollSearchWorks`

---

## Notes on subagents (deepagents)

- Tools are API wrappers. Subagents are spawnable, narrowly focused agents configured with:
  - A very specific prompt for a single task.
  - A minimal toolset (ideally 1–2 of the tools above) to execute that task efficiently.
- Subagents do not respond to the user directly; they return results to the main agent.
- Example pairings:
  - Literature Screener subagent → `SearchWorks` + `ScrollExportWorks`.
  - Trend Analyst subagent → `TimeTrendAnalysis` + `SubjectDistribution`.
  - Venue Scout subagent → `TopVenuesForTopic` + `SearchJournals`.
  - Data Collector for Meta-Analysis → `SystematicSearchTemplates` + `FilterWorksWithFullText` + `BatchGetWorksByIds`.

This aligns with deepagents guidance in `backend/deepagents.README.md`: keep subagent prompts focused and tool lists short, and let the main agent orchestrate when to spawn them.
