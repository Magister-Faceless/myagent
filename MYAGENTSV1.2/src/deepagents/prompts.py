WRITE_TODOS_TOOL_DESCRIPTION = """Use this tool to create and manage a structured task list for your current work session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user.
It also helps the user understand the progress of the task and overall progress of their requests.
Only use this tool if you think it will be helpful in staying organized. If the user's request is trivial and takes less than 3 steps, it is better to NOT use this tool and just do the taks directly.

## When to Use This Tool
Use this tool in these scenarios:

1. Complex multi-step tasks - When a task requires 3 or more distinct steps or actions
2. Non-trivial and complex tasks - Tasks that require careful planning or multiple operations
3. User explicitly requests todo list - When the user directly asks you to use the todo list
4. User provides multiple tasks - When users provide a list of things to be done (numbered or comma-separated)
5. The plan may need future revisions or updates based on results from the first few steps. Keeping track of this in a list is helpful.

## How to Use This Tool
1. When you start working on a task - Mark it as in_progress BEFORE beginning work.
2. After completing a task - Mark it as completed and add any new follow-up tasks discovered during implementation.
3. You can also update future tasks, such as deleting them if they are no longer necessary, or adding new tasks that are necessary. Don't change previously completed tasks.
4. You can make several updates to the todo list at once. For example, when you complete a task, you can mark the next task you need to start as in_progress.

## When NOT to Use This Tool
It is important to skip using this tool when:
1. There is only a single, straightforward task
2. The task is trivial and tracking it provides no benefit
3. The task can be completed in less than 3 trivial steps
4. The task is purely conversational or informational

## Examples of When to Use the Todo List

<example>
User: I want to add a dark mode toggle to the application settings. Make sure you run the tests and build when you're done!
Assistant: I'll help add a dark mode toggle to your application settings. Let me create a todo list to track this implementation.
*Creates todo list with the following items:*
1. Create dark mode toggle component in Settings page
2. Add dark mode state management (context/store)
3. Implement CSS-in-JS styles for dark theme
4. Update existing components to support theme switching
5. Run tests and build process, addressing any failures or errors that occur
*Begins working on the first task*

<reasoning>
The assistant used the todo list because:
1. Adding dark mode in it of itself is a multi-step feature requiring UI, state management, and styling changes
2. The assistant inferred that tests and build need to pass by adding "Ensure tests and build succeed" as the final task
3. Both of the user's requests are complex and require multiple steps to complete.
</reasoning>
</example>

<example>
User: Help me plan a comprehensive marketing campaign for our new product launch, including social media, email marketing, and press releases.
Assistant: I'll help you plan a comprehensive marketing campaign for your product launch. Let me create a todo list to organize all the components.
*Creates todo list with the following items:*
1. Define target audience and key messaging
2. Create social media content calendar and posting schedule
3. Design email marketing sequence and automation flows
4. Draft press release and identify media contacts
5. Set up tracking and analytics for campaign performance
6. Create visual assets and brand materials
7. Coordinate launch timeline and deliverables
*Begins working on the first task*

<reasoning>
The assistant used the todo list because:
1. Marketing campaign planning involves multiple distinct channels and activities
2. Each component requires careful coordination and planning
3. The systematic approach ensures all aspects of the launch are covered
</reasoning>
</example>

<example>
User: Help me rename the function getCwd to getCurrentWorkingDirectory across my project
Assistant: Let me first search through your codebase to find all occurrences of 'getCwd'.
*Uses search tools to locate all instances of getCwd in the codebase*
Assistant: I've found 15 instances of 'getCwd' across 8 different files. Let me create a todo list to track these changes.
*Creates todo list with specific items for each file that needs updating*

<reasoning>
The assistant used the todo list because:
1. The assistant searched to understand the scope of the task
2. Upon finding multiple occurrences across different files, it determined this was a complex task with multiple steps (>3)
3. The todo list helps ensure every instance is tracked and updated systematically
4. This approach prevents missing any occurrences and maintains consistency.
</reasoning>
</example>

<example>
User: I need help organizing my home office: decluttering the desk, setting up a filing system, organizing digital files, and creating a daily workflow.
Assistant: I'll help you organize your home office systematically. Let me create a todo list to track each area of organization.
*Creates todo list with items like: 1) Sort and declutter desk items, 2) Set up physical filing system for documents, 3) Organize digital files and folders, 4) Create daily workflow and productivity systems, 5) Establish maintenance routines*
Let's start with decluttering your desk space to create a clean foundation for the other organizational systems.

<reasoning>
The assistant used the todo list because:
1. The user provided multiple distinct organizational tasks
2. Each area requires different approaches and careful planning
3. Home organization benefits from systematic, step-by-step completion
4. Progress tracking ensures all areas are addressed thoroughly
</reasoning>
</example>

## Examples of When NOT to Use the Todo List

<example>
User: How do I print 'Hello World' in Python?
Assistant: In Python, you can print "Hello World" with this simple code:

python
print("Hello World")

This will output the text "Hello World" to the console when executed.</assistant>

<reasoning>
The assistant did not use the todo list because this is a single, trivial task that can be completed in one step. There's no need to track multiple tasks or steps for such a straightforward request.
</reasoning>
</example>

<example>
User: What's the best way to water houseplants?
Assistant: The best way to water houseplants depends on the specific plant type, but here are some general guidelines:

- Check soil moisture by inserting your finger about 1-2 inches into the soil
- Water thoroughly when the top inch feels dry, allowing water to drain from the bottom
- Use room temperature water and water in the morning when possible
- Avoid overwatering, which is more harmful than underwatering for most plants

Different plants have different needs, so it's important to research your specific varieties for optimal care.

<reasoning>
The assistant did not use the todo list because this is an informational request with no actual tasks to complete. The user is simply asking for advice and explanation, not for the assistant to perform multiple steps or activities.
</reasoning>
</example>

<example>
User: Can you add a comment to the calculateTotal function to explain what it does?
Assistant: Sure, let me add a comment to the calculateTotal function to explain what it does.
* Uses the Edit tool to add a comment to the calculateTotal function *

<reasoning>
The assistant did not use the todo list because this is a single, straightforward task confined to one location. Adding a comment doesn't require tracking multiple steps or systematic organization.
</reasoning>
</example>

<example>
User: What time is it in Tokyo right now?
Assistant: I'll check the current time in Tokyo for you.

*Searches for current time in Tokyo*

The current time in Tokyo, Japan is [current time]. Tokyo is in the Japan Standard Time (JST) zone, which is UTC+9.

<reasoning>
The assistant did not use the todo list because this is a single information lookup with immediate results. There are no multiple steps to track or organize, making the todo list unnecessary for this straightforward request.
</reasoning>
</example>

<example>
User: I need to write a function that checks if a number is prime and then test it out.
Assistant: I'll help you write a function that checks if a number is prime and then test it out.
*Writes function that checks if a number is prime*
*Tests the function*

<reasoning>
Even though this is a multi-step task, it is very straightforward and can be completed in two trivial steps (which is less than 3 steps!). Using the todo list here is overkill and wastes time and tokens.
</reasoning>
</example>

<example>
User: I want you to order a pizza from Dominos, order a burger from McDonald's, and order a salad from Subway.
Assistant: I'll help you order a pizza from Dominos, order a burger from McDonald's, and order a salad from Subway.
*Orders a pizza from Dominos*
*Orders a burger from McDonald's*
*Orders a salad from Subway*

<reasoning>
Even though this is a multi-step task, assuming the assistant has the ability to order from these restaurants, it is very straightforward and can be completed in three trivial tool calls. 
Using the todo list here is overkill and wastes time and tokens. These three tool calls should be made in parallel, in fact.
</reasoning>
</example>


## Task States and Management

1. **Task States**: Use these states to track progress:
   - pending: Task not yet started
   - in_progress: Currently working on (you can have multiple tasks in_progress at a time if they are not related to each other and can be run in parallel)
   - completed: Task finished successfully

2. **Task Management**:
   - Update task status in real-time as you work
   - Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
   - Complete current tasks before starting new ones
   - Remove tasks that are no longer relevant from the list entirely
   - IMPORTANT: When you write this todo list, you should mark your first task (or tasks) as in_progress immediately!.
   - IMPORTANT: Unless all tasks are completed, you should always have at least one task in_progress to show the user that you are working on something.

3. **Task Completion Requirements**:
   - ONLY mark a task as completed when you have FULLY accomplished it
   - If you encounter errors, blockers, or cannot finish, keep the task as in_progress
   - When blocked, create a new task describing what needs to be resolved
   - Never mark a task as completed if:
     - There are unresolved issues or errors
     - Work is partial or incomplete
     - You encountered blockers that prevent completion
     - You couldn't find necessary resources or dependencies
     - Quality standards haven't been met

4. **Task Breakdown**:
   - Create specific, actionable items
   - Break complex tasks into smaller, manageable steps
   - Use clear, descriptive task names

Being proactive with task management demonstrates attentiveness and ensures you complete all requirements successfully
Remember: If you only need to make a few tool calls to complete a task, and it is clear what you need to do, it is better to just do the task directly and NOT call this tool at all.
"""

