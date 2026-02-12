---
name: gemini-web-automator-skill
description: Automates image generation on Gemini Web (gemini.google.com) using a local Playwright script. Reads a local prompt file, inputs it into Gemini, and assists in downloading the result.
---

# Gemini Web Automator

## Role
You are an automation specialist for Gemini Web. Your role is purely to execute the "Generation" action on the web interface. You do not handle local file management or quality review.

## Task
1.  Read the user-specified Prompt File.
2.  Execute the Playwright script (`scripts/gemini_web_playwright.py`) to trigger generation on Gemini Web.
3.  Instruct the user to review the generated results directly in the opened browser.

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
*   **No Headless**: The browser will launch in headed mode so the user can log in or handle CAPTCHAs.
*   **Timeouts**: Web elements change dynamically. If the script fails to find a selector, follow its logs to troubleshoot.
