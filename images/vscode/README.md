# VS Code screenshots

These are real local captures from Visual Studio Code **1.137.0** on macOS,
recorded on October 25, 2026. The interface uses **Dark Modern** and **Chinese
labels**. English action names in the slides identify the corresponding tools;
the native labels and colors have not been translated or replaced in the images.

The captures use an empty temporary profile and a dedicated `my-first-project`
repository with the three course files. Git support, Source Control Graph,
the diff editor, and Merge Editor are built-in features. No GitLens, Git Graph,
or GitHub Pull Requests extension supplies the pictured controls.

`captures.json` records each source image's hash, crop rectangle, and operation.
`engine/prepare_vscode_captures.py --raw <capture-directory>` reproduces the crops
and thin blue outlines. Full desktop captures remain local, outside the public
source tree. The conflict image combines input excerpts before choosing Current
and the result afterward, from two consecutive real Merge Editor views. This
omits blank editor space and an unchanged line while keeping the action visible.

The Commit excerpt was recaptured by replaying the verified pre-B file/index
state on a disposable local branch, so the pointer would not cover its message.
The published crop shows only the message field and Commit action.

## State checks during capture

| GUI action | Checked result |
| --- | --- |
| Initialize Repository | New `.git`; main is unborn; three files remain untracked. |
| Stage Changes | Index contains the new homepage; HEAD is still A. |
| Unstage Changes | Index matches A; the working homepage edit remains. |
| Commit | B has message `Add homepage`; working tree is clean. |
| Status Bar branch picker | HEAD changes to existing add-style; both tips stay at B. |
| Create Branch… | New add-footer and HEAD start at C. This also switches branches. |
| Git: Merge… | main fast-forwards B → C; no merge commit is added. |
| Complete Merge | Conflict entries are resolved; HEAD does not advance and MERGE_HEAD still exists. A separate commit must finish the merge. |
| Publish Branch | With origin configured, main is pushed and its upstream is origin/main. |
| Git: Push | Runs independently of Pull; the already-shared main remains unchanged. |
| Git: Fetch | origin/main advances M → N; main and working README stay at M. |
| Git: Pull | With local pull.ff=only, main advances M → N and the README updates. |
| Git: Clone | A new folder has `.git`, the three files, origin, and a tracking main at N. |

Remote actions were tested against local bare repositories and a second clone.
No account, token, or real learner repository was used. The course diagrams label
the hosting side GitHub; remote Git state works the same way for this exercise.

## Official references

- [Source control overview](https://code.visualstudio.com/docs/sourcecontrol/overview)
- [Staging and committing](https://code.visualstudio.com/docs/sourcecontrol/staging-commits)
- [History and the built-in Graph](https://code.visualstudio.com/docs/sourcecontrol/history)
- [Branches](https://code.visualstudio.com/docs/sourcecontrol/branches-worktrees)
- [Repositories and remotes](https://code.visualstudio.com/docs/sourcecontrol/repos-remotes)
- [Merge conflicts](https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts)

Visual Studio Code is a Microsoft product. These educational screenshots retain
the application's native interface and are not an endorsement by Microsoft.