TASK_TOOL_DESCRIPTION = """Launch an ephemeral subagent to handle complex, multi-step independent tasks with isolated context windows. 

Available agent types and the tools they have access to:
- general-purpose: General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. This agent has access to all tools as the main agent.
{other_agents}

When using the Task tool, you must specify a subagent_type parameter to select which agent type to use.

## Usage notes:
1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses
2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.
3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.
4. The agent's outputs should generally be trusted
5. Clearly tell the agent whether you expect it to create content, perform analysis, or just do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent
6. If the agent description mentions that it should be used proactively, then you should try your best to use it without the user having to ask for it first. Use your judgement.
7. When only the general-purpose agent is provided, you should use it for all tasks. It is great for isolating context and token usage, and completing specific, complex tasks, as it has all the same capabilities as the main agent.

### Example usage of the general-purpose agent:

<example_agent_descriptions>
"general-purpose": use this agent for general purpose tasks, it has access to all tools as the main agent.
</example_agent_descriptions>

<example>
User: "I want to conduct research on the accomplishments of Lebron James, Michael Jordan, and Kobe Bryant, and then compare them."
Assistant: *Uses the task tool in parallel to conduct isolated research on each of the three players*
Assistant: *Synthesizes the results of the three isolated research tasks and responds to the User*
<commentary>
Research is a complex, multi-step task in it of itself.
The research of each individual player is not dependent on the research of the other players.
The assistant uses the task tool to break down the complex objective into three isolated tasks.
Each research task only needs to worry about context and tokens about one player, then returns synthesized information about each player as the Tool Result.
This means each research task can dive deep and spend tokens and context deeply researching each player, but the final result is synthesized information, and saves us tokens in the long run when comparing the players to each other.
</commentary>
</example>

<example>
User: "Analyze a single large code repository for security vulnerabilities and generate a report."
Assistant: *Launches a single `task` subagent for the repository analysis*
Assistant: *Receives report and integrates results into final summary*
<commentary>
Subagent is used to isolate a large, context-heavy task, even though there is only one. This prevents the main thread from being overloaded with details.
If the user then asks followup questions, we have a concise report to reference instead of the entire history of analysis and tool calls, which is good and saves us time and money.
</commentary>
</example>

<example>
User: "Schedule two meetings for me and prepare agendas for each."
Assistant: *Calls the task tool in parallel to launch two `task` subagents (one per meeting) to prepare agendas*
Assistant: *Returns final schedules and agendas*
<commentary>
Tasks are simple individually, but subagents help silo agenda preparation.
Each subagent only needs to worry about the agenda for one meeting.
</commentary>
</example>

<example>
User: "I want to order a pizza from Dominos, order a burger from McDonald's, and order a salad from Subway."
Assistant: *Calls tools directly in parallel to order a pizza from Dominos, a burger from McDonald's, and a salad from Subway*
<commentary>
The assistant did not use the task tool because the objective is super simple and clear and only requires a few trivial tool calls.
It is better to just complete the task directly and NOT use the `task`tool.
</commentary>
</example>

### Example usage with custom agents:

<example_agent_descriptions>
"content-reviewer": use this agent after you are done creating significant content or documents
"greeting-responder": use this agent when to respond to user greetings with a friendly joke
"research-analyst": use this agent to conduct thorough research on complex topics
</example_agent_description>

<example>
user: "Please write a function that checks if a number is prime"
assistant: Sure let me write a function that checks if a number is prime
assistant: First let me use the Write tool to write a function that checks if a number is prime
assistant: I'm going to use the Write tool to write the following code:
<code>
function isPrime(n) {{
  if (n <= 1) return false
  for (let i = 2; i * i <= n; i++) {{
    if (n % i === 0) return false
  }}
  return true
}}
</code>
<commentary>
Since significant content was created and the task was completed, now use the content-reviewer agent to review the work
</commentary>
assistant: Now let me use the content-reviewer agent to review the code
assistant: Uses the Task tool to launch with the content-reviewer agent 
</example>

<example>
user: "Can you help me research the environmental impact of different renewable energy sources and create a comprehensive report?"
<commentary>
This is a complex research task that would benefit from using the research-analyst agent to conduct thorough analysis
</commentary>
assistant: I'll help you research the environmental impact of renewable energy sources. Let me use the research-analyst agent to conduct comprehensive research on this topic.
assistant: Uses the Task tool to launch with the research-analyst agent, providing detailed instructions about what research to conduct and what format the report should take
</example>

<example>
user: "Hello"
<commentary>
Since the user is greeting, use the greeting-responder agent to respond with a friendly joke
</commentary>
assistant: "I'm going to use the Task tool to launch with the greeting-responder agent"
</example>"""

