# Maintenance notes

The course keeps Remark.js and the existing Markdown-to-HTML build. The visual refinements restore the original white background, Droid Serif headings and text, Inconsolata commands, pale gray code blocks, top-right page numbers, and the original Student Network Center Logo at the bottom right. The cover has only a title, a Git diagram, the author, and the date. The closing slide has the author and a short thank-you.

Repeated chapter labels, subtitle wrappers, takeaways, dark panels, and decorative footers were removed. The diagrams retain the recent node and line style, with concrete file states and explicit references.

## The continuous example

All steps use `examples/my-first-project/` as their starting files.

| Commit | Change | Branch result |
| --- | --- | --- |
| A | Add README.md, index.html and style.css | main points to A |
| B | Change the homepage heading | main points to B |
| C | Change CSS text color to navy | add-style points to C; main stays at B |
| C | Fast-forward merge | main advances to C; no extra commit |
| D | Add a footer to index.html | add-footer advances from C to D |
| E | Add the README description | main advances from C to E |
| M | Merge add-footer | main points to M, whose parents are E and D |
| N | A teammate updates README.md | GitHub main advances to N; fetch and pull are demonstrated separately |
| P | Add README run instructions | improve-readme advances from N to P |
| Q | Merge the pull request on GitHub | Q has parents N and P; pulling updates local main to Q |

The staging quiz, conflict example, and undo commands are explicitly separate demonstrations. They do not silently alter the running project's state. A and B are labels for real commits, not literal hashes. Remote diagrams abbreviate earlier history with an ellipsis.

The command check in `engine/verify_git_examples.py` reads the actual Bash blocks from the Markdown. Editor changes are applied between those commands, then assertions compare the resulting Git state with the lesson. It uses a local bare repository in place of GitHub, including a forced merge commit to reproduce the specified GitHub PR merge method.

## VS Code alongside the commands

The third refinement keeps the cover, closing slide, fonts, Logo, and existing
state diagrams. Eleven real screenshot excerpts show the corresponding built-in
controls. Most fit inside the command column; three additional teaching slides
cover the real diff, an unstage-and-restage detour, and the Merge Editor. The
course now has 45 teaching slides and 46 playback states.

The unstage detour starts after staging v2 and returns to staged v2 before B.
Its diagram shows the unstage operation; the final add restores the earlier state.
The conflict example stays explicitly separate from the main footer merge.

Source Control lists are observations, not state-changing commands. Create
Branch also switches and belongs with `switch -c`, not the create-only `branch`.
The merge picker merges the selected source into the current branch. Publish
Branch is shown only after origin has been configured, and differs from Publish
to GitHub. Push is separate from Sync (pull then push). GUI Pull uses Git's pull
configuration; use local `pull.ff=only` to match the course's CLI policy.
Complete Merge resolves the file; Continue commits the pending merge.

See `images/vscode/README.md` and `captures.json` for capture provenance and state
checks. The real local interface is VS Code 1.137.0, Dark Modern, Chinese UI;
English labels are added as slide text rather than painted over native labels.
All capture actions use an empty temporary profile and a dedicated, ignored
`.vscode-demo/` repository with local bare remotes. Do not publish this directory,
temporary profiles, or uncropped desktop captures. The crop helper uses Pillow,
already supplied by the project's python-pptx dependency; it is not part of the
normal build and adds no dependency.

## Build and publication

`build-git.sh` regenerates SVG diagrams and calls the existing Python builder with `--html-only --standalone`. It writes:

- `dist/git-en.html`: portable local course.
- `dist/site/index.html`: the Pages homepage.
- `dist/site/git-en.html`: a direct course URL.

Only `dist/site/` is uploaded by Actions. The public Git repository includes the course Markdown, drawing source, styles, runtime, fonts and licenses, the original Logo, starter files, tests, and the Pages workflow.

The local workspace also contains older decks, backup archives, a Python environment, and an independent `pages/` checkout. A source allowlist in `.gitignore` keeps them out of this repository. Do not replace it with a broad ignore list or blindly add other local files. The older `Sky-Right/git-slides` repository and its Pages site are separate and are not modified by this course's workflow.

## Verification

The local browser check renders all 46 playback states, checks each slide and each SVG label, verifies the Logo and fonts, exercises keyboard navigation and the answer reveal, and tests three desktop viewport sizes. The print output contains 45 pages. Local Git checks cover 14 groups of states and the builder has 5 regression tests.

The new public Pages URL is checked in a browser after deployment. No real learner repository or pull request is created by the command tests. The old PPTX renderer remains available locally, but this course's layout and diagrams are delivered as HTML and browser print output.
