import asyncio
import sys
import argparse
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def run(prompt_file):
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_content = f.read()

    async with async_playwright() as p:
        user_data_dir = Path.home() / ".gemini_automation_profile"
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        downloads_path = Path.home() / "Downloads"
        
        # 定义任务完成事件
        task_completed = asyncio.Event()

        # 核心拦截逻辑：处理 Blob 或 临时下载文件
        async def handle_download(download):
            save_path = downloads_path / download.suggested_filename
            await download.save_as(save_path)
            print(f"\n✅ 【下载成功】已捕获并保存至: {save_path}")
            print(f"🚀 任务已完成，正在为您自动关闭浏览器...")
            await asyncio.sleep(2) # 留出一点点感官上的反应时间
            task_completed.set()

        page.on("download", handle_download)

        print(f"🚀 正在打开 Gemini Web...")
        await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")

        # 1. 自动输入并提交
        while True:
            input_box = await page.query_selector("div[contenteditable='true'], textarea")
            if input_box:
                print("✨ 填入提示词...")
                await input_box.fill(prompt_content)
                await asyncio.sleep(1)
                
                # 点击发送按钮
                send_btn = await page.query_selector("button[aria-label*='Send'], button[aria-label*='发送'], .send-button")
                if send_btn:
                    await send_btn.click()
                else:
                    await page.keyboard.press("Enter")
                break
            await asyncio.sleep(2)

        print("⌛ 指令已发送。")
        print("💡 请在浏览器中预览图片。满意后【直接点击下载】。")
        print("💡 脚本捕获下载后将自动返回 CLI。")

        try:
            # 等待下载完成事件，或设置一个较长的超时（如 15 分钟）
            await asyncio.wait_for(task_completed.wait(), timeout=900)
        except asyncio.TimeoutError:
            print("\n⏰ 超时未检测到下载，脚本自动关闭。")
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_file", required=True)
    args = parser.parse_args()
    try:
        asyncio.run(run(args.prompt_file))
    except KeyboardInterrupt:
        sys.exit(0)