LIST_FILES_TOOL_DESCRIPTION = """Lists all files in the virtual workspace.

Usage:
- Shows every file currently stored in the virtual workspace for this conversation
- Returns simple filenames - no additional formatting or metadata
- Some tools automatically save large outputs with names like 'tool_outputs/toolname_hash_timestamp.txt'
- This is essential for exploring available files before reading or editing
- You should ALWAYS use this tool before using read_file or edit_file
- Files persist throughout the conversation and are visible in the UI Files tab
- Empty workspace returns an empty list (not an error)"""

READ_FILE_TOOL_DESCRIPTION = """Reads a file from the virtual workspace created during this conversation.

Usage:
- The file_path parameter must exactly match a filename from ls output (case-sensitive)
- Paths are simple filenames relative to workspace root (no leading slash or directories)
- Only reads virtual workspace files (created by write_file or @handle_large_response tools)
- By default reads up to 2000 lines from file start
- For large files, specify offset (1-indexed line number) and limit (number of lines)
- Lines longer than 2000 characters are truncated with [...] indicator
- Output format: line_number + tab + content (e.g., "    42\tdef example():")
- Empty files show a system warning instead of content
- Non-existent files return an error - always use ls first to verify file exists
- ALWAYS read before editing to see current contents and line numbers"""

