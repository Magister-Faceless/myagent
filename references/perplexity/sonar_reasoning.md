# Sonar Reasoning
Quick reasoning with real-time search

A reasoning-focused model that applies Chain-of-Thought (CoT) reasoning for quick problem-solving and structured analysis with real-time web search.

## Features

- Reasoning model
- Search
- Chain-of-Thought (CoT) reasoning
- Length: 128K context length
- Speed: Designed for quick reasoning-based tasks
- Citation
- Real-time web search with detailed search results

## Real World Use Cases
- Problem solving
- Multi-step problem solving
- Analysis
- Logical analysis and structured reasoning
- Planning
- Strategic planning and decision making

## Code examples:

import requests

url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "sonar-reasoning",
    "messages": [
        {"role": "user", "content": "Provide an in-depth analysis of the impact of AI on global job markets over the next decade."}
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
"id": "2c87a264-8481-40b1-974a-721e1aad7850",
"model": "sonar-reasoning",
"created": 1756486636,
"usage": {
  "prompt_tokens": 19,
  "completion_tokens": 1531,
  "total_tokens": 1550,
  "search_context_size": "low",
  "cost": {
    "input_tokens_cost": 0.0,
    "output_tokens_cost": 0.008,
    "request_cost": 0.005,
    "total_cost": 0.013
  }
},
"citations": [
  "https://www.nexford.edu/insights/how-will-ai-affect-jobs",
  "https://www.weforum.org/stories/2025/04/ai-jobs-international-workers-day/",
  "https://www.jpmorgan.com/insights/global-research/artificial-intelligence/ai-impact-job-growth",
  "https://onlinedegrees.sandiego.edu/ai-impact-on-job-market/",
  "https://www.pwc.com/gx/en/issues/artificial-intelligence/ai-jobs-barometer.html"
],
"search_results": [
  {
    "title": "How will Artificial Intelligence Affect Jobs 2025-2030",
    "url": "https://www.nexford.edu/insights/how-will-ai-affect-jobs",
    "date": "2025-06-29",
    "last_updated": "2025-08-29",
    "snippet": "Artificial intelligence (AI) could replace the equivalent of 300 million full-time jobs, a report by investment bank Goldman Sachs says. It ..."
  },
  {
    "title": "Is AI closing the door on entry-level job opportunities?",
    "url": "https://www.weforum.org/stories/2025/04/ai-jobs-international-workers-day/",
    "date": "2025-04-30",
    "last_updated": "2025-08-29",
    "snippet": "The Forum's Future of Jobs Report 2025 reveals that 40% of employers expect to reduce their workforce where AI can automate tasks."
  },
  {
    "title": "Is AI already impacting job growth? - Global Research - J.P. Morgan",
    "url": "https://www.jpmorgan.com/insights/global-research/artificial-intelligence/ai-impact-job-growth",
    "date": "2025-08-15",
    "last_updated": "2025-08-29",
    "snippet": "August 15, 2025. AI is poised to displace jobs, with some industries more at risk than others. Is the paradigm shift already underway?"
  },
  {
    "title": "The Impact of AI on the Job Market and Employment Opportunities",
    "url": "https://onlinedegrees.sandiego.edu/ai-impact-on-job-market/",
    "date": "2025-03-27",
    "last_updated": "2025-08-29",
    "snippet": "AI is transforming recruitment and workforce management by optimizing key processes. One of its most significant benefits is improving hiring efficiency."
  },
  {
    "title": "The Fearless Future: 2025 Global AI Jobs Barometer - PwC",
    "url": "https://www.pwc.com/gx/en/issues/artificial-intelligence/ai-jobs-barometer.html",
    "date": "2025-06-02",
    "last_updated": "2025-08-29",
    "snippet": "PwC's 2025 Global AI Jobs Barometer reveals that AI can make people more valuable, not less – even in the most highly automatable jobs."
  }
],
"object": "chat.completion",
"choices": [
  {
    "index": 0,
    "finish_reason": "stop",
    "message": {
      "role": "assistant",
      "content": "<think>\nThis is a complex query asking for an in-depth analysis of AI's impact on global job markets over the next decade. Based on the search results, I need to provide a comprehensive and detailed answer covering multiple aspects of this topic.\n\nFrom the search results, I can extract key information about:\n1. Job displacement predictions\n2. Industries most at risk\n3. New job creation\n4. Skills transformation\n5. Geographic and demographic impacts\n6. Current trends already visible\n\nLet me organize this into a structured analysis with multiple sections, as this is an academic-type research query that requires a detailed, scientific write-up format.\n\nKey points from the search results:\n- Goldman Sachs: AI could replace equivalent of 300 million full-time jobs\n- World Economic Forum: 85 million jobs replaced by 2025, but 11 million new jobs created\n- 40% of employers expect to reduce workforce where AI can automate\n- McKinsey: 14% of employees globally may need career changes by 2030\n- PwC: wages rising for AI-skilled workers, suggesting AI makes workers more valuable\n- Current unemployment among college graduates has increased to 5.8%\n\nI need to be careful about the current date (August 29, 2025) and use appropriate tenses. Some of the predictions mentioned for 2025 should be discussed in present or past tense since we're in 2025.\n</think>\n\nArtificial intelligence is fundamentally reshaping global employment patterns, creating both unprecedented disruption and opportunity across industries. The transformation represents one of the most significant shifts in the labor market since the industrial revolution, with effects already visible and projections indicating accelerating change through 2035.\n\n## **Scale of Transformation**\n\nThe magnitude of AI's impact on employment is substantial and multifaceted. Goldman Sachs projects that AI could replace the equivalent of 300 million full-time jobs globally, with two-thirds of jobs in the US and Europe exposed to some degree of AI automation[1]. However, this disruption comes with corresponding job creation - technology trends, including AI, are expected to create 11 million jobs while simultaneously displacing 9 million others[2].\n\nCurrent data reveals that the transformation has already begun. The unemployment rate among college graduates reached 5.8% in March 2025, the highest in more than four years, with the rate trending above the aggregate unemployment rate - a historically unusual pattern[3]. This suggests that AI's impact on knowledge workers, previously considered the most secure employment category, is already materializing.\n\nThe World Economic Forum estimates that 85 million jobs will be replaced by 2025, with 40% of employers expecting to reduce their workforce where AI can automate tasks[1][2]. Looking toward 2030, McKinsey Global Institute reports that at least 14% of employees globally will need to change their careers due to digitization, robotics, and AI advancements[1].\n\n## **Industry-Specific Impact Patterns**\n\n**High-Risk Sectors**\n\nManufacturing leads the automation wave, with MIT and Boston University research indicating that AI will replace as many as two million manufacturing workers by 2025[1]. The retail sector faces particularly acute disruption, with 65% of retail jobs potentially automated due to technological advancements, rising costs, and tight labor markets[1].\n\nCustomer service represents another vulnerable sector, where natural language processing algorithms now commonly power chatbots that handle initial customer interactions[4]. Banking and insurance are experiencing significant transformation as AI automates paperwork, accelerates issue resolution, and enhances fraud detection capabilities[4].\n\nTransportation stands at the forefront of AI-driven change, with autonomous driving technology promising to reshape the entire sector. Self-driving trucks offer faster deliveries and reduced labor costs, while companies like Tesla have brought autonomous vehicles into mainstream consideration[4].\n\n**Emerging Opportunities**\n\nDespite widespread automation concerns, certain sectors are experiencing AI-driven job growth. Technology and information processing roles are expanding rapidly, with AI creating specialized positions in prompt engineering, AI system management, and human-AI collaboration[5]. The skills premium for AI-capable workers is substantial - wages for workers with AI skills are significantly higher across all analyzed industries[5].\n\n## **Skills Revolution and Workforce Adaptation**\n\nThe AI transformation is triggering what experts term a \"skills earthquake.\" Employers expect 39% of key skills required in the job market will change by 2030, with technological skills leading in importance over the next five years[4]. This represents an accelerating pace of skill requirement evolution that demands continuous workforce adaptation.\n\n**White-Collar Vulnerability**\n\nContrary to earlier assumptions that blue-collar jobs faced the greatest automation risk, research from the University of Pennsylvania and OpenAI reveals that educated white-collar workers earning up to $80,000 annually are among the most likely to be affected by workforce automation[1]. This shift reflects AI's capability to handle complex cognitive tasks previously considered uniquely human.\n\n**Geographic and Demographic Considerations**\n\nThe impact varies significantly across demographics and regions. PwC estimates that by the mid-2030s, up to 30% of jobs could be automatable, with slightly more men affected long-term as autonomous vehicles replace manual tasks where male employment share is higher[1]. However, women face greater risk during initial automation waves due to higher representation in clerical and administrative functions[1].\n\nCompetition is intensifying globally, with US firms expanding operations in countries like India, where skilled professionals can be employed at significantly lower costs, creating additional pressure on domestic white-collar roles[2].\n\n## **Economic Implications and Productivity Gains**\n\nThe economic implications extend beyond job displacement to fundamental productivity transformation. AI could eventually increase the total annual value of goods and services produced globally by 7%[1]. Paradoxically, wages are rising twice as quickly in industries most exposed to AI compared to those least exposed, suggesting that AI is making workers more valuable rather than replaceable in many contexts[5].\n\nThis wage premium challenges conventional assumptions about AI's impact. Workers with AI skills command significantly higher wages across all analyzed industries, indicating that human-AI collaboration creates more value than either humans or AI alone[5].\n\n## **Current Market Dynamics**\n\nThe labor market is already experiencing AI-driven changes that extend beyond simple job replacement. Entry-level positions are declining, with salary expectations shifting as remaining positions increasingly require AI collaboration capabilities for potentially lower compensation[2]. Nearly half of US Gen Z job hunters believe AI has reduced their college education's market value[2].\n\nThe talent pipeline faces disruption with significant implications for social mobility and equal representation. As traditional entry-level roles disappear, career pathways that historically enabled economic advancement are being restructured[2].\n\n## **Future Trajectory Through 2035**\n\nThe next decade will likely see an acceleration of current trends rather than revolutionary new patterns. The transformation appears to be following a wave-like progression, with different industries and job categories affected sequentially rather than simultaneously. Initial waves target routine, repetitive tasks, while subsequent phases will likely address more complex cognitive functions.\n\nAI's impact is not simply substitutive but transformative, creating hybrid roles where human judgment, creativity, and emotional intelligence complement AI's analytical and processing capabilities. The most successful workers and organizations will be those that effectively integrate AI tools to enhance rather than replace human capabilities.\n\nThe evidence suggests that while AI will continue displacing certain job categories, it simultaneously creates new opportunities and increases the value of workers who adapt their skills accordingly. The key challenge lies not in preventing AI adoption but in managing the transition to ensure workforce adaptation keeps pace with technological change."
    },
    "delta": {
      "role": "assistant",
      "content": ""
    }
  }
]
}