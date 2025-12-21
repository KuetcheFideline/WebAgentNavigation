
import json
from playwright.sync_api import sync_playwright
from browser_env.processors import TextObervationProcessor
from browser_env.utils import BrowserConfig

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.google.com/search?q=test")
        
        client = page.context.new_cdp_session(page)
        
        # Initialize processor
        viewport_size = {"width": 1280, "height": 720}
        processor = TextObervationProcessor("html", False, viewport_size)
        
        # Fetch browser info (this will trigger the bounds calibration)
        browser_info = processor.fetch_browser_info(page, client)
        
        # Fetch page HTML (this will trigger the recursive parsing)
        dom_tree = processor.fetch_page_html(browser_info, page, client, False)
        
        print(f"Total nodes in DOM tree: {len(dom_tree)}")
        
        # Check if we have nodes from iframes
        # Nodes from iframes will have high IDs and likely be children of nodes with lower IDs
        # We can check if any node has a parentId that corresponds to an iframe
        
        # Also check if we have any text content that is likely inside an iframe (e.g. search results)
        # But raw node count comparison with previous run (79 nodes) is a good indicator.
        
        # Let's print some stats
        node_types = {}
        for node in dom_tree:
            nt = node["nodeName"]
            node_types[nt] = node_types.get(nt, 0) + 1
            
        print("Node types:", node_types)

        browser.close()

if __name__ == "__main__":
    run()
