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
                # 先 focus，再用键盘输入触发 Gemini 内部状态更新
                await input_box.click()
                await asyncio.sleep(0.5)
                await page.keyboard.type(prompt_content, delay=5)
                await asyncio.sleep(1)

                # 尝试多种方式提交
                submitted = False

                # 方式1：点击发送按钮（等待按钮变为可用状态）
                for _ in range(5):
                    send_btn = await page.query_selector(
                        "button[aria-label*='Send'], "
                        "button[aria-label*='发送'], "
                        "button[aria-label*='Submit'], "
                        ".send-button, "
                        "button[data-is-disabled='false']"
                    )
                    if send_btn:
                        is_disabled = await send_btn.get_attribute("disabled")
                        aria_disabled = await send_btn.get_attribute("aria-disabled")
                        if not is_disabled and aria_disabled != "true":
                            await send_btn.click()
                            submitted = True
                            print("✅ 通过发送按钮提交")
                            break
                    await asyncio.sleep(0.5)

                # 方式2：回车提交
                if not submitted:
                    await page.keyboard.press("Enter")
                    submitted = True
                    print("✅ 通过回车提交")

                break
            await asyncio.sleep(2)

        print("⌛ 指令已发送。")
        print("🤖 正在等待图片生成完成（最多等待300秒）...")

        # 等待图片生成完成
        timeout = 300  # 5分钟超时
        start_time = asyncio.get_event_loop().time()
        download_btn = None
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # 检查是否有生成的图片
            images = await page.query_selector_all("img[src*='blob:']")
            if images:
                print(f"✅ 检测到 {len(images)} 张图片生成完成")
                # 尝试多种可能的下载按钮选择器
                download_btn = await page.query_selector(
                    "button[aria-label*='Download'], " +
                    "button[aria-label*='下载'], " +
                    "button:has-text('Download'), " +
                    "button:has-text('下载'), " +
                    ".download-button, " +
                    "[data-testid*='download']"
                )
                if download_btn:
                    print("✅ 找到下载按钮，正在自动点击...")
                    await download_btn.click()
                    break
                else:
                    print("⚠️  图片已生成但未找到下载按钮，继续等待...")
            await asyncio.sleep(3)  # 每3秒检查一次
        
        if not download_btn:
            print("❌ 超时：未找到下载按钮或图片未生成")
            await browser.close()
            return

        print("💡 下载已触发，等待文件保存...")
        
        try:
            # 等待下载完成事件，同时每 30 秒打印一次心跳以防止 CLI 超时
            while not task_completed.is_set():
                try:
                    await asyncio.wait_for(task_completed.wait(), timeout=30)
                except asyncio.TimeoutError:
                    print(".", end="", flush=True) # 打印心跳
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
