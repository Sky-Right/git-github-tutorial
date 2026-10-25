#!/usr/bin/env python3
"""Execute the course's Git commands in disposable repositories; never contact GitHub."""
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
           GIT_TERMINAL_PROMPT='0', GIT_AUTHOR_NAME='Workshop Test',
           GIT_AUTHOR_EMAIL='test@example.invalid', GIT_COMMITTER_NAME='Workshop Test',
           GIT_COMMITTER_EMAIL='test@example.invalid')
for key in ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_CONFIG_COUNT']:
    ENV.pop(key, None)


def git(repo, *args, ok=True):
    result = subprocess.run(['git', '-C', str(repo), *args], env=ENV, text=True, capture_output=True)
    if ok and result.returncode:
        raise AssertionError(f'git {args}: {result.stderr}')
    return result.stdout.strip() if ok else result


def commands():
    result = {}
    for slide in re.split(r'\n---\s*\n', (ROOT / 'content/git-en.md').read_text()):
        name = re.search(r'^name: (.+)$', slide, re.M)
        if not name:
            continue
        visible = slide.split('???')[0]
        blocks = re.findall(r'```bash\n(.*?)\n```', visible, re.S)
        lines = '\n'.join(blocks).replace('\\\n', '').splitlines()
        result[name[1]] = [shlex.split(line)[1:] for line in lines if line.startswith('git ')]
    return result


COMMANDS = commands()


def run(repo, name, remote=None, part=slice(None)):
    for args in COMMANDS[name][part]:
        args = [str(remote) if value == '<repo-url>' else value for value in args]
        git(repo, *args)


def save(repo, file, text, message):
    (repo / file).write_text(text)
    git(repo, 'add', file)
    git(repo, 'commit', '-m', message)
    return git(repo, 'rev-parse', 'HEAD')


