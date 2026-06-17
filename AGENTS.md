# Instructions for Jules (Autonomous Agent)

**Objective:** Your task is to extract a strictly filtered list of zero-dependency Core CSS Frameworks. 
You are provided with a file named `css-frameworks.md` containing a table of over 1,300 CSS frameworks. 
You must run the Python script below to dynamically check the live `package.json` of every single framework in that file.

### Filtration Rules:
1. **NPM Verification:** The framework MUST exist on NPM (meaning it has a `package.json`). If it does not, discard it.
2. **Zero Framework Dependencies:** The framework's `dependencies` and `peerDependencies` must **NOT** contain any other CSS framework or wrapper (like `tailwindcss`, `bootstrap`, `react-bootstrap`, `vue`, etc.).
3. **DevDependencies Exception:** As per the system architect's instructions, frameworks *are* allowed to have Tailwind or Bootstrap inside their `devDependencies` (for their docs/testing sites). This is perfectly fine. The strict zero-dependency rule only applies to `dependencies` and `peerDependencies`.

---

## Action Plan

1. **Create the Script:** Save the Python code below as `npm_verifier.py` in your working directory.
2. **Execute:** Ensure that the input file `css-frameworks.md` is in the same directory. Run the script using `python3 npm_verifier.py`.
3. **Wait:** This script will make over 1,300 live HTTP requests to GitHub. It has a built-in sleep timer to prevent rate-limiting. **It may take 1 to 2 hours to complete depending on network speed.** Let it run in the background.
4. **Final Result:** Once it finishes, it will generate a new file called `npm_zero_dependency_frameworks.md`. Present this finalized list to the user. Do **NOT** modify or delete the original `css-frameworks.md` file.

---

## Python Script (`npm_verifier.py`)

```python
import re
import json
import urllib.request
import urllib.error
import time

def fetch_package_json(owner, repo):
    branches = ['main', 'master']
    for branch in branches:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/package.json"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Agent-Jules-Verifier'})
            # 10 second timeout for slow networks
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
        except Exception:
            pass
    return None

def has_css_framework_dependency(pkg_json):
    deps = pkg_json.get('dependencies', {})
    peer_deps = pkg_json.get('peerDependencies', {})
    
    # We strictly check dependencies and peerDependencies. devDependencies are ignored.
    all_deps = list(deps.keys()) + list(peer_deps.keys())
    
    banned_deps = [
        'tailwindcss', 'bootstrap', 'bulma', 'foundation-sites', 
        'material-ui', '@mui/material', 'vuetify', 'react-bootstrap',
        'styled-components', '@emotion/react', '@emotion/styled',
        'chakra-ui', '@chakra-ui/react', 'uikit', 'semantic-ui', 'tachyons',
        'tailwind', 'windicss', 'unocss'
    ]
    
    for dep in all_deps:
        dep_lower = dep.lower()
        if any(banned in dep_lower for banned in banned_deps):
            # Exception for a framework depending on its own internal packages
            pkg_name = pkg_json.get('name', '').lower()
            if 'bootstrap' in pkg_name and 'bootstrap' in dep_lower:
                continue
            if 'tailwind' in pkg_name and 'tailwind' in dep_lower:
                continue
            return True
            
    return False

def process_frameworks():
    input_file = 'css-frameworks.md'
    output_file = 'npm_zero_dependency_frameworks.md'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}'. Ensure it exists in the same directory.")
        return
        
    table_headers = []
    data_lines = []
    
    in_table = False
    for line in lines:
        if line.startswith('| Rank |') or line.startswith('|---|'):
            table_headers.append(line)
            in_table = True
        elif in_table and line.startswith('|'):
            data_lines.append(line)
            
    valid_frameworks = []
    total = len(data_lines)
    
    print(f"Starting Live NPM package.json verification for {total} frameworks...")
    print("This process will take significant time. Please wait...")
    
    for idx, line in enumerate(data_lines, 1):
        parts = line.split('|')
        if len(parts) >= 5:
            repo_link = parts[2].strip()
            
            repo_match = re.search(r'\[(.*?)\]\((.*?)\)', repo_link)
            if not repo_match:
                continue
                
            repo_full_name = repo_match.group(1)
            owner_repo = repo_full_name.split('/')
            if len(owner_repo) != 2:
                continue
                
            owner, repo = owner_repo
            
            pkg_json = fetch_package_json(owner, repo)
            
            if pkg_json is None:
                print(f"[{idx}/{total}] SKIP: No package.json (Not on NPM) - {repo_full_name}")
                continue
                
            if 'name' not in pkg_json:
                print(f"[{idx}/{total}] SKIP: Invalid package.json - {repo_full_name}")
                continue
                
            if has_css_framework_dependency(pkg_json):
                print(f"[{idx}/{total}] SKIP: Has Framework Dependency - {repo_full_name}")
                continue
                
            print(f"[{idx}/{total}] KEEP: Zero Dependency NPM Framework - {repo_full_name}")
            valid_frameworks.append(line)
            
        # Add a sleep to prevent GitHub from temporarily blocking the IP
        time.sleep(0.5) 
            
    final_output = []
    for i, line in enumerate(valid_frameworks, 1):
        # Renumber the rank column
        new_line = re.sub(r'\|\s*\*\*\d+\*\*\s*\|', f'| **{i}** |', line, count=1)
        final_output.append(new_line)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<div dir="rtl" style="text-align: right; direction: rtl;">\n\n')
        f.write("# تصدیق شدہ (Verified) خودمختار سی ایس ایس فریم ورکس\n\n")
        f.write(f"**ابتدائی لسٹ:** {total} فریم ورکس\n")
        f.write(f"**حتمی تعداد (NPM تصدیق کے بعد):** {len(final_output)} فریم ورکس\n\n")
        f.write("> [!SUCCESS]\n")
        f.write("> اس لسٹ میں موجود ہر فریم ورک کی لائیو package.json چیک کی گئی ہے۔ جن کی dependencies میں کوئی اور فریم ورک شامل تھا، انہیں نکال دیا گیا ہے۔ البتہ devDependencies کو نظر انداز کیا گیا ہے۔\n\n")
        f.write("</div>\n\n")
        
        for h in table_headers:
            f.write(h)
        for l in final_output:
            f.write(l)
            
    print(f"\nVerification complete! Kept {len(final_output)} frameworks out of {total}.")
    print(f"File saved to {output_file}")

if __name__ == "__main__":
    process_frameworks()
```
