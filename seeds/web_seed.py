import re
import urllib.request

def execute(agent_output: str) -> str:
    url_matches = re.findall(r"\[FETCH_URL:\s*(.*?)\]", agent_output)
    status = ""

    for target_url in url_matches:
        target_url = target_url.strip()
        print(f"🌐 [Seed Triggered] Fetching web address contents: {target_url}")
        try:
            req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                html = response.read().decode('utf-8', errors='ignore')
                text = re.sub(r'<script.*?>.*?</script>|<style.*?>.*?</style>', '', html, flags=re.DOTALL)
                text = re.sub(r'<[^>]*>', ' ', text)
                compressed_body = " ".join(text.split())[:2000]
                status += f"\n[System Scraped Data from '{target_url}':\n{compressed_body}]"
        except Exception as e:
            status += f"\n[System Error fetching URL '{target_url}': {e}]"

    return status
