---
trigger: always_on
---

C:\Users\netfl\OneDrive\Desktop\myagents\backend\langgraph.json is the connection between the backend and the frontend. it connects the main chat agent in the backend with the frontend UI. if the path to the main agent changes, then this needs to be changed to correctly point to the main agent, so when the main agent file is modified or its location is changed, ALWAYS make sure that the langgraph.json is appropriately modified to point to the main agent file so that the connection between the backend and the frontend is maintained. 