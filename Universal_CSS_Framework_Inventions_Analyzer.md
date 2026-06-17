# Universal CSS Framework Inventions Analyzer (Python Script)

یہ دستاویز آپ کو ایک پائتھون سکرپٹ فراہم کرتی ہے جو کسی بھی سی ایس ایس فریم ورک کے سورس کوڈ کا تجزیہ کر کے اس کی ذاتی اختراعات (Framework-specific Abstractions) کو نکال کر ایک تفصیلی رپورٹ تیار کرے گا۔

## 1. سکرپٹ کا نام

آپ اس سکرپٹ کو `analyze_frameworks.py` کے نام سے محفوظ کر سکتے ہیں۔

## 2. استعمال کا طریقہ (ہدایات برائے Jules)

1.  **سکرپٹ کو محفوظ کریں:** اس دستاویز میں موجود پائتھون کوڈ کو `analyze_frameworks.py` کے نام سے ایک فائل میں محفوظ کریں۔
2.  **ان پٹ فائل تیار کریں:** آپ کی سی ایس ایس فریم ورکس کی فہرست `npm_zero_dependency_frameworks.md` میں موجود ہونی چاہیے۔ اس فائل میں ہر فریم ورک کی معلومات JSON فارمیٹ میں ایک نئی لائن پر ہونی چاہیے، جیسا کہ مثال میں دکھایا گیا ہے:
    ```json
    {"name": "Tailwind CSS", "source_code": "@tailwind base; @apply bg-red-500; group-hover:opacity-100; h-[10px];"}
    {"name": "Bootstrap", "source_code": "@mixin media-breakpoint-up($name, $breakpoints: $grid-breakpoints) { ... }"}
    ```
    **نوٹ:** جولز خود بخود `npm_zero_dependency_frameworks.md` فائل کو تلاش کر لے گا اگر وہ سکرپٹ کے ساتھ ہی موجود ہو۔ اگر یہ فائل کسی اور پاتھ پر ہے، تو آپ کو سکرپٹ چلاتے وقت اس کا پورا پاتھ دینا ہوگا۔
3.  **سکرپٹ چلائیں:** جولز کو درج ذیل کمانڈ کے ذریعے سکرپٹ چلانے کی ہدایت دیں:
    ```bash
    python3 analyze_frameworks.py npm_zero_dependency_frameworks.md
    ```
    اگر آپ کی ان پٹ فائل کا نام مختلف ہے یا وہ کسی اور پاتھ پر ہے، تو کمانڈ میں اس کا صحیح پاتھ دیں۔
4.  **رپورٹ حاصل کریں:** سکرپٹ چلنے کے بعد، یہ ایک `framework_inventions_report.md` نامی فائل تیار کرے گا جس میں تمام تجزیہ شدہ ڈیٹا آپ کے مطلوبہ فارمیٹ میں موجود ہوگا۔

## 3. سکرپٹ کا کوڈ (analyze_frameworks.py)

