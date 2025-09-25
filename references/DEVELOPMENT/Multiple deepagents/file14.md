# src/lib/environment/deployments.ts

@@ -1,7 +1,16 @@
export function getDeployment() {
  return {
    name: "Deep Agent",
    deploymentUrl: process.env.NEXT_PUBLIC_DEPLOYMENT_URL || "http://127.0.0.1:2024",
    agentId: process.env.NEXT_PUBLIC_AGENT_ID || "deepagent",
    name: "Deep Agents Platform",
    deploymentUrl:
      process.env.NEXT_PUBLIC_DEPLOYMENT_URL || "http://127.0.0.1:2024",
  };
}

export function getDeploymentForAgent(agentId: string) {
  return {
    name: "Deep Agents Platform",
    deploymentUrl:
      process.env.NEXT_PUBLIC_DEPLOYMENT_URL || "http://127.0.0.1:2024",
    agentId,
  };
}