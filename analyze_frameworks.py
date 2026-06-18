import re
import os
import sys
import urllib.request
import urllib.error
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class UniversalCSSAnalyzer:
    """
    یونیورسل سی ایس ایس فریم ورک اینالائزر
    یہ سکرپٹ کسی بھی سی ایس ایس فریم ورک سے اس کی ذاتی اختراعات (Abstractions) نکالنے کے لیے بنایا گیا ہے۔
    """

    def __init__(self):
        self.main_counter = 1

    def analyze_framework(self, name, rank, source_code):
        fw_id_str = f"{name} ({rank})"
        inventions = []

        w3c_directives = {
            'charset', 'import', 'namespace', 'media', 'supports', 'document', 'page',
            'font-face', 'keyframes', 'viewport', 'counter-style', 'font-feature-values', 'property'
        }
        directives = re.findall(r'@([a-zA-Z0-9-]+)', source_code)
        for d in sorted(list(set(directives))):
            if d not in w3c_directives:
                inventions.append(self._create_entry(
                    fw_id_str, f"Custom Directive: @{d}", f"@{d}", f"@{d} {{ ... }}",
                    f"A framework-specific directive that extends CSS functionality.",
                    f"یہ فریم ورک کا ایک مخصوص ڈائریکٹو ہے جو سی ایس ایس کی فعالیت کو بڑھاتا ہے۔"
                ))

        w3c_pseudo_classes = {
            'hover', 'focus', 'active', 'visited', 'link', 'target', 'checked', 'disabled',
            'enabled', 'empty', 'first-child', 'last-child', 'only-child', 'root', 'not',
            'nth-child', 'nth-last-child', 'first-of-type', 'last-of-type', 'only-of-type',
            'nth-of-type', 'nth-last-of-type', 'read-only', 'read-write', 'required', 'optional'
        }
        modifiers = re.findall(r'([a-zA-Z0-9-]+):', source_code)
        for m in sorted(list(set(modifiers))):
            if m not in w3c_pseudo_classes and not m.startswith(('sm', 'md', 'lg', 'xl', '2xl')):
                inventions.append(self._create_entry(
                    fw_id_str, f"Custom Modifier: {m}:", f"{m}:", f"<div class=\"{m}:text-red-500\">",
                    f"A unique framework-specific state or condition modifier.",
                    f"یہ فریم ورک کی ایک منفرد حالت یا شرط کی تبدیلی کی لاجک ہے۔"
                ))
            elif m.startswith(('sm', 'md', 'lg', 'xl', '2xl')):
                 inventions.append(self._create_entry(
                    fw_id_str, f"Responsive Modifier: {m}:", f"{m}:", f"<div class=\"{m}:text-lg\">",
                    f"A framework-specific responsive breakpoint modifier.",
                    f"یہ فریم ورک کا ایک مخصوص رسپانسیو بریک پوائنٹ موڈیفائر ہے۔"
                ))

        if re.search(r'\[[^\]]+\]', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Arbitrary Values Logic", "[...]", "class=\"h-[123px] bg-[#ff0000]\"",
                "Logic to generate styles from user-defined values at runtime.",
                "رن ٹائم پر صارف کی اپنی دی گئی ویلیوز سے اسٹائل بنانے کی منطق۔"
            ))

        if re.search(r'space-[xy]-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Space-Between Utilities", "space-x-* / space-y-*", "<div class=\"space-x-4\">",
                "Utility to add space between child elements automatically.",
                "یہ بچوں کے ایلیمنٹس کے درمیان خود بخود فاصلہ پیدا کرنے کی یوٹیلٹی ہے۔"
            ))
        if re.search(r'divide-[xy]-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Divide Utilities", "divide-x-* / divide-y-*", "<div class=\"divide-y divide-gray-200\">",
                "Utility to add borders between child elements automatically.",
                "یہ بچوں کے ایلیمنٹس کے درمیان خود بخود بارڈرز ڈالنے کی یوٹیلٹی ہے۔"
            ))
        if re.search(r'ring-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Ring Utilities", "ring-*", "<button class=\"ring-2 ring-blue-500\">",
                "Utility to create accessible focus rings using box-shadow.",
                "یہ باکس شیڈو کا استعمال کرتے ہوئے قابل رسائی فوکس رنگ بنانے کی یوٹیلٹی ہے۔"
            ))
        if re.search(r'opacity-', source_code) and re.search(r'(bg|text)-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Theme-aware Opacity Modifiers", "bg-opacity-* / text-opacity-*", "<div class=\"bg-blue-500 bg-opacity-50\">",
                "Utilities to control the opacity of background or text colors.",
                "یہ بیک گراؤنڈ یا ٹیکسٹ کے رنگوں کی شفافیت کو کنٹرول کرنے کی یوٹیلٹی ہے۔"
            ))
        if re.search(r'-(m|p|top|bottom|left|right)-[0-9]', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Negative Values Logic", "-mt-*", "<div class=\"-mt-4\">",
                "Logic to apply negative margins or positions easily.",
                "یہ منفی مارجن یا پوزیشنز کو آسانی سے لاگو کرنے کی منطق ہے۔"
            ))
        if re.search(r'[a-zA-Z0-9-]+:[a-zA-Z0-9-]+:[a-zA-Z0-9-]+:', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Stacked Modifiers", "dark:hover:bg-red-500", "<div class=\"dark:hover:bg-red-500\">",
                "Ability to combine multiple state/responsive modifiers.",
                "یہ متعدد حالتوں/رسپانسیو موڈیفائرز کو یکجا کرنے کی صلاحیت ہے۔"
            ))
        if re.search(r'group/{[a-zA-Z0-9-]+}', source_code) or re.search(r'peer/{[a-zA-Z0-9-]+}', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Group/Peer Labeling", "group/{name}", "<div class=\"group/item\">",
                "Ability to name groups/peers for more specific styling.",
                "یہ زیادہ مخصوص اسٹائلنگ کے لیے گروپس/پیئرز کو نام دینے کی صلاحیت ہے۔"
            ))
        if re.search(r'text-\[clamp\(', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Fluid Typography Logic", "text-[clamp(...)]", "<p class=\"text-[clamp(1rem,2vw,2rem)]\">",
                "Logic for responsive text sizing using CSS clamp() function.",
                "یہ سی ایس ایس clamp() فنکشن کا استعمال کرتے ہوئے رسپانسیو ٹیکسٹ سائزنگ کی منطق ہے۔"
            ))
        if re.search(r'@container', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Container Queries Abstraction", "@container", "@container (min-width: 768px) { ... }",
                "Abstraction for styling based on parent container size, not viewport.",
                "یہ ویو پورٹ کے بجائے پیرنٹ کنٹینر کے سائز کی بنیاد پر اسٹائلنگ کے لیے ایک تجرید ہے۔"
            ))
        if re.search(r'(start|end)-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Automatic RTL Support", "start-* / end-*", "<div class=\"ps-4\">",
                "Utilities for logical properties (start/end) for RTL/LTR layouts.",
                "یہ RTL/LTR لے آؤٹس کے لیے منطقی خصوصیات (start/end) کی یوٹیلٹیز ہیں۔"
            ))

        return inventions

    def _create_entry(self, fw_id_str, inv_name, name_code, app_code, eng_def, urd_def):
        entry = {
            "Main ID": 0, # Will be set later
            "Framework ID": fw_id_str,
            "Invention Name": inv_name,
            "Name Code": name_code,
            "Application Code": app_code,
            "English Definition": eng_def,
            "Urdu Definition": urd_def
        }
        return entry

    def generate_report_header(self):
        header = "# Universal CSS Framework Inventions Report\n\n"
        header += "## اصطلاحی نام: Framework-specific Abstractions / Proprietary Directives\n\n"
        header += "| نمبر شمار | فریم ورک (ID) | اختراع کا نام | نیم کوڈ | استعمال کا کوڈ | English Definition | اردو تعریف |\n"
        header += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        return header

    def generate_report_rows(self, inventions):
        rows = ""
        for inv in inventions:
            rows += f"| {inv['Main ID']} | {inv['Framework ID']} | {inv['Invention Name']} | `{inv['Name Code']}` | `{inv['Application Code']}` | {inv['English Definition']} | {inv['Urdu Definition']} |\n"
        return rows


