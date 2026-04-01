# gemini-web-automator-skill

使用本地 Playwright 脚本在 Gemini Web 上执行生图，并让用户在浏览器中完成确认与下载。

## Installation

This skill is intended to run in the local Codex/Gemini skill workspace.

If you are working in this repository, use the skill directly from:

```bash
.gemini/skills/gemini-web-automator-skill
```

## Documentation

# Gemini Web Automator

## Codex Compatibility
- 适合在 Codex 中作为“人工在环”的浏览器自动化步骤使用。
- 运行脚本后，要停下来让用户查看浏览器中的结果，不要假设可以自动完成下载确认。
- 默认优先使用项目约定的 `.venv` 运行脚本。

## Command

```bash
./.venv/bin/python .gemini/skills/gemini-web-automator-skill/scripts/gemini_web_playwright.py --prompt_file "path/to/prompt.md"
```

## 默认下载位置

脚本会捕获用户在 Gemini Web 中手动点击下载的图片，并默认保存到：

```text
~/Downloads/<downloaded-filename>
```
