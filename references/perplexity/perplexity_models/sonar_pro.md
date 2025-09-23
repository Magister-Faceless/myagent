# Sonar Pro
Advanced search with enhanced search results
An advanced search model designed for complex queries, delivering deeper content understanding with enhanced search result accuracy and 2x more search results than standard Sonar.

## Features

- Non-reasoning model
- Optimized for complex, multi-step Q&A tasks
- 200K context length
- Advanced information retrieval architecture
- 2x more search results than standard Sonar
- No training on customer data

## Real World Use Cases

- Complex research questions requiring depth
- Comparative analysis across multiple sources
- Information synthesis and detailed reporting

## Python code:

import requests

url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "sonar-pro",
    "messages": [
        {"role": "user", "content": "Analyze the competitive positioning of Perplexity in the AI search market and evaluate how Comet compares to similar offerings from other companies."}
    ]
}
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

## Sample Response Metadata

{
"id": "12572668-b12a-4ce5-a697-57e22816a2ce",
"model": "sonar-pro",
"created": 1756486047,
"usage": {
  "prompt_tokens": 26,
  "completion_tokens": 832,
  "total_tokens": 858,
  "search_context_size": "low",
  "cost": {
    "input_tokens_cost": 0.0,
    "output_tokens_cost": 0.012,
    "request_cost": 0.006,
    "total_cost": 0.019
  }
},
"citations": [
  "https://explodingtopics.com/blog/perplexity-ai-stats",
  "https://opentools.ai/news/perplexity-ceo-challenges-googles-ai-strategy-in-the-browser-wars",
  "https://taptwicedigital.com/stats/perplexity",
  "https://www.leanware.co/insights/comet-perplexity-everything-you-need-to-know",
  "https://www.index.dev/blog/perplexity-statistics"
],
"search_results": [
  {
    "title": "The Latest Perplexity AI Stats (2025)",
    "url": "https://explodingtopics.com/blog/perplexity-ai-stats",
    "date": "2025-06-23",
    "last_updated": "2025-08-29",
    "snippet": "As of 2025, the AI space is valued at approximately $600 billion, with projections to increase by 500% over the next 5 years."
  },
  {
    "title": "Perplexity CEO Challenges Google's AI Strategy in the ...",
    "url": "https://opentools.ai/news/perplexity-ceo-challenges-googles-ai-strategy-in-the-browser-wars",
    "date": "2025-07-17",
    "last_updated": "2025-07-17",
    "snippet": "For example, Perplexity's AI-driven browser, Comet, represents a direct challenge to Google's traditional search engine model by prioritizing ..."
  },
  {
    "title": "7 Perplexity AI Statistics (2025): Revenue, Valuation, ...",
    "url": "https://taptwicedigital.com/stats/perplexity",
    "date": "2025-04-19",
    "last_updated": "2025-08-29",
    "snippet": "Perplexity AI holds a 6.2% market share in the AI search market. Perplexity AI is valued at $18 billion as of March 2025. Perplexity AI has ..."
  },
  {
    "title": "Comet Perplexity: Everything You Need to Know - Leanware",
    "url": "https://www.leanware.co/insights/comet-perplexity-everything-you-need-to-know",
    "date": "2025-07-25",
    "last_updated": "2025-08-28",
    "snippet": "Learn what Perplexity Comet is, how it works, and why it's changing the AI landscape, from real-world uses and tech insights to pricing, ..."
  },
  {
    "title": "50+ Perplexity AI Stats to Know in 2025",
    "url": "https://www.index.dev/blog/perplexity-statistics",
    "date": "2025-08-01",
    "last_updated": null,
    "snippet": "As of May 2025, Perplexity AI processes over 780 million monthly search queries, up from just 230 million in mid-2024. That's more than 30 ..."
  }
],
"object": "chat.completion",
"choices": [
  {
    "index": 0,
    "finish_reason": "stop",
    "message": {
      "role": "assistant",
      "content": "Perplexity occupies a rapidly expanding and influential position in the AI search market, characterized by robust user growth, significant market share, and disruptive innovation through products like the Comet browser[1][3][5]. Comet, Perplexity's AI-driven browser, stands out by favoring a user-centric, agentic browsing experience, in marked contrast to traditional browsers and search tools built around advertising ecosystems[2][4].\n\n**Competitive Positioning of Perplexity:**\n- **Market Share & Growth**: Perplexity has achieved a 6.2% market share in AI search, with an $18 billion valuation as of March 2025[3]. The platform saw visits surge from 52.4 million in March 2024 to 159.7 million in March 2025—a nearly 192% increase in monthly visitors—and now processes over 780 million monthly queries[1][5].\n- **User Base**: With approximately 15 million active monthly users, Perplexity is among the most adopted AI search platforms[1].\n- **Strategic Focus**: Its strategy centers on synthesizing information from multiple sources, rather than relying on a single proprietary index or algorithm[3].\n- **Ecosystem Independence**: By launching its own browser, Perplexity extends beyond plug-ins and integrations, directly challenging the dominance of Google (Chrome/Search), Microsoft (Edge/Bing), and Apple (Safari)[4].\n\n**Comet's Distinct Approach Compared to Competitors:**\n\n| Feature                        | Comet (Perplexity)                       | Google Chrome/Search     | Microsoft Edge/Bing     | Others (e.g., Safari, Firefox)   |\n|-------------------------------|------------------------------------------|--------------------------|------------------------|----------------------------------|\n| **Business Model**            | Subscription-based, low ad reliance      | Ad-driven               | Mixed (ads + services) | Mainly traditional browsing      |\n| **AI Integration**            | Deeply agentic, task automation          | Incipient (AI summaries)| Embedded search AI     | Limited or add-on only           |\n| **User Experience Focus**     | Automation, personalization              | Traffic/ads optimization| Integration w/ Windows | Privacy, open-source emphasis    |\n| **Ecosystem Independence**    | Fully standalone browser; own assistant  | Chrome Store dependence | Tied to Windows        | Add-ons, less AI-focused         |\n\n**Key Innovations of Comet vs. Competitors:**\n- **Agentic Browsing**: Comet enables autonomous execution of user intent—tasks beyond search, such as form completion or navigation—leveraging AI agents to streamline workflows[2][4].\n- **Contextual Awareness**: Maintains session and browsing context for more relevant, personalized assistance[4].\n- **Cross-Tab Functionality**: Performs tasks across all tabs and logged-in sites, surpassing limitations of plug-ins or browser extensions[4].\n- **User-Centric Model**: Moves away from ad-driven monetization, focusing on delivering value through direct service and subscription[2].\n\n**Competitive Landscape and Impact:**\n- **Direct Challenge to Market Leaders**: Comet attacks the core of Google's and Microsoft's value proposition, offering a radically different vision centered on user benefit rather than maximizing ad engagement[2][4].\n- **Potential Market Shift**: The shift toward premium, AI-enhanced browsing reflects growing consumer willingness to pay for advanced features, potentially leading to reduced reliance on advertising industry-wide[2].\n- **Risk and Opportunities**: While incumbents possess vast resources, Perplexity's rapid innovation and its Comet ecosystem present a legitimate threat to traditional models—if it maintains reliability and continues scaling its offerings[3][4].\n\n**Summary**\nPerplexity's Comet browser redefines competition in the AI search and browsing space by prioritizing intelligence, agentic workflows, and user-centric design over the prevailing ad-driven model. Its suite of features and rapidly growing user base set it apart from legacy offerings from Google, Microsoft, Apple, and Mozilla, positioning Perplexity as a leader in the evolving landscape of AI-powered digital information services[1][2][3][4][5]."
    },
    "delta": {
      "role": "assistant",
      "content": ""
    }
  }
]
}
