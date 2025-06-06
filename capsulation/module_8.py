import re

class RegexTool:
    def find_emails(self, text):
        return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

    def replace_text(self, text, pattern, replacement):
        return re.sub(pattern, replacement, text)
