# Git & GitHub

An English workshop for people new to version control, by Tianyou Yu.

[Open the course](https://sky-right.github.io/git-github-tutorial/)

The 45 slides follow `my-first-project`, with a README, an HTML file, and a stylesheet. Commands sit beside diagrams of the files, commits, branches, and remote references before and after each operation. Real VS Code excerpts connect the commands with staging, committing, history, branch selection, merging, and conflict resolution. Speaker notes include the teaching details and official references.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./build-git.sh
python3 -m http.server 8000 --directory dist/site
```

Open http://localhost:8000/ or open `dist/git-en.html` directly. The HTML includes its fonts, Logo, diagrams, styles, and Remark.js runtime, so playback also works offline.

Use the arrow keys to navigate, **P** for speaker notes, and **?** for help. Printing produces one page per teaching slide, including the completed answer reveal.

## Edit the course

- `content/git-en.md`: slides and speaker notes.
- `theme/git-course.css`: the original workshop typography and layout, with small course-specific adjustments.
- `engine/git_diagrams.py`: SVG drawing source. The build regenerates `images/git-course/`.
- `examples/my-first-project/`: the starter files used throughout the lesson.
- `images/vscode/`: real, cropped VS Code screenshots and capture provenance.
- `theme/git.html`: Remark configuration and HTML template.

Run `./build-git.sh` after editing. Change the source files rather than the generated HTML or SVG files.

## Deploy

Push to `main`. [The Pages workflow](.github/workflows/pages.yml) installs the Python dependencies, checks the course, builds it, and publishes only `dist/site/` to GitHub Pages. The site root opens the course directly. `git-en.html` is also available at the same site.

```bash
git add content/git-en.md theme/git-course.css engine/git_diagrams.py
git commit -m "Clarify the branching example"
git push origin main
```

Review the Actions run after pushing. A failed build leaves the previous published version available. The workflow can also be started manually from GitHub Actions.

## Checks

```bash
python3 -m unittest discover -s engine -p 'test_*.py'
python3 engine/verify_git_examples.py
```

The second command extracts the lesson's Git commands and runs them against temporary local repositories. It checks file contents, staging, HEAD, branch tips, merge parents, and remote operations without writing to GitHub.

The VS Code examples use built-in Git tools. [Capture notes](images/vscode/README.md) identify the version, localized interface, tested actions, and differences between similar operations such as Push and Sync. The teaching repository and its local bare remotes are excluded from publication.

For browser screenshots, install Playwright separately and provide Chrome or Chromium:

```bash
PLAYWRIGHT_MODULE=/path/to/node_modules/playwright \
CHROME_BIN=/path/to/chrome \
node engine/qa_git.cjs
```

The browser check writes screenshots, a contact index, a printable PDF, and a JSON report to `dist/git-en-preview/`. These generated checks are not deployed.

## Credits

The original workshop layout follows the container.training style. See [the notice](LICENSES/NOTICE.md). Remark.js is bundled under its [MIT license](theme/vendor/remark-LICENSE). Droid Serif and Inconsolata retain their [original licenses](theme/fonts/README.md). The Student Network Center Logo is the original course asset.

[Maintenance notes](docs/maintenance.md) describe the continuous example and the publication scope.