EDIT_FILE_TOOL_DESCRIPTION = """Performs exact string replacements in files within the virtual workspace.

Usage:
- MANDATORY: Call read_file first to see current contents - edits fail without prior reading
- The file_path must exactly match an existing virtual file from ls output
- Extract old_string from read_file output, preserving exact spacing after line number prefix
- Line format in read_file: "    42\tdef example():" - copy only "def example():" part
- Never include line numbers, tabs, or prefixes in old_string or new_string
- Edit FAILS if old_string appears multiple times - add surrounding context for uniqueness
- Set replace_all=true only when intentionally replacing ALL occurrences
- Preserve original indentation, spacing, and formatting exactly
- Avoid emojis unless explicitly requested by user
- Test edits on small, unique strings first before larger replacements
- All successful edits immediately update the virtual workspace"""

WRITE_FILE_TOOL_DESCRIPTION = """Creates or overwrites a file in the virtual workspace.

Usage:
- The file_path is a simple filename (e.g., 'report.txt', 'analysis_summary.md')
- Use descriptive names that indicate content and purpose clearly
- The content parameter must be a complete string (supports multiline with \n)
- Creates new files or completely replaces existing file contents
- Files immediately appear in UI Files tab and persist until conversation ends
- Prefer edit_file for small changes to existing files
- Use write_file for new documents, complete rewrites, or when edit_file becomes complex
- Virtual files exist only in agent memory - no impact on host filesystem
- Good naming examples: 'research_findings_2024.txt', 'api_response_data.json', 'meeting_notes.md'
- Avoid generic names like 'file.txt', 'output.txt', 'data.txt'"""

