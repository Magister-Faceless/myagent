# src/lib/client.ts

@@ -1,5 +1,8 @@
import { Client } from "@langchain/langgraph-sdk";
import { getDeployment } from "./environment/deployments";
import {
  getDeployment,
  getDeploymentForAgent,
} from "./environment/deployments";

export function createClient(accessToken: string) {
  const deployment = getDeployment();
@@ -11,3 +14,14 @@ export function createClient(accessToken: string) {
    },
  });
}

export function createClientForAgent(accessToken: string, agentId: string) {
  const deployment = getDeploymentForAgent(agentId);
  return new Client({
    apiUrl: deployment?.deploymentUrl || "",
    apiKey: accessToken,
    defaultHeaders: {
      "x-auth-scheme": "langsmith",
    },
  });
}