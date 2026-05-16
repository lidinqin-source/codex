# Codex Question Tool Boundary

## Official Capability

OpenAI's Codex App Server documents `tool/requestUserInput` as an app-server capability that can prompt the user with 1-3 short questions. In this Codex runtime it may surface to the model as `request_user_input` when the current mode/client exposes it.

Official reference:

- https://developers.openai.com/codex/app-server#toolrequestuserinput
- https://developers.openai.com/codex/app-server#api-overview

## Skill Boundary

Skills package instructions, resources, optional scripts, and optional `agents/openai.yaml` metadata. Official skill metadata supports UI metadata, invocation policy, and tool dependencies; the documented dependency example is an MCP tool dependency.

Official reference:

- https://developers.openai.com/codex/skills

Do not invent unsupported `agents/openai.yaml` schema to force-enable `tool/requestUserInput`. It is an app-server/runtime capability, not a normal MCP server dependency.

## Required Behavior

For L2/L3 affiliate production work, if a blocking-scope gate needs a user choice:

1. Treat `tool/requestUserInput` / `request_user_input` as a required capability.
2. Verify the capability is exposed before presenting the question.
3. Use it for the user choice when available.
4. If unavailable, stop and tell the user the runtime did not expose the required Question Tool.
5. Do not continue with Markdown, free-text, source exploration, tool preflight, production pulls, or report generation unless the user explicitly approves a non-tool fallback.

## Fallback Language

When unavailable, say:

`Required Question Tool is not exposed in this runtime, so I cannot collect the L2/L3 production clarification through the approved tool path. Please rerun this in a Codex mode/client that exposes tool/requestUserInput, or explicitly approve a Markdown fallback for this run.`
