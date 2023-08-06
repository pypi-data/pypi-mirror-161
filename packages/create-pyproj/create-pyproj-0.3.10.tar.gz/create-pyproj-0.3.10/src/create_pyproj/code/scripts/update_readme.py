from pathlib import Path

DIR = Path(__file__).parent
ROOT = DIR.parent


def replaceTextBetween(text: str, delimA: str, delimB: str, replacement: str) -> str:
    leadingText = text.split(delimA)[0]
    trailingText = text.split(delimB)[1]

    return leadingText + delimA + replacement + delimB + trailingText


def getbadges(badges: str = '\n***** Badges *******'):
    with open(ROOT / 'README.md', 'r') as f:
        readme = f.read()

    badge_start = '\n<!-- Badges -->'
    badge_end = '\n<!-- End Badges -->'
    newreadme = replaceTextBetween(readme, badge_start, badge_end, badges)

    with open(ROOT / 'README.md', 'w') as f:
        readme = f.write(newreadme)