```python
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

        self.frameworks_analyzed = 0
        self.main_counter = 1

    def analyze_framework(self, name, source_code):
        self.frameworks_analyzed += 1
        inventions = []
        fw_id_str = f"{name} ({self.frameworks_analyzed})"

        # 1. Custom Directives (e.g., @apply, @screen, @layer, @mixin, @extend)
        # W3C directives: @charset, @import, @namespace, @media, @supports, @document, @page, @font-face, @keyframes, @viewport, @counter-style, @font-feature-values, @property
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
        # This is a heuristic approach, looking for patterns like 'word:'
        # Standard pseudo-classes are filtered out
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
            # Responsive modifiers (sm:, md:, etc.) are also framework-specific in their utility-first application
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
        # Space-between utilities
        if re.search(r'space-[xy]-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Space-Between Utilities", "space-x-* / space-y-*", "<div class=\"space-x-4\">",
                "Utility to add space between child elements automatically.",
                "یہ بچوں کے ایلیمنٹس کے درمیان خود بخود فاصلہ پیدا کرنے کی یوٹیلٹی ہے۔"
            ))
        # Divide utilities
        if re.search(r'divide-[xy]-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Divide Utilities", "divide-x-* / divide-y-*", "<div class=\"divide-y divide-gray-200\">",
                "Utility to add borders between child elements automatically.",
                "یہ بچوں کے ایلیمنٹس کے درمیان خود بخود بارڈرز ڈالنے کی یوٹیلٹی ہے۔"
            ))
        # Ring utilities
        if re.search(r'ring-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Ring Utilities", "ring-*", "<button class=\"ring-2 ring-blue-500\">",
                "Utility to create accessible focus rings using box-shadow.",
                "یہ باکس شیڈو کا استعمال کرتے ہوئے قابل رسائی فوکس رنگ بنانے کی یوٹیلٹی ہے۔"
            ))
        # Opacity modifiers (e.g., bg-opacity-50, text-opacity-75)
        if re.search(r'opacity-', source_code) and re.search(r'(bg|text)-', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Theme-aware Opacity Modifiers", "bg-opacity-* / text-opacity-*", "<div class=\"bg-blue-500 bg-opacity-50\">",
                "Utilities to control the opacity of background or text colors.",
                "یہ بیک گراؤنڈ یا ٹیکسٹ کے رنگوں کی شفافیت کو کنٹرول کرنے کی یوٹیلٹی ہے۔"
            ))
        # Negative values (e.g., -mt-4)
        if re.search(r'-(m|p|top|bottom|left|right)-[0-9]', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Negative Values Logic", "-mt-*", "<div class=\"-mt-4\">",
                "Logic to apply negative margins or positions easily.",
                "یہ منفی مارجن یا پوزیشنز کو آسانی سے لاگو کرنے کی منطق ہے۔"
            ))
        # Stacked Modifiers (e.g., dark:hover:)
        if re.search(r'[a-zA-Z0-9-]+:[a-zA-Z0-9-]+:[a-zA-Z0-9-]+:', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Stacked Modifiers", "dark:hover:bg-red-500", "<div class=\"dark:hover:bg-red-500\">",
                "Ability to combine multiple state/responsive modifiers.",
                "یہ متعدد حالتوں/رسپانسیو موڈیفائرز کو یکجا کرنے کی صلاحیت ہے۔"
            ))
        # Group/Peer Labeling (v3.2+)
        if re.search(r'group/{[a-zA-Z0-9-]+}', source_code) or re.search(r'peer/{[a-zA-Z0-9-]+}', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Group/Peer Labeling", "group/{name}", "<div class=\"group/item\">",
                "Ability to name groups/peers for more specific styling.",
                "یہ زیادہ مخصوص اسٹائلنگ کے لیے گروپس/پیئرز کو نام دینے کی صلاحیت ہے۔"
            ))
        # Fluid Typography (clamp) (v3+)
        if re.search(r'text-\[clamp\(', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Fluid Typography Logic", "text-[clamp(...)]", "<p class=\"text-[clamp(1rem,2vw,2rem)]\">",
                "Logic for responsive text sizing using CSS clamp() function.",
                "یہ سی ایس ایس clamp() فنکشن کا استعمال کرتے ہوئے رسپانسیو ٹیکسٹ سائزنگ کی منطق ہے۔"
            ))
        # Container Queries (@container) (v3.2+)
        if re.search(r'@container', source_code):
            inventions.append(self._create_entry(
                fw_id_str, "Container Queries Abstraction", "@container", "@container (min-width: 768px) { ... }",
                "Abstraction for styling based on parent container size, not viewport.",
                "یہ ویو پورٹ کے بجائے پیرنٹ کنٹینر کے سائز کی بنیاد پر اسٹائلنگ کے لیے ایک تجرید ہے۔"
            ))
        # RTL Support (start/end) (v3+)
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

    def generate_report(self, all_inventions):
        report = "# Universal CSS Framework Inventions Report\n\n"
        report += "## اصطلاحی نام: Framework-specific Abstractions / Proprietary Directives\n\n"
        report += "| نمبر شمار | فریم ورک (ID) | اختراع کا نام | نیم کوڈ | استعمال کا کوڈ | English Definition | اردو تعریف |\n"
        report += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"

        for inv in all_inventions:
            report += f"| {inv["Main ID"]} | {inv["Framework ID"]} | {inv["Invention Name"]} | `{inv["Name Code"]}` | `{inv["Application Code"]}` | {inv["English Definition"]} | {inv["Urdu Definition"]} |\n"

        return report

    def run_analysis(self, input_md_file):
        all_inventions = []
        try:
            with open(input_md_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            fw_data = json.loads(line)
                            if "name" in fw_data and "source_code" in fw_data:
                                print(f"Analyzing framework: {fw_data['name']}")
                                inventions = self.analyze_framework(fw_data["name"], fw_data["source_code"])
                                all_inventions.extend(inventions)
                            else:
                                print(f"Skipping malformed JSON line: {line}")
                        except json.JSONDecodeError:
                            print(f"Skipping non-JSON line: {line}")
                    else:
                        print(f"Skipping non-JSON line: {line}")
        except FileNotFoundError:
            print(f"Error: Input file '{input_md_file}' not found.")
            sys.exit(1)

        final_report = self.generate_report(all_inventions)
        output_file = 'framework_inventions_report.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_report)
        print(f"Report generated: {output_file}")

# استعمال کا طریقہ (Example Usage)
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_frameworks.py <input_markdown_file>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    analyzer = UniversalCSSAnalyzer()
    analyzer.run_analysis(input_file_path)
```

## 4. `npm_zero_dependency_frameworks.md` فائل کی مثال

آپ کی `npm_zero_dependency_frameworks.md` فائل میں درج ذیل فارمیٹ میں ڈیٹا ہونا چاہیے (ہر فریم ورک ایک نئی لائن پر JSON آبجیکٹ کی صورت میں):

```json
{"name": "Tailwind CSS", "source_code": "@tailwind base; @apply bg-red-500; group-hover:opacity-100; h-[10px]; dark:bg-gray-800; peer-focus:border-blue-500; space-x-4; divide-y; ring-2; bg-blue-500/50; -mt-4; text-[clamp(1rem,2vw,2rem)]; @container; ps-4;"}
{"name": "Bootstrap", "source_code": "@mixin media-breakpoint-up($name, $breakpoints: $grid-breakpoints) { ... } @extend .base; .text-primary { color: var(--bs-primary); }"}
{"name": "Bulma", "source_code": "@import \"~bulma/sass/utilities/_all.sass\"; @include mobile { ... } .is-flex-touch { display: flex; }"}
{"name": "Custom Framework X", "source_code": "@custom-directive; custom-modifier:value; [custom-arbitrary-value];"}
```

اس سکرپٹ کو استعمال کرتے ہوئے، جولز آپ کے تمام سی ایس ایس فریم ورکس کا باریک بینی سے تجزیہ کر کے ایک جامع رپورٹ تیار کر دے گا۔
