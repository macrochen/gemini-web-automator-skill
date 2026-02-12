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
        stop_event = asyncio.Event()

        async def handle_download(download):
            save_path = downloads_path / download.suggested_filename
            await download.save_as(save_path)
            print(f"✅ 【下载成功】已保存至: {save_path}")
            await asyncio.sleep(2)
            stop_event.set()

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

        print("⌛ 等待生图并尝试全自动下载...")

        # 2. 全自动扫描并点击下载
        async def auto_download_task():
            processed_imgs = set()
            while not stop_event.is_set():
                # 寻找所有图片容器
                images = await page.query_selector_all("img[src*='googleusercontent.com']")
                for img in images:
                    src = await img.get_attribute("src")
                    if not src or src in processed_imgs or "googleusercontent.com/a/" in src: 
                        continue
                    
                    try:
                        # 核心动作：先悬停在图片上，这通常会触发工具栏显示
                        await img.hover()
                        await asyncio.sleep(1)

                        # 查找下载按钮：尝试多种可能的路径
                        # 1. 直接在图片父级寻找
                        # 2. 寻找带有 download 图标的按钮
                        download_btn = await page.query_selector("button:has(mat-icon:has-text('download')), button[aria-label*='Download'], button[aria-label*='下载']")
                        
                        if download_btn:
                            print("🎯 捕捉到下载按钮，正在执行自动点击...")
                            await download_btn.click()
                            processed_imgs.add(src)
                            # 给下载留出响应时间
                            await asyncio.sleep(3)
                    except:
                        pass
                await asyncio.sleep(2)

        asyncio.create_task(auto_download_task())

        try:
            await asyncio.wait([
                asyncio.create_task(stop_event.wait()),
                asyncio.create_task(asyncio.sleep(180))
            ], return_when=asyncio.FIRST_COMPLETED)
        except KeyboardInterrupt:
            pass
        finally:
            await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_file", required=True)
    args = parser.parse_args()
    asyncio.run(run(args.prompt_file))
