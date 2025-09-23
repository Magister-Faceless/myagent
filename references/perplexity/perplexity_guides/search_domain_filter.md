# Search Domain Filter Guide

<Note>
  The `search_domain_filter` feature allows you to limit search results to specific domains/URLs or exclude certain domains/URLs from search results. This supports both broad domain-level filtering and granular URL-level filtering for precise content control.
</Note>

<Warning>
  You can add a maximum of 20 domains or URLs to the `search_domain_filter` list. The filter works in either allowlist mode (include only) or denylist mode (exclude), but not both simultaneously.
</Warning>

<Warning>
  Before adding URLs to your allowlist, test that they are accessible via the API by making a sample request. URLs that are blocked, require authentication, or have access restrictions may not return search results, which can significantly impact response quality when using allowlist mode.
</Warning>

## Overview

The `search_domain_filter` parameter allows you to control which websites are included in or excluded from the search results used by the Sonar models. This feature is particularly useful when you want to:

* Restrict search results to trusted sources
* Filter out specific domains from search results
* Focus research on particular websites

Enabling domain filtering can be done by adding a `search_domain_filter` field in the request:

```
"search_domain_filter": [
  "<domain1>",
  "<domain2>",
  ...
]
```

Each entry in the list can be a domain name or a specific URL. The filter operates in two modes:

* **Allowlist mode**: Include only the specified domains/URLs (no `-` prefix)
* **Denylist mode**: Exclude the specified domains/URLs (use `-` prefix)

## Filtering Capabilities

### Domain-Level Filtering

Filter entire domains for broad control:

```json
// Allowlist: Only search these domains
"search_domain_filter": ["wikipedia.org", "github.com", "stackoverflow.com"]

// Denylist: Exclude these domains  
"search_domain_filter": ["-reddit.com", "-pinterest.com", "-quora.com"]
```

### URL-Level Filtering

Target specific pages or sections for granular control:

```json
// Allowlist: Only search these specific URLs
"search_domain_filter": [
  "https://en.wikipedia.org/wiki/Chess",
  "https://stackoverflow.com/questions/tagged/python",
  "https://docs.python.org/3/tutorial/"
]

// Denylist: Exclude these specific URLs
"search_domain_filter": [
  "-https://en.wikipedia.org/wiki/FIDE_rankings",
  "-https://reddit.com/r/politics"
]
```

This granular approach allows you to:

* Include or exclude specific Wikipedia articles while keeping/removing the rest
* Target particular sections of large sites like Stack Overflow or Reddit
* Filter specific documentation pages or subdirectories

## Examples

### 1. Allowlist Specific Domains

This example shows how to limit search results to only include content from specific domains.

**Request**

<CodeGroup>
  ```bash cURL
  curl --request POST \
    --url https://api.perplexity.ai/chat/completions \
    --header "Authorization: Bearer YOUR_API_KEY" \
    --header "Content-Type: application/json" \
    --data '{
      "model": "sonar",
      "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about the James Webb Space Telescope discoveries."}
      ],
      "search_domain_filter": [
        "nasa.gov",
        "wikipedia.org",
        "space.com"
      ]
    }' | jq
  ```

  ```python python
  import requests

  url = "https://api.perplexity.ai/chat/completions"
  headers = {"Authorization": "Bearer YOUR_API_KEY"}
  payload = {
      "model": "sonar-reasoning-pro",
      "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Tell me about the James Webb Space Telescope discoveries."}
      ],
      "search_domain_filter": [
          "nasa.gov",
          "wikipedia.org",
          "space.com"
      ]
  }

  response = requests.post(url, headers=headers, json=payload).json()
  print(response["choices"][0]["message"]["content"])
  ```
</CodeGroup>

**Best Practice**: Use simple domain names (e.g., `wikipedia.org`) without additional elements like `https://` or `www.` prefixes.

### 2. Denylist Specific Domains

