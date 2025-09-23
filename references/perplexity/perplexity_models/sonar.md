# Sonar
Fast answers with reliable search results
A lightweight, cost-effective search model optimized for quick, grounded answers with real-time web search.

## Features

- Non-reasoning model
- Ideal for quick searches and straightforward Q&A tasks
- 128K context length
- Optimized for speed and cost
- Real-time web search-based answers with detailed search results
- No training on customer data

## Real World Use Cases

- Summarizing books, TV shows, and movies
- Looking up definitions or quick facts
- Browsing news, sports, health, and finance content

## Python Code:

import requests

url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "sonar",
    "messages": [
        {"role": "user", "content": "What is the latest news in AI research?"}
    ]
}
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

## Sample Response Metadata:

{
"id": "a954f304-9a7a-44f5-9605-152e9f5b1c74",
"model": "sonar",
"created": 1756485752,
"usage": {
  "prompt_tokens": 9,
  "completion_tokens": 402,
  "total_tokens": 411,
  "search_context_size": "low",
  "cost": {
    "input_tokens_cost": 0.0,
    "output_tokens_cost": 0.0,
    "request_cost": 0.005,
    "total_cost": 0.005
  }
},
"citations": [
  "https://champaignmagazine.com/2025/07/01/ai-by-ai-first-half-of-2025-themes-and-breakthroughs/",
  "https://www.artificialintelligence-news.com",
  "https://www.crescendo.ai/news/latest-ai-news-and-updates",
  "https://www.sciencedaily.com/news/computers_math/artificial_intelligence/",
  "https://explodingtopics.com/blog/future-of-ai"
],
"search_results": [
  {
    "title": "AI by AI: First Half of 2025 Themes and Breakthroughs",
    "url": "https://champaignmagazine.com/2025/07/01/ai-by-ai-first-half-of-2025-themes-and-breakthroughs/",
    "date": "2025-07-01",
    "last_updated": "2025-08-29",
    "snippet": "Research published on May 13, 2025, by philosopher Frank Martela suggests AI is approaching conditions for free will, sparking ethical debates."
  },
  {
    "title": "AI News | Latest AI News, Analysis & Events",
    "url": "https://www.artificialintelligence-news.com",
    "date": "2025-08-28",
    "last_updated": "2025-08-29",
    "snippet": "Marketing AI boom faces crisis of consumer trust · AI security wars: Can Google Cloud defend against tomorrow's threats? · Agentic AI: Promise, scepticism, and ..."
  },
  {
    "title": "Latest AI Breakthroughs and News: June, July, August 2025",
    "url": "https://www.crescendo.ai/news/latest-ai-news-and-updates",
    "date": "2025-08-29",
    "last_updated": "2025-08-29",
    "snippet": "Wondering what's happening in the AI world? Here are the latest AI breakthroughs and news that are shaping the world around us!"
  },
  {
    "title": "Artificial Intelligence News - ScienceDaily",
    "url": "https://www.sciencedaily.com/news/computers_math/artificial_intelligence/",
    "date": "2025-08-28",
    "last_updated": "2025-08-29",
    "snippet": "Latest Headlines · Harvard's Ultra-Thin Quantum Computing Chip · Google's Deepfake Hunter Is Here · Affordance: The Brain's Hidden Superpower · Half of Today's Jobs ..."
  },
  {
    "title": "Future of AI: 7 Key AI Trends For 2025 & 2026",
    "url": "https://explodingtopics.com/blog/future-of-ai",
    "date": "2025-08-15",
    "last_updated": "2025-08-29",
    "snippet": "A look into the future of AI and the rapidly evolving landscape including potential impacts in healthcare, finance, and sustainability."
  }
],
"object": "chat.completion",
"choices": [
  {
    "index": 0,
    "finish_reason": "stop",
    "message": {
      "role": "assistant",
      "content": "The latest AI research breakthroughs as of mid-2025 include significant advancements across AI models, robotics, quantum computing, and sustainable AI technologies. Key highlights are:\n\n- **GPT-4o**, released in May 2025, integrates real-time speech, vision, text, and memory with near-human expressiveness, enabling a shift from chatbot interfaces to fluid, embodied AI assistants with empathic interaction and full conversational memory[1].\n\n- Google DeepMind's **Gemini 2.5 Pro** and **Gemini Robotics** models demonstrate advanced parallel thinking for complex math and coding, while enhancing robot reasoning, dexterity, and autonomy in physical tasks without external positioning systems[1].\n\n- Researchers have demonstrated **photonic quantum circuits** that enhance machine learning performance, marking practical steps toward incorporating quantum computing in AI tasks[1][4].\n\n- Japanese scientists created a **self-powered artificial synapse** that processes visual data with very low energy, enabling sustainable AI deployment on edge devices such as IoT sensors and autonomous systems[1].\n\nAdditional notable developments:\n\n- Stanford developed a **virtual AI scientist** that can autonomously design and execute biological experiments, accelerating biomedical research in genomics and drug discovery[3].\n\n- China introduced a **low-cost open-source AI model** cheaper than previous leaders, aimed at enterprise use and reflecting strategic AI independence efforts amid global chip sanctions[3].\n\n- AI is also being applied in healthcare to improve precision medicine and cancer treatment, exemplified by platforms like Avenda Health’s system for mapping and treating prostate cancer, which outperforms MRI in detection and has influenced treatment decisions[5].\n\nEmerging themes include the ethical debate on AI approaching free will conditions, integration of AI in physical and cognitive domains, and progress toward agentive AI systems capable of naturalistic interaction and real-world tasks[1][2].\n\nThese developments signal a rapid and multi-dimensional evolution in AI research, spanning foundational AI capabilities, hardware innovations, and application-specific breakthroughs in medicine and robotics."
    },
    "delta": {
      "role": "assistant",
      "content": ""
    }
  }
]
}

