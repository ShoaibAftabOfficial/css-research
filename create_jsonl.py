import re
import urllib.request
import urllib.error
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_files_from_repo(owner, repo):
    branches = ['main', 'master']
    source_code = ""
    for branch in branches:
        try:
            # First fetch package.json
            pkg_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/package.json"
            req = urllib.request.Request(pkg_url, headers={'User-Agent': 'Mozilla/5.0 Agent-Jules'})
            with urllib.request.urlopen(req, timeout=5) as response:
                pkg_json = json.loads(response.read().decode())
                css_file_paths = []
                for key in ['style', 'main', 'unpkg', 'jsdelivr']:
                    val = pkg_json.get(key, '')
                    if isinstance(val, str) and val.endswith(('.css', '.scss', '.sass', '.less')):
                        css_file_paths.append(val)

                if not css_file_paths:
                    css_file_paths = ['style.css', 'src/style.css', 'dist/style.css', 'index.css', 'css/style.css', 'dist/css/style.css']

                for file_path in css_file_paths:
                    if file_path.startswith('./'):
                        file_path = file_path[2:]
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
                    try:
                        file_req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0 Agent-Jules'})
                        with urllib.request.urlopen(file_req, timeout=5) as file_resp:
                            source_code += file_resp.read().decode(errors='ignore') + "\n"
                            if len(source_code) > 100000: # limit to avoid giant files taking too long to regex
                                break
                    except:
                        pass
            if source_code:
                return source_code
        except Exception:
            pass
    return source_code

def create_jsonl():
    input_file = 'npm_zero_dependency_frameworks.md'
    output_file = 'frameworks_source.jsonl'

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}'.")
        return

    data_lines = [line for line in lines if line.startswith('|') and not line.startswith('| Rank |') and not line.startswith('|---|')]

    def process_single(line):
        parts = line.split('|')
        if len(parts) >= 5:
            repo_link = parts[2].strip()
            repo_match = re.search(r'\[(.*?)\]\((.*?)\)', repo_link)
            if not repo_match:
                return None

            repo_full_name = repo_match.group(1)
            owner_repo = repo_full_name.split('/')
            if len(owner_repo) != 2:
                return None

            owner, repo = owner_repo
            source_code = fetch_files_from_repo(owner, repo)
            if source_code:
                # Basic minification to store cleanly in JSONL
                source_code = source_code.replace('\n', ' ').replace('\r', ' ')
                source_code = re.sub(r'\s+', ' ', source_code).strip()
                return {"name": repo_full_name, "source_code": source_code}
        return None

    results = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(process_single, line): line for line in data_lines}
        for idx, future in enumerate(as_completed(futures), 1):
            res = future.result()
            if res:
                results.append(res)
            if idx % 50 == 0:
                print(f"Processed {idx}/{len(data_lines)} frameworks for JSONL.")

    with open(output_file, 'w', encoding='utf-8') as f:
        for res in results:
            f.write(json.dumps(res) + "\n")
    print(f"JSONL created successfully: {output_file}")

if __name__ == "__main__":
    create_jsonl()
