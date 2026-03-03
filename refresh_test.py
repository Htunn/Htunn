#!/usr/bin/env python3
"""
Page Refresh Test Script
Refreshes a given URL multiple times using Playwright for Chrome automation
with anti-abuse detection measures
"""

import asyncio
import sys
import time
import random


async def refresh_page_test(url: str, refresh_count: int = 1000, 
                           delay_min: float = 2.0, delay_max: float = 5.0,
                           batch_size: int = 50, batch_delay: float = 10.0):
    """
    Opens a URL in Chrome and refreshes it multiple times with human-like behavior.
    
    Args:
        url: The URL to open and refresh
        refresh_count: Number of times to refresh (default: 1000)
        delay_min: Minimum delay between refreshes in seconds (default: 2.0)
        delay_max: Maximum delay between refreshes in seconds (default: 5.0)
        batch_size: Number of refreshes before taking a longer break (default: 50)
        batch_delay: Delay in seconds between batches (default: 10.0)
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Error: Playwright is not installed.")
        print("Please install it with: pip install playwright")
        print("Then run: playwright install chromium")
        sys.exit(1)
    
    async with async_playwright() as p:
        # Launch browser with realistic user agent
        print("Launching Chrome...")
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create context with realistic user agent and viewport
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        print(f"Opening URL: {url}")
        print(f"Settings: {delay_min:.1f}-{delay_max:.1f}s delay, "
              f"{batch_size} refreshes per batch, {batch_delay:.1f}s batch delay")
        
        await page.goto(url, wait_until="domcontentloaded")
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        # Refresh the page multiple times
        print(f"\nStarting {refresh_count} refreshes...")
        start_time = time.time()
        successful_refreshes = 0
        consecutive_errors = 0
        
        for i in range(refresh_count):
            try:
                # Check if we need a batch break
                if i > 0 and i % batch_size == 0:
                    print(f"⏸  Batch break after {i} refreshes (waiting {batch_delay:.1f}s)...")
                    await asyncio.sleep(batch_delay)
                
                # Random delay between refreshes (human-like behavior)
                delay = random.uniform(delay_min, delay_max)
                await asyncio.sleep(delay)
                
                # Reload the page
                await page.reload(wait_until="domcontentloaded", timeout=30000)
                successful_refreshes += 1
                consecutive_errors = 0
                
                # Progress update every 25 refreshes
                if (i + 1) % 25 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (i + 1)
                    remaining = (refresh_count - i - 1) * avg_time
                    print(f"Progress: {i + 1}/{refresh_count} refreshes "
                          f"| Elapsed: {elapsed:.1f}s | ETA: {remaining:.1f}s "
                          f"| Success rate: {successful_refreshes}/{i+1}")
                
            except Exception as e:
                consecutive_errors += 1
                print(f"⚠️  Error on refresh {i + 1}: {e}")
                
                # If we get too many consecutive errors, implement exponential backoff
                if consecutive_errors >= 3:
                    backoff_time = min(60, 5 * (2 ** (consecutive_errors - 3)))
                    print(f"⏳ Multiple errors detected. Backing off for {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
                    
                    # Try to recover by creating a new page
                    if consecutive_errors >= 5:
                        print("🔄 Attempting to recover by creating new page...")
                        try:
                            await page.close()
                            page = await context.new_page()
                            await page.goto(url, wait_until="domcontentloaded")
                            consecutive_errors = 0
                            print("✓ Recovery successful")
                        except Exception as recovery_error:
                            print(f"❌ Recovery failed: {recovery_error}")
                            print("Stopping test...")
                            break
                
                continue
        
        total_time = time.time() - start_time
        success_rate = (successful_refreshes / refresh_count) * 100
        
        print(f"\n{'='*60}")
        print(f"✓ Test completed!")
        print(f"Successful refreshes: {successful_refreshes}/{refresh_count} ({success_rate:.1f}%)")
        print(f"Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        if successful_refreshes > 0:
            print(f"Average time per refresh: {total_time/successful_refreshes:.3f}s")
        print(f"{'='*60}")
        
        # Keep browser open for a few seconds to see final state
        await asyncio.sleep(3)
        await browser.close()


async def main():
    """Main entry point"""
    url = "https://github.com/Htunn"
    refresh_count = 1000
    
    # Conservative defaults to avoid abuse detection
    delay_min = 2.0  # Minimum 2s between refreshes
    delay_max = 5.0  # Maximum 5s between refreshes
    batch_size = 50  # Take a break every 50 refreshes
    batch_delay = 10.0  # 10s break between batches
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        url = sys.argv[1]
    if len(sys.argv) > 2:
        refresh_count = int(sys.argv[2])
    if len(sys.argv) > 3:
        delay_min = float(sys.argv[3])
    if len(sys.argv) > 4:
        delay_max = float(sys.argv[4])
    
    print(f"Page Refresh Test Script (Anti-Abuse Protection Enabled)")
    print(f"URL: {url}")
    print(f"Refresh count: {refresh_count}")
    print(f"Delay between refreshes: {delay_min}-{delay_max}s (randomized)")
    print(f"Batch breaks: Every {batch_size} refreshes, wait {batch_delay}s")
    print("-" * 60)
    
    estimated_time = (refresh_count * ((delay_min + delay_max) / 2) + 
                     (refresh_count // batch_size) * batch_delay)
    print(f"⏱️  Estimated total time: {estimated_time/60:.1f} minutes")
    print("-" * 60)
    
    try:
        await refresh_page_test(url, refresh_count, delay_min, delay_max, 
                               batch_size, batch_delay)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
