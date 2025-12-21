
import json
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.google.com/search?q=test")
        
        # Create CDP session
        client = page.context.new_cdp_session(page)
        
        # Capture snapshot
        tree = client.send(
            "DOMSnapshot.captureSnapshot",
            {
                "computedStyles": [],
                "includeDOMRects": True,
                "includePaintOrder": True,
            },
        )
        
        print(f"Number of documents: {len(tree['documents'])}")
        doc0 = tree['documents'][0]
        nodes = doc0['nodes']
        
        if 'contentDocumentIndex' in nodes:
            print(f"contentDocumentIndex found in doc 0: {nodes['contentDocumentIndex']}")
            # Find which nodes have this property
            for i, idx in enumerate(nodes['contentDocumentIndex']):
                if idx != -1: # usually -1 or undefined if not present, but here it's a list of indices matching the nodes that have it?
                    # Actually, CDP often returns sparse arrays or arrays of same length.
                    # Let's check the length.
                    pass
            print(f"Length of contentDocumentIndex: {len(nodes['contentDocumentIndex'])}")
            print(f"Length of nodeName: {len(nodes['nodeName'])}")
        else:
            print("contentDocumentIndex NOT found in doc 0 nodes")

        browser.close()

if __name__ == "__main__":
    run()
