# Sonar Reasoning Pro
Advanced reasoning with enhanced multi-step analysis
A high-performance reasoning model leveraging advanced multi-step Chain-of-Thought (CoT) reasoning and enhanced information retrieval for complex problem-solving.

## Features

- Advanced reasoning model
- Enhanced Chain-of-Thought (CoT) reasoning
- 128K context length
- Best for complex multi-step reasoning tasks
- 2x more search results than Sonar Reasoning
- No training on customer data

## Real World Use Cases

- Complex multi-step analysis and reasoning
- Advanced research with deep reasoning
- Strategic decision making with comprehensive analysis

## Python Code:
import requests

url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "sonar-reasoning-pro",
    "messages": [
        {"role": "user", "content": "Analyze the feasibility of fusion energy becoming a mainstream power source by 2040."}
    ]
}
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

## Think section
The sonar-reasoning-pro model is designed to output a <think> section containing reasoning tokens, immediately followed by a valid JSON object. As a result, the response_format parameter does not remove these reasoning tokens from the output. We recommend using a custom parser to extract the valid JSON portion, and an example implementation can be found here: 

import json
from typing import Any, Dict

def extract_valid_json(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and returns only the valid JSON part from a response object.
    
    This function assumes that the response has a structure where the valid JSON
    is included in the 'content' field of the first choice's message, after the 
    closing "</think>" marker. Any markdown code fences (e.g. ```json) are stripped.

    Parameters:
        response (dict): The full API response object.

    Returns:
        dict: The parsed JSON object extracted from the content.
    
    Raises:
        ValueError: If no valid JSON can be parsed from the content.
    """
    # Navigate to the 'content' field; adjust if your structure differs.
    content = (
        response
        .get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    
    # Find the index of the closing </think> tag.
    marker = "</think>"
    idx = content.rfind(marker)
    
    if idx == -1:
        # If marker not found, try parsing the entire content.
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError("No </think> marker found and content is not valid JSON") from e
    
    # Extract the substring after the marker.
    json_str = content[idx + len(marker):].strip()
    
    # Remove markdown code fence markers if present.
    if json_str.startswith("```json"):
        json_str = json_str[len("```json"):].strip()
    if json_str.startswith("```"):
        json_str = json_str[3:].strip()
    if json_str.endswith("```"):
        json_str = json_str[:-3].strip()
    
    try:
        parsed_json = json.loads(json_str)
        return parsed_json
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse valid JSON from response content") from e

## Sample response metadata:
{
"id": "f9a5c42b-a53f-4c63-8e68-80d927221e7a",
"model": "sonar-reasoning-pro",
"created": 1756486858,
"usage": {
  "prompt_tokens": 17,
  "completion_tokens": 1152,
  "total_tokens": 1169,
  "search_context_size": "low",
  "cost": {
    "input_tokens_cost": 0.0,
    "output_tokens_cost": 0.009,
    "request_cost": 0.006,
    "total_cost": 0.015
  }
},
"citations": [
  "https://pubs.aip.org/physicstoday/article/77/12/22/3321123/UK-coalition-gears-up-to-demonstrate-commercial",
  "https://energy.mit.edu/news/mit-study-shows-that-fusion-energy-could-play-a-major-role-in-the-global-response-to-climate-change/",
  "https://www.world-nuclear-news.org/Articles/US-could-operate-a-fusion-plant-by-2040-Academy-sa",
  "https://www.youtube.com/watch?v=qUkn8FarAcw",
  "https://world-nuclear.org/information-library/current-and-future-generation/nuclear-fusion-power"
],
"search_results": [
  {
    "title": "UK coalition gears up to demonstrate commercial viability of ...",
    "url": "https://pubs.aip.org/physicstoday/article/77/12/22/3321123/UK-coalition-gears-up-to-demonstrate-commercial",
    "date": "2024-12-01",
    "last_updated": "2025-05-24",
    "snippet": "The UK plans to build a prototype fusion plant by the early 2040s that can put electricity on the grid and demonstrates that fusion energy is commercially ...See more"
  },
  {
    "title": "MIT study shows that fusion energy could play a major role ...",
    "url": "https://energy.mit.edu/news/mit-study-shows-that-fusion-energy-could-play-a-major-role-in-the-global-response-to-climate-change/",
    "date": "2024-10-16",
    "last_updated": "2024-10-18",
    "snippet": "Experts in energy systems modeling and fusion technology explore the future role of fusion at various costs and carbon constraints."
  },
  {
    "title": "US could operate a fusion plant by 2040, Academy says",
    "url": "https://www.world-nuclear-news.org/Articles/US-could-operate-a-fusion-plant-by-2040-Academy-sa",
    "date": "2021-03-12",
    "last_updated": "2024-12-22",
    "snippet": "It identifies key goals and innovations needed to support the development of a US fusion pilot plant, many of which it says should be developed ...See more"
  },
  {
    "title": "MIT Cracked Nuclear Fusion.. And it Might Have Just ...",
    "url": "https://www.youtube.com/watch?v=qUkn8FarAcw",
    "date": "2025-05-31",
    "last_updated": "2025-08-23",
    "snippet": "This single breakthrough from MIT may have just triggered the beginning of the end for the global oil industry."
  },
  {
    "title": "Nuclear Fusion Power",
    "url": "https://world-nuclear.org/information-library/current-and-future-generation/nuclear-fusion-power",
    "date": "2025-06-05",
    "last_updated": "2025-08-29",
    "snippet": "STEP is scheduled for completion in 2040. In February 2022 researchers at JET achieved 59 megajoules of heat energy from fusion over a five- ...See more"
  }
],
"object": "chat.completion",
"choices": [
  {
    "index": 0,
    "finish_reason": "stop",
    "message": {
      "role": "assistant",
      "content": "<think>\nThe user is asking me to analyze the feasibility of fusion energy becoming a mainstream power source by 2040. Let me look at the search results to see what information is available about fusion energy timelines and viability.\n\nFrom the search results:\n\n1. UK STEP program plans to build a prototype fusion plant by early 2040s that can put electricity on the grid and demonstrate commercial viability. Goal is to produce about 100 MW of net electricity.\n\n2. MIT study shows fusion technologies may be a decade away from commercial deployment, with focus on determining what cost levels fusion plants must reach by 2050 to achieve strong market penetration.\n\n3. US could operate a fusion pilot plant by 2040 according to the National Academy. The report suggests the US is positioned to begin planning its first fusion pilot plant now to meet the challenge of operating between 2035 and 2040.\n\n4. YouTube video discussing MIT breakthrough and market projections of $80 billion by 2035 and $350 billion by 2050.\n\n5. World Nuclear Association mentions STEP scheduled for completion in 2040, and various tokamak projects including ITER operating in the 2020s and CFETR due for completion in 2030.\n\nSo I need to analyze the feasibility based on:\n- Technical challenges and progress\n- Timeline considerations  \n- Economic factors\n- Current projects and milestones\n\nThe query is asking for analysis, so I should provide a comprehensive assessment covering different aspects. This seems like it would benefit from multiple sections since it's a complex topic.\n\nLet me structure this as:\n- Current state and recent progress\n- Technical challenges \n- Timeline analysis\n- Economic considerations\n- Conclusion on feasibility\n\nI need to be careful about the restrictions - no hedging language, no \"according to search results\" phrases, cite sources appropriately, use past tense for events that happened before the current date (August 29, 2025).\n</think>\n\nThe prospect of fusion energy becoming a mainstream power source by 2040 represents one of the most ambitious technological challenges of our time, with significant progress being made but substantial hurdles remaining.\n\n## Current State and Recent Breakthroughs\n\nMultiple major projects are converging on the 2040 timeline with varying degrees of ambition. The UK's Spherical Tokamak for Energy Production (STEP) program aims to build a prototype fusion plant by the early 2040s that can deliver electricity to the grid and demonstrate commercial viability, targeting approximately 100 MW of net electricity output[1]. The United States has positioned itself to operate a fusion pilot plant between 2035 and 2040, with the National Academy concluding that requisite resources and planning can support this timeline[3].\n\nSeveral critical technological milestones have been achieved in recent years. The Joint European Torus (JET) achieved 59 megajoules of heat energy from fusion, while multiple tokamak facilities continue advancing the science[5]. The international ITER project, currently under construction in France, will become the largest tokamak when it operates in the 2020s, providing crucial data for commercial development[5].\n\n## Technical and Engineering Challenges\n\nThe technical demands for achieving mainstream fusion power by 2040 are **formidable**. Current fusion technologies face three primary engineering challenges: achieving sustained net energy output, maintaining adequate tritium supply for fuel, and demonstrating long-term operational maintenance capabilities[1]. Even successful projects like STEP acknowledge these goals as \"massively ambitious\" but \"just about doable\"[1].\n\nThe transition from experimental reactors to commercial power plants requires solving complex materials science problems, particularly regarding radiation-resistant components and magnetic confinement systems. The Chinese Fusion Engineering Test Reactor (CFETR), designed to be larger than ITER and scheduled for completion in 2030, represents a critical stepping stone toward commercial viability[5].\n\n## Economic Feasibility and Market Dynamics\n\nEconomic projections suggest the fusion market could reach $80 billion by 2035 and potentially exceed $350 billion by 2050[4]. However, research indicates that fusion technologies may still be a decade away from commercial deployment, with detailed costs of future commercial fusion power plants remaining uncertain[2].\n\nThe economic viability of fusion power will depend heavily on achieving competitive cost levels compared to other energy sources, including conventional fossil fuels, nuclear fission, renewable energy, and storage technologies[2]. Regulatory frameworks will play a crucial role as cost drivers, potentially creating significant barriers or enablers depending on policy approaches[2].\n\n## Timeline Reality Check\n\nWhile pilot plants and demonstration facilities may operate by 2040, achieving **mainstream** adoption requires distinguishing between proving technical feasibility and scaling to widespread commercial deployment. The evidence suggests 2040 will likely mark the beginning of commercial demonstration rather than mainstream adoption.\n\nResearch emphasizes that if cost and performance targets can be achieved, fusion energy can play a major role in meeting future electricity needs and achieving global net-zero carbon goals[2]. However, this transition will more likely occur in the latter half of the century rather than by 2040.\n\n## Assessment of 2040 Feasibility\n\nFusion energy becoming a mainstream power source by 2040 faces significant feasibility constraints. While multiple pilot plants and demonstration facilities will likely operate by this date, true mainstream adoption requires overcoming substantial technical, economic, and scaling challenges that extend beyond the 2040 timeline.\n\nThe convergence of major international projects, substantial investment flows, and recent technical breakthroughs creates a foundation for commercial fusion power. However, the transition from demonstration to mainstream deployment typically requires additional decades for technology maturation, cost reduction, and infrastructure development. The 2040s will more realistically represent the **beginning** of the commercial fusion era rather than its mainstream adoption."
    },
    "delta": {
      "role": "assistant",
      "content": ""
    }
  }
]
}