This example shows how to exclude specific domains from search results by prefixing the domain name with a minus sign (`-`).

**Request**

<CodeGroup>
  ```bash cURL
  curl --request POST \
    --url https://api.perplexity.ai/chat/completions \
    --header "Authorization: Bearer YOUR_API_KEY" \
    --header "Content-Type: application/json" \
    --data '{
      "model": "sonar",
      "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the latest advancements in renewable energy?"}
      ],
      "search_domain_filter": [
        "-pinterest.com",
        "-reddit.com",
        "-quora.com"
      ]
    }' | jq
  ```

  ```python python
  import requests

  url = "https://api.perplexity.ai/chat/completions"
  headers = {"Authorization": "Bearer YOUR_API_KEY"}
  payload = {
      "model": "sonar-deep-research",
      "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "What are the latest advancements in renewable energy?"}
      ],
      "search_domain_filter": [
          "-pinterest.com",
          "-reddit.com",
          "-quora.com"
      ]
  }

  response = requests.post(url, headers=headers, json=payload).json()
  print(response["choices"][0]["message"]["content"])
  ```
</CodeGroup>

**Best Practice**: Use simple domain names with a minus prefix (e.g., `-pinterest.com`) to exclude domains from search results.

### 3. URL-Level Filtering for Granular Control

This example shows how to exclude specific pages while keeping the rest of the domain accessible.

**Request**

<CodeGroup>
  ```bash cURL
  curl --request POST \
    --url https://api.perplexity.ai/chat/completions \
    --header "Authorization: Bearer YOUR_API_KEY" \
    --header "Content-Type: application/json" \
    --data '{
      "model": "sonar-pro",
      "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about chess rankings and tournaments."}
      ],
      "search_domain_filter": [
        "-https://en.wikipedia.org/wiki/FIDE_rankings"
      ]
    }' | jq
  ```

  ```python python
  import requests

  url = "https://api.perplexity.ai/chat/completions"
  headers = {"Authorization": "Bearer YOUR_API_KEY"}
  payload = {
      "model": "sonar-pro",
      "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Tell me about chess rankings and tournaments."}
      ],
      "search_domain_filter": [
          "-https://en.wikipedia.org/wiki/FIDE_rankings"
      ]
  }

  response = requests.post(url, headers=headers, json=payload).json()
  print(response["choices"][0]["message"]["content"])
  ```
</CodeGroup>

**Result**: This will search all websites except the specific FIDE rankings Wikipedia page, while keeping all other Wikipedia content accessible.

**Alternative - Allowlist specific URLs only:**

```json
"search_domain_filter": [
  "https://en.wikipedia.org/wiki/Chess",
  "https://en.wikipedia.org/wiki/World_Chess_Championship",
  "https://chess.com"
]
```

This would only search those three specific sources and ignore all other websites.

## Best Practices

### Domain and URL Specification

* **Domain filtering**: Use simple domain names (e.g., `example.com`) without protocol prefixes for broad filtering.
* **URL filtering**: Use complete URLs including protocol (e.g., `https://en.wikipedia.org/wiki/FIDE_rankings`) for specific page targeting.
* **Subdomain behavior**: Using a main domain (e.g., `nytimes.com`) will filter all subdomains as well.
* **Granular control**: URL-level filtering allows you to include/exclude specific pages while keeping the rest of the domain.

### Filter Optimization

* **Be specific**: Use domains/URLs that are most relevant to your query to get the best results.
* **Choose your mode**: Use either allowlist mode (include only) OR denylist mode (exclude), but not both in the same request.
* **Limit filter size**: You can add up to 20 domains or URLs. Using fewer, more targeted entries often yields better results.
* **URL precision**: Use full URLs (including `https://`) when targeting specific pages for maximum precision.

### Performance Considerations

* Adding domain filters may slightly increase response time as the search engine needs to apply additional filtering.
* Overly restrictive domain filters might result in fewer search results, potentially affecting the quality of the response.