def fetch_files_from_repo(owner, repo):
    branches = ['main', 'master']
    source_code = ""
    for branch in branches:
        try:
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
                            if len(source_code) > 100000: # Limit length
                                break
                    except:
                        pass
            if source_code:
                return source_code
        except Exception:
            pass
    return source_code

def process_and_analyze_frameworks():
    input_file = 'npm_zero_dependency_frameworks.md'

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}'.")
        return

    data_lines = [line for line in lines if line.startswith('|') and not line.startswith('| Rank |') and not line.startswith('|---|')]

    frameworks_to_process = []

    for line in data_lines:
        parts = line.split('|')
        if len(parts) >= 5:
            # Extract rank
            rank_match = re.search(r'\*\*(\d+)\*\*', parts[1])
            rank = int(rank_match.group(1)) if rank_match else 0

            repo_link = parts[2].strip()
            repo_match = re.search(r'\[(.*?)\]\((.*?)\)', repo_link)
            if repo_match:
                repo_full_name = repo_match.group(1)
                owner_repo = repo_full_name.split('/')
                if len(owner_repo) == 2:
                    frameworks_to_process.append({
                        'rank': rank,
                        'name': repo_full_name,
                        'owner': owner_repo[0],
                        'repo': owner_repo[1]
                    })

    # Sort frameworks properly by their rank
    frameworks_to_process.sort(key=lambda x: x['rank'])

    print(f"Starting analysis for {len(frameworks_to_process)} frameworks...")

    os.makedirs('frameworks_source_code', exist_ok=True)

    analyzer = UniversalCSSAnalyzer()

    def process_single(fw_data):
        owner, repo = fw_data['owner'], fw_data['repo']
        name = fw_data['name']
        rank = fw_data['rank']

        source_code = fetch_files_from_repo(owner, repo)
        if source_code:
            # Save the source code
            safe_name = name.replace('/', '_')
            with open(f"frameworks_source_code/{safe_name}.css", 'w', encoding='utf-8') as f:
                f.write(source_code)

            # Truncate for regex performance if too large
            if len(source_code) > 20000:
                source_code = source_code[:20000]

            inventions = analyzer.analyze_framework(name, rank, source_code)
            return rank, inventions
        return rank, []

    # Store results by rank
    all_results = {}

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(process_single, fw): fw for fw in frameworks_to_process}
        count = 0
        for future in as_completed(futures):
            count += 1
            try:
                rank, inventions = future.result()
                all_results[rank] = inventions
                if count % 50 == 0:
                    print(f"Processed {count}/{len(frameworks_to_process)} frameworks...")
            except Exception as e:
                print(f"Error processing framework: {e}")

    # Generate Reports in batches of 50
    batch_size = 50
    master_report_content = analyzer.generate_report_header()
    batch_reports = []

    main_counter = 1

    for i in range(0, len(frameworks_to_process), batch_size):
        batch = frameworks_to_process[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        batch_inventions = []

        for fw in batch:
            rank = fw['rank']
            if rank in all_results:
                for inv in all_results[rank]:
                    inv['Main ID'] = main_counter
                    main_counter += 1
                    batch_inventions.append(inv)

        batch_output_file = f'framework_inventions_report_batch_{batch_num}.md'
        batch_report_content = analyzer.generate_report_header() + analyzer.generate_report_rows(batch_inventions)

        with open(batch_output_file, 'w', encoding='utf-8') as f:
            f.write(batch_report_content)
        batch_reports.append(batch_output_file)

        master_report_content += analyzer.generate_report_rows(batch_inventions)
        print(f"Batch {batch_num} report generated: {batch_output_file}")

    master_output_file = 'framework_inventions_report_master.md'
    with open(master_output_file, 'w', encoding='utf-8') as f:
        f.write(master_report_content)

    print(f"Master report generated: {master_output_file}")
    print(f"Total inventions found: {main_counter - 1}")

if __name__ == "__main__":
    process_and_analyze_frameworks()
