# utils.py
from bs4 import BeautifulSoup
import requests
import time
# import httpx
# import asyncio
from urllib.parse import urlparse, urljoin

def is_allowed_by_robots(url, user_agent='AccessibilityAnalysisTool'):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    robots_url = urljoin(base_url, '/robots.txt')

    try:
        response = requests.get(robots_url)
        if response.status_code == 200:
            robots_txt = response.text
            lines = robots_txt.split('\n')
            user_agent_directives = False
            for line in lines:
                line = line.strip()
                if line.lower().startswith(f"user-agent: {user_agent.lower()}") or line.lower().startswith("user-agent: *"):
                    user_agent_directives = True
                elif user_agent_directives and line.lower().startswith('user-agent:'):
                    user_agent_directives = False
                if user_agent_directives and line.lower().startswith('disallow:'):
                    disallow_path = line[len('disallow:'):].strip()
                    disallow_url = urljoin(base_url, disallow_path)
                    if parsed_url.path.startswith(disallow_path):
                        return False
        return True
    except requests.RequestException:
        return False

def fetch_html_content(html_url):
    html_url = str(html_url)
    if html_url.startswith(('http://', 'https://')):
        if not is_allowed_by_robots(html_url):
            return None
        headers = {'User-Agent': 'AccessibilityAnalysisTool/1.0'}
        try:
            response = requests.get(html_url, headers=headers)
            response.raise_for_status()
            time.sleep(1)  # Rate limiting: sleep for 1 second between requests
            return response.text
        except requests.RequestException:
            return None
    return html_url

def check_labels(html):
    from collections import Counter
    
    soup = BeautifulSoup(html, 'html.parser')
    fields = soup.find_all(['input', 'textarea', 'select'])
    report = []
    error_summary = Counter()

    for field in fields:
        field_id = field.get('id')
        label = None
        if field_id:
            label = soup.find('label', {'for': field_id})
        if not label:
            label = field.find_parent('label')

        parent = field.find_parent()
        has_aria_label = field.get('aria-label')
        surrounding_text = parent.get_text(strip=True) if parent else ''

        suggestions = []
        if not label and not has_aria_label:
            suggestions.append('Add a label element associated with this field or an aria-label attribute.')
            error_summary['missing_label_or_aria'] += 1

        if surrounding_text and not has_aria_label:
            suggestions.append('Consider providing additional context with aria-label or aria-describedby.')
            error_summary['missing_contextual_aria'] += 1

        if field.get('placeholder'):
            suggestions.append('Do not use placeholder as a substitute for labels.')
            error_summary['placeholder_as_label'] += 1

        if field.get('required'):
            suggestions.append('Ensure the required field is clearly indicated.')
            error_summary['required_field_indication'] += 1

        fieldset = field.find_parent('fieldset')
        if fieldset and not fieldset.find('legend'):
            suggestions.append('Add a legend element to the fieldset to describe the group of related fields.')
            error_summary['missing_legend'] += 1

        form = field.find_parent('form')
        if form and not form.find('p'):
            suggestions.append('Provide clear instructions and guidance for filling out the form.')
            error_summary['missing_instructions'] += 1

        if field.get('aria-invalid'):
            suggestions.append('Ensure the form has proper error handling and messages.')
            error_summary['aria_invalid_error_handling'] += 1

        if not field.get('autocomplete'):
            suggestions.append('Add an appropriate autocomplete attribute to this field.')
            error_summary['missing_autocomplete'] += 1

        report.append({
            'field': str(field),
            'hasLabel': bool(label) or bool(has_aria_label),
            'suggestions': suggestions,
            'context': surrounding_text
        })

    return report, error_summary
