import re
import json
import os
import sys

class UniversalCSSAnalyzer:
    """
    یونیورسل سی ایس ایس فریم ورک اینالائزر
    یہ سکرپٹ کسی بھی سی ایس ایس فریم ورک سے اس کی ذاتی اختراعات (Abstractions) نکالنے کے لیے بنایا گیا ہے۔
    """

    def __init__(self):
        # W3C اسٹینڈرڈ پراپرٹیز کی ایک بنیادی لسٹ (یہ لسٹ مزید وسیع کی جا سکتی ہے)
        self.standard_css_keywords = {
            # Properties
            'align-content', 'align-items', 'align-self', 'all', 'animation', 'animation-delay',
            'animation-direction', 'animation-duration', 'animation-fill-mode', 'animation-iteration-count',
            'animation-name', 'animation-play-state', 'animation-timing-function', 'backface-visibility',
            'background', 'background-attachment', 'background-blend-mode', 'background-clip',
            'background-color', 'background-image', 'background-origin', 'background-position',
            'background-repeat', 'background-size', 'border', 'border-bottom', 'border-bottom-color',
            'border-bottom-left-radius', 'border-bottom-right-radius', 'border-bottom-style',
            'border-bottom-width', 'border-collapse', 'border-color', 'border-image',
            'border-image-outset', 'border-image-repeat', 'border-image-slice', 'border-image-source',
            'border-image-width', 'border-left', 'border-left-color', 'border-left-style',
            'border-left-width', 'border-radius', 'border-right', 'border-right-color',
            'border-right-style', 'border-right-width', 'border-spacing', 'border-style',
            'border-top', 'border-top-color', 'border-top-left-radius', 'border-top-right-radius',
            'border-top-style', 'border-top-width', 'border-width', 'bottom', 'box-decoration-break',
            'box-shadow', 'box-sizing', 'caption-side', 'caret-color', 'clear', 'clip', 'color',
            'column-count', 'column-fill', 'column-gap', 'column-rule', 'column-rule-color',
            'column-rule-style', 'column-rule-width', 'column-span', 'column-width', 'columns',
            'content', 'counter-increment', 'counter-reset', 'cursor', 'direction', 'display',
            'empty-cells', 'filter', 'flex', 'flex-basis', 'flex-direction', 'flex-flow',
            'flex-grow', 'flex-shrink', 'flex-wrap', 'float', 'font', 'font-family', 'font-feature-settings',
            'font-kerning', 'font-size', 'font-size-adjust', 'font-stretch', 'font-style',
            'font-variant', 'font-variant-caps', 'font-weight', 'gap', 'grid', 'grid-area',
            'grid-auto-columns', 'grid-auto-flow', 'grid-auto-rows', 'grid-column',
            'grid-column-end', 'grid-column-gap', 'grid-column-start', 'grid-gap',
            'grid-row', 'grid-row-end', 'grid-row-gap', 'grid-row-start', 'grid-template',
            'grid-template-areas', 'grid-template-columns', 'grid-template-rows', 'height',
            'hyphens', 'image-rendering', 'isolation', 'justify-content', 'left', 'letter-spacing',
            'line-height', 'list-style', 'list-style-image', 'list-style-position',
            'list-style-type', 'margin', 'margin-bottom', 'margin-left', 'margin-right',
            'margin-top', 'max-height', 'max-width', 'min-height', 'min-width', 'mix-blend-mode',
            'object-fit', 'object-position', 'opacity', 'order', 'outline', 'outline-color',
            'outline-offset', 'outline-style', 'outline-width', 'overflow', 'overflow-x',
            'overflow-y', 'padding', 'padding-bottom', 'padding-left', 'padding-right',
            'padding-top', 'page-break-after', 'page-break-before', 'page-break-inside',
            'perspective', 'perspective-origin', 'pointer-events', 'position', 'quotes',
            'resize', 'right', 'row-gap', 'scroll-behavior', 'tab-size', 'table-layout',
            'text-align', 'text-align-last', 'text-decoration', 'text-decoration-color',
            'text-decoration-line', 'text-decoration-style', 'text-indent', 'text-justify',
            'text-overflow', 'text-shadow', 'text-transform', 'top', 'transform',
            'transform-origin', 'transform-style', 'transition', 'transition-delay',
            'transition-duration', 'transition-property', 'transition-timing-function',
            'unicode-bidi', 'user-select', 'vertical-align', 'visibility', 'white-space',
            'width', 'word-break', 'word-spacing', 'word-wrap', 'writing-mode', 'z-index',
            # Pseudo-classes/elements (common ones)
            'hover', 'focus', 'active', 'visited', 'first-child', 'last-child', 'nth-child',
            'before', 'after', 'placeholder', 'selection', 'marker', 'file'
        }

        self.frameworks_analyzed_count = {}
        self.main_counter = 1

    def analyze_framework(self, name, source_code):
        if name not in self.frameworks_analyzed_count:
            self.frameworks_analyzed_count[name] = 0
        self.frameworks_analyzed_count[name] += 1
        fw_instance_id = self.frameworks_analyzed_count[name]
        fw_id_str = f"{name} ({fw_instance_id})"
        inventions = []

        # 1. Custom Directives (e.g., @apply, @screen, @layer, @mixin, @extend)
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

        # 2. Custom Modifiers/Variants (e.g., group-hover:, peer-focus:, sm:, dark:)
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

        # 3. Arbitrary Values Logic (e.g., h-[123px], bg-[#ff0000])
        if re.search(r'\[[^\]]+\]', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Arbitrary Values Logic", "[...]", "class=\"h-[123px] bg-[#ff0000]\"",
                "Logic to generate styles from user-defined values at runtime.",
                "رن ٹائم پر صارف کی اپنی دی گئی ویلیوز سے اسٹائل بنانے کی منطق۔"
            ))

        # 4. Special Utility Patterns (Heuristic based on common framework inventions)
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
            "Main ID": self.main_counter,
            "Framework ID": fw_id_str,
            "Invention Name": inv_name,
            "Name Code": name_code,
            "Application Code": app_code,
            "English Definition": eng_def,
            "Urdu Definition": urd_def
        }
        self.main_counter += 1
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

    def run_analysis_batched(self, input_md_file, batch_size=50):
        all_frameworks_data = []
        try:
            with open(input_md_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            fw_data = json.loads(line)
                            if "name" in fw_data and "source_code" in fw_data:
                                all_frameworks_data.append(fw_data)
                            else:
                                print(f"Skipping malformed JSON line: {line}")
                        except json.JSONDecodeError:
                            print(f"Skipping non-JSON line: {line}")
                    else:
                        print(f"Skipping non-JSON line: {line}")
        except FileNotFoundError:
            print(f"Error: Input file '{input_md_file}' not found.")
            sys.exit(1)

        # Prioritize specific frameworks (e.g., Tailwind CSS) into their own batches
        prioritized_frameworks = []
        remaining_frameworks = []
        for fw in all_frameworks_data:
            if fw['name'] == 'Tailwind CSS': # Example of a prioritized framework
                prioritized_frameworks.append(fw)
            else:
                remaining_frameworks.append(fw)

        # Combine prioritized and remaining for batching
        frameworks_to_process = prioritized_frameworks + remaining_frameworks

        batch_reports = []
        master_report_content = self.generate_report_header()

        for i in range(0, len(frameworks_to_process), batch_size):
            batch = frameworks_to_process[i:i + batch_size]
            batch_inventions = []

            batch_num = (i // batch_size) + 1
            batch_output_file = f'framework_inventions_report_batch_{batch_num}.md'

            print(f"Processing batch {batch_num} with {len(batch)} frameworks...")

            for fw_data in batch:
                print(f"  Analyzing framework: {fw_data['name']}")
                inventions = self.analyze_framework(fw_data["name"], fw_data["source_code"])
                batch_inventions.extend(inventions)

            batch_report_content = self.generate_report_header() + self.generate_report_rows(batch_inventions)
            with open(batch_output_file, 'w', encoding='utf-8') as f:
                f.write(batch_report_content)
            batch_reports.append(batch_output_file)
            master_report_content += self.generate_report_rows(batch_inventions)
            print(f"Batch {batch_num} report generated: {batch_output_file}")

        master_output_file = 'framework_inventions_report_master.md'
        with open(master_output_file, 'w', encoding='utf-8') as f:
            f.write(master_report_content)
        print(f"Master report generated: {master_output_file}")
        print(f"Individual batch reports: {', '.join(batch_reports)}")

# استعمال کا طریقہ (Example Usage)
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_frameworks.py <input_markdown_file> [batch_size]")
        sys.exit(1)

    input_file_path = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50 # Default batch size

    analyzer = UniversalCSSAnalyzer()
    analyzer.run_analysis_batched(input_file_path, batch_size)
