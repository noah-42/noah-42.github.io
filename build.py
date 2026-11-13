#!/usr/bin/env python3
"""Build both CV pages (human + ATS) from the single source of truth: cv_data.json.

Usage: python3 build.py
Writes index.html (human version) and ats/index.html (ATS version).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent
data = json.load(open(ROOT / 'cv_data.json'))


def plain(text: str) -> str:
    """HTML entities -> plain text (for the ATS page)."""
    return (text.replace('&amp;', '&')
                .replace('&ndash;', '-')
                .replace('&atilde;', 'a')
                .replace('S&atilde;o Paulo', 'Sao Paulo'))


def esc_split(location: str) -> tuple[str, str]:
    """Split 'City (dates)' into (city, dates)."""
    location = location.strip()
    if location.endswith(')') and ' (' in location:
        city, dates = location.rsplit(' (', 1)
        return city, dates.rstrip(')')
    return location, ''


def link_or_text(text: str, url: str | None, human: bool) -> str:
    """Human page links companies; ATS page keeps plain text (entities unescaped
    there since the human page carries them)."""
    if human:
        return f'<a class="plain-link" href="{url}" target="_blank" rel="noopener">{text}</a>' if url else text
    return text


# ---------------- HUMAN PAGE ----------------

def human_summary_text(text: str) -> str:
    """Link 42 Berlin in the human-readable opening Summary sentence only."""
    prefix = 'Software engineering student at 42 Berlin who, on the side, is actively building with AI'
    if text.startswith(prefix):
        return text.replace(
            '42 Berlin',
            '<a class="plain-link summary-link" href="https://www.42berlin.de" target="_blank" rel="noopener">42 Berlin</a>',
            1,
        )
    return text


HUMAN_LINKS = {
    'AOL': 'https://aol.com',
    'AstraZeneca': 'https://www.astrazeneca.com/',
    'Blockbuster': 'https://www.blockbuster.com/',
    'Discover Card': 'https://www.discover.com',
    'Electronic Arts': 'https://www.ea.com',
    'eBay': 'https://www.ebay.com',
    'GlaxoSmithKline': 'https://gsk.com',
    'Merck': 'https://www.merckgroup.com/',
    'Netflix': 'https://www.netflix.com',
    'Novartis': 'https://novartis.com',
    'O Negative': 'https://www.linkedin.com/company/o-negative-media-llc',
    'Oracle': 'https://www.oracle.com',
    'Pfizer': 'https://pfizer.com',
    'Sanofi': 'https://sanofi.com',
    'Starbucks': 'https://starbucks.com',
    'Universal Music': 'https://universalmusic.com',
    'Verizon Wireless': 'https://www.verizon.com/',
    'Warner Music': 'https://www.wmg.com',
}

HUMAN_SKILL_LINKS = {
    'Claude Code': 'https://claude.com/product/claude-code',
    'Codex': 'https://chatgpt.com/codex',
    'Cursor': 'https://cursor.com',
    'Google Workspace': 'https://workspace.google.com/',
    'Jira': 'https://www.atlassian.com/software/jira',
    'Microsoft Office': 'https://www.microsoft.com/en/microsoft-365/microsoft-office',
    'Miro': 'https://miro.com/',
    'Slack': 'https://slack.com/',
    'Trello': 'https://trello.com/',
    'UV': 'https://docs.astral.sh/uv/',
    'VS Code': 'https://code.visualstudio.com/',
    'Vim': 'https://www.vim.org/',
    'Zed': 'https://zed.dev/',
    'Grok Bot': 'https://x.ai/bot',
    'Instinct': 'https://www.instinct.com',
    'OmO': 'https://omo.dev/',
    'OpenCode': 'https://opencode.ai/',
    'Pi': 'https://pi.dev/',
    'Python': 'https://www.python.org/',
    'C': 'https://www.c-language.org/',
    'git': 'https://git-scm.com/',
}


def human_bullet_text(text: str) -> str:
    """Link named companies in the human-readable page only."""
    text = text.replace(
        'Inc. Magazine',
        '<a class="plain-link" href="https://www.inc.com" target="_blank" rel="noopener">Inc. Magazine</a>',
        1,
    ).replace(
        '11th fastest growing private company in the USA',
        '<a class="plain-link" href="https://www.forbes.com/sites/mnewlands/2015/11/11/this-ceo-bootstrapped-his-mobile-ad-company-to-400-billion-impressions-a-month-heres-how/" target="_blank" rel="noopener">11th fastest growing private company in the USA</a>',
        1,
    )
    for name in sorted(HUMAN_LINKS, key=len, reverse=True):
        url = HUMAN_LINKS[name]
        text = text.replace(
            name,
            f'<a class="plain-link" href="{url}" target="_blank" rel="noopener">{name}</a>',
            1,
        )
    return text

summary = '\n'.join(f'          <li>{human_summary_text(b)}</li>' for b in data['summary'])

visible_projects = [p for p in data['projects'] if not p.get('hidden', False)]

projects = []
for p in visible_projects:
    name = link_or_text(p['name'], p.get('url'), True)
    desc = p['desc']
    for word, url in (p.get('desc_links') or {}).items():
        desc = desc.replace(
            word,
            f'<a class="plain-link" href="{url}" target="_blank" rel="noopener">{word}</a>',
            1,
        )
    projects.append(f'          <li><span class="project-name">{name}</span>\n'
                    f'            <span class="project-desc">{desc}</span>\n'
                    f'          </li>')
projects_html = '\n'.join(projects)

experience = []
for e in data['experience']:
    parts = e['heading_parts']
    if len(parts) >= 2:
        title = parts[0]['text']
        company = ', '.join(link_or_text(p['text'], p.get('url'), True) for p in parts[1:])
        heading = f'{title}, {company}'
    else:
        heading = parts[0]['text']
    city, dates = esc_split(e['location'])
    loc = f'{city} ({dates})' if dates else city
    bullets = ''
    if e['bullets']:
        items = '\n'.join(f'          <li>{human_bullet_text(b)}</li>' for b in e['bullets'])
        bullets = f'        <ul>\n{items}\n        </ul>\n'
    experience.append(f'        <h3>{heading}</h3>\n'
                      f'        <p class="location">{loc}</p>\n'
                      f'{bullets}')
experience_html = '\n'.join(experience)

education = []
for e in data['education']:
    heading = ', '.join(link_or_text(p['text'], p.get('url'), True) for p in e['heading_parts'])
    city, dates = esc_split(e['location'])
    loc = f'{city} ({dates})' if dates else city
    education.append(f'        <h3>{heading}</h3>\n'
                     f'        <p class="location">{loc}</p>')
education_html = '\n'.join(education)

HUMAN_SKILL_LINKS_PARTIAL = {
    'Linux': 'https://www.linux.org/',
}


def human_skill_item(item: str) -> str:
    url = HUMAN_SKILL_LINKS.get(item)
    if url:
        return f'<a class="plain-link" href="{url}" target="_blank" rel="noopener">{item}</a>'
    for key, partial_url in HUMAN_SKILL_LINKS_PARTIAL.items():
        if key in item:
            return item.replace(
                key,
                f'<a class="plain-link" href="{partial_url}" target="_blank" rel="noopener">{key}</a>',
                1,
            )
    return item


skills = []
for s_ in data['skills']:
    items = ', '.join(human_skill_item(i) for i in s_['items'])
    skills.append(f'          <li><span class="skill-name">{s_["label"]}</span>\n'
                  f'            <span class="skill-desc">{items}</span>\n'
                  f'          </li>')
skills_html = '\n'.join(skills)

contact_urls = {
    'linkedin.com/in/noahrobinson': 'https://linkedin.com/in/noahrobinson',
    'github.com/noah-42': 'https://github.com/noah-42',
    'noah42.com': 'https://noah42.com',
}
contact_lines = '\n'.join(
    f'          <li>{label}: <a href="{contact_urls[url]}">{url}</a></li>'
    for line in data['contact']['lines']
    for label, url in [line.split(': ', 1)]
)

human = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Noah Robinson</title>

    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="personal website" />
    <meta name="author" content="Noah Robinson" />
    <link rel="icon" type="image/png" href="./assets/favicon.png" />
    <link rel="stylesheet" href="./css/style.css" />
  </head>
  <body>
    <div class="wrapper">
      <div class="navbar container">
        <a id="author-name" class="pull-left" href="./">Noah Robinson</a>
        <ul id="navlist" class="pull-right navbar-ul">
          <li class="pull-left nav-list"><a href="https://noah42.com">noah42.com</a> /</li>
          <li class="pull-left nav-list">
            <a target="_blank" rel="noopener" href="https://linkedin.com/in/noahrobinson">LinkedIn</a> /
          </li>
          <li class="pull-left nav-list">
            <a target="_blank" rel="noopener" href="https://github.com/noah-42">GitHub</a>
          </li>
        </ul>
      </div>
      <div class="ats-note"><a href="./ats/">ATS-friendly version</a></div>
      <hr />

      <div class="container content">
        <h2 id="summary">Summary</h2>

        <ul>
{summary}
        </ul>

        <h2 id="projects">Coding Projects (Beta)</h2>

        <ul class="projects-table">
{projects_html}
        </ul>

        <h2 id="experience">Experience</h2>

{experience_html}
        <h2 id="education">Education</h2>

{education_html}
        <h2 id="skills-tools">Skills &amp; Tools</h2>

        <ul class="skills-table">
{skills_html}
        </ul>

        <h2 id="languages">Languages</h2>

        <p>{data['languages']}</p>

        <h2 id="contact">Contact</h2>

        <ul>
{contact_lines}
        </ul>

        <div class="bottom-space"></div>
      </div>
    </div>
  </body>
</html>
'''

(ROOT / 'index.html').write_text(human)

# ---------------- ATS PAGE ----------------

ats_summary = '\n'.join(f'      <li>{plain(b)}</li>' for b in data['summary'])

ats_projects = '\n'.join(f'      <li>{plain(p["name"])}: {plain(p["desc"])}</li>'
                         for p in visible_projects)

ats_experience = []
for e in data['experience']:
    heading = ', '.join(plain(p['text']) for p in e['heading_parts'])
    city, dates = esc_split(e['location'])
    heading_full = f'{heading} | {plain(dates)}' if dates else heading
    loc = f'    <p class="location">{plain(city)}</p>\n' if city else ''
    bullets = ''
    if e['bullets']:
        items = '\n'.join(f'      <li>{plain(b)}</li>' for b in e['bullets'])
        bullets = f'    <ul>\n{items}\n    </ul>\n'
    ats_experience.append(f'    <h3>{heading_full}</h3>\n{loc}{bullets}')
ats_experience_html = '\n'.join(ats_experience)

ats_education = []
for e in data['education']:
    heading = ', '.join(plain(p['text']) for p in e['heading_parts'])
    city, dates = esc_split(e['location'])
    loc = f'    <p class="location">{plain(city)}</p>\n' if city else ''
    ats_education.append(f'    <h3>{heading}</h3>\n{loc}')
ats_education_html = '\n'.join(ats_education)

ats_skills = '\n'.join(f'      <li>{plain(s_["label"])}: {plain(", ".join(s_["items"]))}</li>'
                       for s_ in data['skills'])

ats = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Noah Robinson - ATS CV</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="ATS-friendly CV for Noah Robinson" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Inconsolata:400,700&display=swap">
    <style>
      body {{ font-family: "Inconsolata", "Courier New", monospace; font-size: 12pt; color: #24292f; max-width: 100%; margin: 24px auto; padding: 0 16px; line-height: 1.5; background: #fff; }}
      h1 {{ font-size: 20pt; margin-bottom: 4px; color: #0A66C2; }}
      h2 {{ font-size: 15pt; color: #444746; border-bottom: 1px solid #444746; margin-top: 20px; margin-bottom: 8px; }}
      h3 {{ font-size: 12pt; margin: 12px 0 2px; color: #0A66C2; }}
      p.location {{ font-style: italic; color: #3d3d3d; margin: 0 0 4px; }}
      ul {{ margin: 4px 0 10px 22px; padding: 0; }}
      li {{ margin-bottom: 2px; color: #24292f; }}
      a {{ color: #0A66C2; }}
      .contact {{ margin-bottom: 8px; }}
    </style>
  </head>
  <body>
    <h1>Noah Robinson</h1>
    <p class="contact">Berlin | linkedin.com/in/noahrobinson | github.com/noah-42 | noah42.com | <a href="../">formatted version</a></p>

    <h2>Summary</h2>
    <ul>
{ats_summary}
    </ul>

    <h2>AI Projects (Beta)</h2>
    <ul>
{ats_projects}
    </ul>

    <h2>Experience</h2>
{ats_experience_html}

    <h2>Education</h2>
{ats_education_html}

    <h2>Skills &amp; Tools</h2>
    <ul>
{ats_skills}
    </ul>

    <h2>Languages</h2>
    <p>{plain(data['languages'])}</p>

    <h2>Contact</h2>
    <ul>
      <li>LinkedIn: linkedin.com/in/noahrobinson</li>
      <li>GitHub: github.com/noah-42</li>
      <li>Web: noah42.com</li>
    </ul>
  </body>
</html>
'''

(ROOT / 'ats' / 'index.html').write_text(ats)
print('built index.html and ats/index.html from cv_data.json')
