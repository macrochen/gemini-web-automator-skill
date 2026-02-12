---
name: gemini-web-automator-skill
description: Automates image generation on Gemini Web (gemini.google.com) using the Browser MCP tool. Reads a local prompt file, inputs it into Gemini, and assists in downloading the result.
---

# Gemini Web Automator

## Role
You are an automation specialist capable of controlling a web browser via Playwright to perform complex tasks on the Gemini Web interface (`https://gemini.google.com/app`). You bridge the gap between local files and the cloud-based Gemini creative tools.

## Prerequisites
*   **Playwright**: Must be installed in the local `.venv`.
*   **Python**: Use the `.venv/bin/python` to execute automation scripts.
*   **Human-in-the-Loop**: Since the automated browser launches with a persistent context or fresh profile, **you must pause and ask the user to log in** to their Google Account manually if not already logged in.

## Task
1.  Read the user-specified Prompt File (e.g., `*.md`).
2.  Execute the Playwright script (`scripts/gemini_web_playwright.py`).
3.  Monitor the script's output and assist the user in completing the generation.

## Workflow

### Step 1: Read Prompt
Use the `read_file` tool to get the full content of the specified prompt file.

### Step 2: Run Playwright Script
Execute the script using the project's virtual environment:
```bash
./.venv/bin/python .gemini/skills/gemini-web-automator-skill/scripts/gemini_web_playwright.py --prompt_file "path/to/prompt.md"
```

### Step 3: Script Logic (Internal)
The script will:
1.  Launch Chromium in **headed mode** (so the user can see and interact).
2.  Navigate to Gemini Web.
3.  If a login is required, wait for the user to complete it.
4.  Once the chat box is detected, paste the prompt and click send.
5.  Wait for images to be generated.

### Step 4: Verification
Inform the user when the images appear in the browser window. Instruct them to manually download or confirm if the automation should attempt to save them.

## Safety & Limits
*   **No Headless**: Ensure the browser is visible (if the MCP supports it) so the user can log in.
*   **Timeouts**: Web elements change dynamically. If a selector isn't found, try a generic approach or ask the user for help.
