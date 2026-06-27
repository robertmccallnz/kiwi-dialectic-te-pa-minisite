#!/usr/bin/env python3
"""Te Pā weekly asset link-rot audit.

Crawls index.html and rhizome-mapper.html for every image / PDF / SVG / favicon
reference (relative + absolute including R2 CDN). HEAD-checks each URL against
https://te-pa.org/ and writes a broken-asset report.

Usage:
    python3 scripts/asset-audit.py [--base https://te-pa.org/] [--out audit.md]

Exit code 0 if 0 broken, 1 otherwise (suitable for CI / cron alerting).
"""
import argparse, json, re, sys, urllib.request, urllib.error
import concurrent.futures
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES = ['index.html', 'rhizome-mapper.html']
URL_PATTERNS = [
    re.compile(r'''(?:src|href)\s*=\s*["']([^"']+)["']''', re.IGNORECASE),
    re.compile(r'''url\(\s*["']?([^"'\)]+)["']?\s*\)''', re.IGNORECASE),
]
ASSET_EXT = re.compile(r'\.(png|jpe?g|webp|gif|svg|pdf|ico)(?:[?#]|$)', re.IGNORECASE)
SKIP_HOSTS = ('twitter.com', 'x.com', 'facebook.com', 'linkedin.com',
              'wa.me', 'mailto:', 'tel:', 'javascript:', 'data:', '#')


def extract(html_path):
    text = html_path.read_text(encoding='utf-8', errors='replace')
    found = {}  # url -> first line number
    for i, line in enumerate(text.splitlines(), 1):
        for pat in URL_PATTERNS:
            for m in pat.finditer(line):
                u = m.group(1).strip()
                if not u or u.startswith(SKIP_HOSTS): continue
                if '${' in u or '{{' in u: continue
                if not ASSET_EXT.search(u): continue
                # Skip Twitter/X share URLs containing image url= params
                if 'twitter.com' in u or 'x.com/intent' in u: continue
                if u not in found:
                    found[u] = i
    return found


def normalize(url, base):
    if url.startswith('http'):
        return url
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return base.rstrip('/') + url
    return base + url


def head(url, timeout=15):
    try:
        req = urllib.request.Request(
            url, method='HEAD',
            headers={'User-Agent': 'TePaAuditBot/1.0 (+https://te-pa.org)'}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        # Some CDNs reject HEAD — retry with GET range
        try:
            req = urllib.request.Request(
                url, method='GET',
                headers={'User-Agent': 'TePaAuditBot/1.0',
                         'Range': 'bytes=0-0'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:
            return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='https://te-pa.org/',
                    help='Live site base URL (default: https://te-pa.org/)')
    ap.add_argument('--out', default='/tmp/te-pa-audit.md',
                    help='Markdown report output path')
    ap.add_argument('--json', default='/tmp/te-pa-audit.json',
                    help='JSON report output path')
    args = ap.parse_args()

    assets = []
    for src in SOURCES:
        p = REPO_ROOT / src
        if not p.exists():
            print(f'WARN: {p} not found', file=sys.stderr)
            continue
        for url, line in extract(p).items():
            assets.append({'source_file': src, 'line': line, 'raw_url': url,
                           'check_url': normalize(url, args.base)})

    print(f'[audit] checking {len(assets)} asset URLs against {args.base}…',
          file=sys.stderr)

    def check(a):
        a['status'] = head(a['check_url'])
        a['broken'] = a['status'] != 200
        return a

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        assets = list(ex.map(check, assets))

    broken = sorted([a for a in assets if a['broken']],
                    key=lambda a: (a['source_file'], a['line']))

    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%MZ')
    md = [f'# Te Pā weekly asset link-rot audit',
          f'',
          f'**Run:** {ts}  ',
          f'**Base URL:** {args.base}  ',
          f'**Total assets checked:** {len(assets)}  ',
          f'**Broken (non-200):** **{len(broken)}**  ',
          f'']
    if broken:
        md.append('| Source file | Line | URL | HTTP |')
        md.append('|---|---:|---|---:|')
        for b in broken:
            md.append(f"| `{b['source_file']}` | {b['line']} | "
                      f"`{b['raw_url']}` | {b['status']} |")
    else:
        md.append('✅ All asset URLs returned HTTP 200. Nothing broken.')

    Path(args.out).write_text('\n'.join(md), encoding='utf-8')
    Path(args.json).write_text(json.dumps(
        {'run_at': ts, 'base': args.base, 'total': len(assets),
         'broken_count': len(broken), 'broken': broken, 'all': assets},
        indent=2), encoding='utf-8')

    print(f'[audit] broken: {len(broken)} / {len(assets)}', file=sys.stderr)
    print(f'[audit] report: {args.out}', file=sys.stderr)
    sys.exit(1 if broken else 0)


if __name__ == '__main__':
    main()