def verify():
    checks = []
    with tempfile.TemporaryDirectory(prefix='git-workshop-') as tmp:
        root = Path(tmp)
        local = root / 'my-first-project'
        shutil.copytree(ROOT / 'examples/my-first-project', local)
        run(local, 'init')
        assert (local / '.git').is_dir()
        assert git(local, 'status', '--porcelain').count('??') == 3
        checks.append('init creates .git and leaves all three files untracked')
        run(local, 'initial-stage')
        assert git(local, 'diff', '--cached', '--name-only').splitlines() == ['README.md', 'index.html', 'style.css']
        run(local, 'initial-commit')
        a = git(local, 'rev-parse', 'HEAD')
        assert len(git(local, 'ls-tree', '--name-only', 'HEAD').splitlines()) == 3
        checks.append('add . stages three files; A records all three')
        (local / 'index.html').write_text('<h1>My homepage</h1>\n')
        assert git(local, 'status', '--porcelain').splitlines()[0] == 'M index.html'
        assert git(local, 'diff', '--cached') == ''
        run(local, 'inspect')
        run(local, 'add')
        assert git(local, 'show', ':index.html') == '<h1>My homepage</h1>'
        assert git(local, 'rev-parse', 'HEAD') == a
        run(local, 'unstage', part=slice(0, 1))
        assert git(local, 'show', ':index.html') == '<h1>Hello</h1>'
        assert (local / 'index.html').read_text() == '<h1>My homepage</h1>\n'
        assert git(local, 'rev-parse', 'HEAD') == a
        run(local, 'unstage', part=slice(1, None))
        assert git(local, 'show', ':index.html') == '<h1>My homepage</h1>'
        checks.append('unstage restores index from A, preserves working v2 and HEAD, then add restores staged v2')
        run(local, 'commit')
        b = git(local, 'rev-parse', 'HEAD')
        assert len(git(local, 'ls-tree', '--name-only', 'HEAD').splitlines()) == 3
        assert git(local, 'log', '--format=%s').splitlines() == ['Add homepage', 'Add project files']
        checks.append('edit changes only working files; add updates staging; B keeps unchanged files')
        run(local, 'branch')
        assert git(local, 'symbolic-ref', '--short', 'HEAD') == 'main'
        assert git(local, 'rev-parse', 'add-style') == b
        run(local, 'switch')
        assert git(local, 'symbolic-ref', '--short', 'HEAD') == 'add-style'
        assert git(local, 'rev-parse', 'HEAD') == b
        checks.append('branch adds a name without switching; switch changes HEAD without moving tips')
        (local / 'style.css').write_text('body { color: navy; }\n')
        run(local, 'branch-commit')
        c = git(local, 'rev-parse', 'HEAD')
        assert git(local, 'rev-parse', 'main') == b
        run(local, 'switch-main')
        assert (local / 'style.css').read_text() == 'body { color: #222; }\n'
        assert git(local, 'rev-parse', 'add-style') == c
        run(local, 'fast-forward')
        assert git(local, 'rev-parse', 'main') == c
        assert len(git(local, 'rev-list', '--parents', '-n', '1', 'HEAD').split()) == 2
        assert (local / 'style.css').read_text() == 'body { color: navy; }\n'
        checks.append('C advances only add-style; switch restores #222; merge fast-forwards main to C')
        run(local, 'footer-branch', part=slice(0, 1))
        (local / 'index.html').write_text('<h1>My homepage</h1>\n<footer>Made with Git.</footer>\n')
        run(local, 'footer-branch', part=slice(1, None))
        d = git(local, 'rev-parse', 'HEAD')
        run(local, 'main-change', part=slice(0, 1))
        (local / 'README.md').write_text('# My first project\n\nA small website for learning Git.\n')
        run(local, 'main-change', part=slice(1, None))
        e = git(local, 'rev-parse', 'HEAD')
        run(local, 'merge')
        m = git(local, 'rev-parse', 'HEAD')
        assert git(local, 'rev-list', '--parents', '-n', '1', 'HEAD').split()[1:] == [e, d]
        assert 'Made with Git.' in (local / 'index.html').read_text()
        assert 'A small website' in (local / 'README.md').read_text()
        checks.append('D and E diverge after C; M has parents E and D and contains both edits')
        remote = root / 'my-first-project.git'
        git(root, 'init', '--bare', '-b', 'main', str(remote))
        run(local, 'local-remote', remote)
        assert git(local, 'remote', 'get-url', 'origin') == str(remote)
        assert git(remote, 'show-ref', ok=False).returncode != 0
        run(local, 'push')
        assert git(remote, 'rev-parse', 'main') == m
        assert git(remote, 'for-each-ref', '--format=%(refname)', 'refs/heads') == 'refs/heads/main'
        checks.append('adding origin uploads nothing; push shares main and reachable history through M')
        second = root / 'second-computer'
        second.mkdir()
        run(second, 'clone', remote)
        teammate = second / 'my-first-project'
        assert git(teammate, 'rev-parse', 'main') == m
        assert len(git(teammate, 'ls-tree', '--name-only', 'HEAD').splitlines()) == 3
        n = save(teammate, 'README.md', (teammate / 'README.md').read_text() + '\n## About\nA Git exercise.\n', 'Add About paragraph')
        git(teammate, 'push')
        before = (local / 'README.md').read_text()
        run(local, 'fetch')
        assert git(local, 'rev-parse', 'main') == m
        assert git(local, 'rev-parse', 'origin/main') == n
        assert (local / 'README.md').read_text() == before
        run(local, 'pull')
        assert git(local, 'rev-parse', 'main') == n
        assert '## About' in (local / 'README.md').read_text()
        checks.append('clone checks out M; fetch reads teammate N without changing files; pull updates main and README to N')
        run(local, 'pr-start', part=slice(0, 1))
        (local / 'README.md').write_text((local / 'README.md').read_text() + '\n## Run\nOpen index.html in a browser.\n')
        run(local, 'pr-start', part=slice(1, None))
        p = git(local, 'rev-parse', 'HEAD')
        run(local, 'pr-push')
        assert git(remote, 'rev-parse', 'main') == n
        assert git(remote, 'rev-parse', 'improve-readme') == p
        checks.append('PR commit P advances the feature branch; pushing it leaves remote main at N')
        git(teammate, 'fetch', 'origin')
        git(teammate, 'merge', '--no-ff', 'origin/improve-readme', '-m', 'Merge pull request')
        q = git(teammate, 'rev-parse', 'HEAD')
        assert git(teammate, 'rev-list', '--parents', '-n', '1', 'HEAD').split()[1:] == [n, p]
        git(teammate, 'push')
        run(local, 'merge-and-sync')
        assert git(local, 'rev-parse', 'main') == q
        assert git(local, 'rev-parse', 'origin/main') == q
        assert git(local, 'rev-parse', 'improve-readme') == p
        assert '## Run' in (local / 'README.md').read_text()
        checks.append('the merge-commit method creates Q with parents N/P; sync advances local main to Q and keeps feature at P')
        save(local, 'README.md', (local / 'README.md').read_text() + '\nLocal edit\n', 'Local edit')
        save(teammate, 'README.md', (teammate / 'README.md').read_text() + '\nRemote edit\n', 'Remote edit')
        git(teammate, 'push')
        assert git(local, 'push', ok=False).returncode != 0
        assert git(local, 'pull', '--ff-only', ok=False).returncode != 0
        checks.append('divergent history rejects push and stops pull --ff-only')
        # Separate demonstrations do not leave the continuous exercise dirty.
        demo = root / 'separate-demo'
        demo.mkdir()
        git(demo, 'init', '-b', 'main')
        save(demo, 'index.html', '<h1>Hello</h1>\n', 'Base')
        (demo / 'index.html').write_text('v2\n')
        git(demo, 'add', 'index.html')
        (demo / 'index.html').write_text('v3\n')
        git(demo, 'commit', '-m', 'Save v2')
        assert git(demo, 'show', 'HEAD:index.html') == 'v2'
        git(demo, 'add', 'index.html')
        git(demo, 'restore', '--staged', 'index.html')
        assert (demo / 'index.html').read_text() == 'v3\n'
        git(demo, 'restore', 'index.html')
        assert (demo / 'index.html').read_text() == 'v2\n'
        checks.append('the staging quiz saves v2; unstage preserves v3; restore copies the staged v2')
        git(demo, 'switch', '-c', 'conflict-incoming')
        save(demo, 'index.html', '<h1>Your homepage</h1>\n', 'Incoming heading')
        git(demo, 'switch', 'main')
        save(demo, 'index.html', '<h1>Our homepage</h1>\n', 'Current heading')
        assert git(demo, 'merge', 'conflict-incoming', ok=False).returncode != 0
        conflict = (demo / 'index.html').read_text()
        assert '<<<<<<< HEAD' in conflict and '=======' in conflict and '>>>>>>> conflict-incoming' in conflict
        git(demo, 'merge', '--abort')
        assert git(demo, 'status', '--porcelain') == ''
        checks.append('the alternative conflict example produces the displayed markers and can be aborted')
    return checks


if __name__ == '__main__':
    checks = verify()
    print(json.dumps({'git': subprocess.check_output(['git', '--version'], text=True).strip(),
                      'passed': len(checks), 'checks': checks}, indent=2))