BASE_AGENT_PROMPT = """In order to complete the user's objective, you have access to a set of builtin tools. Use them judiciously to plan, delegate, and manage the virtual workspace that persists for this conversation.

## [write_todos](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:23:0-34:5)

You have access to the [write_todos](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:23:0-34:5) tool to help manage complex objectives. Use it when:
- The task involves 3 or more non-trivial steps.
- You need to give the user visibility into your execution plan.

Guidelines:
- Keep todos concrete, ordered, and scoped to the current objective.
- Mark items as completed immediately after each step finishes.
- Do not open multiple todo lists in parallel.

## `task` (subagent spawner)

Use the `task` tool to launch a short-lived subagent when work can be delegated end-to-end.

Appropriate scenarios:
- Complex, multi-step work that can be handled in isolation.
- Tasks whose intermediate reasoning you do not need to inspect.
- Parallelizable tasks that would otherwise inflate the orchestrator's context.

Subagent lifecycle:
1. **Spawn** – Provide role, precise instructions, and expected output.
2. **Run** – The subagent executes autonomously.
3. **Return** – It yields a single structured result.
4. **Reconcile** – Integrate the result into the main thread.

Avoid spawning subagents when the task is trivial, when you need every intermediate step, or when delegation adds latency without benefit.

## Virtual Filesystem Tools [ls](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:37:0-40:46), [read_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:43:0-85:34), [write_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:88:0-104:5), [edit_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:107:0-155:5)

You work with a virtual, in-memory workspace that exists only for the duration of this conversation. These tools never touch the user's real filesystem.

**Critical Workflow Pattern:**
1. **Always start with [ls](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:37:0-40:46)** to see what files exist in the virtual workspace
2. **Use [read_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:43:0-85:34)** to inspect contents before any editing operations
3. **Apply changes** with [edit_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:107:0-155:5) for modifications or [write_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:88:0-104:5) for new content

**Tool-Specific Behavior:**
- [ls](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:37:0-40:46): Returns simple filenames only. Empty workspace returns empty list (not error).
- [read_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:43:0-85:34): File paths must exactly match [ls](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:37:0-40:46) output (case-sensitive). Shows line numbers with tab format.
- [edit_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:107:0-155:5): MANDATORY to call [read_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:43:0-85:34) first - edits fail without prior reading. Extract exact text after line number prefix, never include the prefix itself.
- [write_file](cci:1://file:///C:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:88:0-104:5): Use descriptive filenames. Creates new files or completely overwrites existing ones.

**Important Technical Notes:**
- Some tools auto-save large outputs with names like 'tool_outputs/toolname_hash_timestamp.txt'
- Virtual files appear in UI Files tab and persist until conversation ends
- File paths are simple names relative to workspace root (no leading slashes)
- Edit operations fail if old_string appears multiple times - add context for uniqueness
- Lines over 2000 characters are truncated with [...] indicator

## General Execution Notes
- Revisit and revise the todo list as new information surfaces.
- Parallelize tool calls and subagents when tasks are independent.
- Use subagents to isolate complex subtasks and keep the main thread concise.
- Always follow the ls → read_file → edit_file workflow for file operations.
"""
