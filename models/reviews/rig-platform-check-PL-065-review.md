# Re-review: rig-platform-check without personal paths (PL-065 draft), MA-034

**For:** Platform (qitem-20261015054948-d5fe648e, 2026-10-15). The baseline is my MA-031 review
(`rig-platform-check-review.md`) and the installed PD-033 runner (sha256 `06740982…`).
**Verdict:** fit to put to the owner **at sha256 `6d44508c17f4ad63a9efbf3fb0a00c5f0d4c71c62bbc1f33edb4f7c97002af8c`**.
The owner's card must check against that hash, not the `33efa579…` in the request. Two low hardening points
follow; neither blocks.

## What I reviewed
- **The candidate kept changing during the review.** The request named `33efa579…`. At 05:53Z the setup copy was
  `eaaa838c…`, and by 05:57Z both copies were `6d44508c…`. I froze copies in my scratchpad and checked their
  hashes before probing, at the operator's request. Everything below is about **`6d44508c…`**.
- **Tests:** `test_check.py` is now `fb08dc2b…`, not the `fe343bae…` named in the request. I did **not** run it,
  because it writes and deletes log files in Platform's scratch. The "24/24 pass" was against `33efa579…`, so
  Platform should rerun the tests on `6d44508c…`/`fb08dc2b…` and record the result on the card.
- **Seen once, superseded:** the intermediate `eaaa838c…` counted every `REPO=` line, including the indented
  harness fallback on line 35 of the installed release command. It read an **empty REPO from the real installed
  file**, so every subcommand would have refused after install. `6d44508c…` counts only column-0 lines and reads the
  right path. This is not a finding against the final version. It's why the hash pin matters.

## Probe of how the frozen copy reads REPO
I loaded the frozen copy as a module (no subcommand runs) and called `_installed_repo` on the real installed release
command and on temp files, with `fstat` patched to report root ownership. Script: scratchpad `pl065_probe.py`.

| Input | REPO |
|---|---|
| The real `/usr/local/sbin/rig-console-release` | the repo path (correct) |
| `REPO="/srv/OpenRig"   # comment` | `/srv/OpenRig` |
| The installed shape: a filled line plus the indented `REPO="$(cd …)"` fallback | `/srv/OpenRig` |
| `REPO="@REPO@"` (not filled in), `$` in the value, `; rm …` after it, a relative path | empty (refuses) |
| `REPO="/srv/../etc"` | `/srv/../etc` (see L1) |
| A CRLF line ending | `/srv/x` (harmless) |

## The four questions
1. **Is the release command's REPO line a sound source?** Yes.
   - `/usr/local/sbin/rig-console-release`, `/usr/local/sbin` and `/usr/local` are all `root:root 755`
     (checked with stat on 10-15).
   - The file is opened with `O_NOFOLLOW`, and the open file is checked with `fstat` (regular file, uid 0, no group
     or other write). The parent folders are root-owned, so nothing can be swapped between the check and the read.
   - Only root, meaning the deploy, can change the path.
2. **NODE: does choosing the newest version change MA-031?** No. The old fixed path was in the same user-writable
   `~/.nvm` folder, so a seat that can add `v99.0.0/bin/node` could already overwrite the old binary. One practical
   change: an nvm upgrade now silently changes which node the page and dip checks use. That's fine, but say so in
   PL-065.
3. **Can the caller's environment or a seat-written file change what runs?**
   - **Environment:** no. The shebang is `python3 -I`, HOME comes from the user record, not `$HOME`, and the child's
     environment is fixed.
   - **Seat-written files:** the same as MA-031 and no wider. smoke.py, the `.mjs` checks, the release harness and
     node are still user-writable code (the S3 limit stated in the docstring). git config filters are still refused.
4. **Can REPO be non-empty but wrong?** Only through L1 below, and that needs root. Bad encoding gives an empty
   REPO. There's no time gap between check and read (see 1).

## Low points (hardening; not blocking)
- **L1. `..` is accepted in REPO.** `/srv/../etc` passes. Only root can write the source, so this is defence in
  depth. Fix: refuse unless `os.path.normpath(value) == value`.
- **L2. Running as root isn't refused.** Under `sudo`, HOME becomes `/root` and the smoke checks would run
  user-writable code as root. The PD-033 runner had the same gap, and I haven't checked whether any sudo rule
  allows this. Fix: `if os.geteuid() == 0: sys.exit(...)` at the top of `main`.

## Follow-up: final candidate `5c37960c…` (qitem-20261015062749-f1f822ec, 2026-10-15)
**Verdict: confirmed.** The owner's card should pin
`5c37960c8ca105baeb89dd35ba4da492def1aac6ffd83102175e63b24087e464`.

**What I checked:**
- **Inputs:** I copied both frozen inputs to my scratchpad and checked their hashes. The runner is `5c37960c…` and
  the tests `12a8213c…`, both matching the request.
- **Diff against my frozen `6d44508c…`:** exactly the three described changes, and nothing else.
  1. **The comment form** (recheck-11). The pattern now needs a space or tab before `#`.
  2. **L1:** the path must equal `os.path.normpath` of itself.
  3. **L2:** `main()` exits first thing when `geteuid() == 0`, before any check runs. Only read-only setup (the
     release file read and the nvm glob) runs before that point.
- **Probe on the frozen copy** (`pl065_probe.py`, 19 cases):
  - **Refused:** `"/x"#y`, `/srv/../etc`, `/srv/./x`, `/srv//x`, `/srv/x/`, `/`, the unfilled placeholder, `$`, a
    trailing `; …`, and a relative path.
  - **Accepted:** the plain form, a space- or tab-separated comment, trailing spaces, and the real installed file,
    which reads the correct repo path.
- **The root refusal:** Platform's test fakes `geteuid` to return 0 (`test_check` lines 154–162). I couldn't run it
  as root myself (no sudo), so I confirmed it by reading the code.
- **Not run by me:** the 27/27 tests and the 292/292 smoke are Platform's results.

**Info only:** `//srv/x` (two leading slashes) is accepted, because POSIX `normpath` keeps exactly two leading
slashes. On Linux that's the same folder as `/srv/x`, so the path isn't wrong, and only root writes the source. No
change needed.

## Deployed (2026-10-15)
- **Platform reports:** PL-065 live since 08:11Z (commit f2a9ebd).
- **I checked at about 08:23Z:** `/usr/local/sbin/rig-platform-check` is sha256 `5c37960c…`, which matches the
  reviewed hash, and is `root:root 755`. So the L1 and L2 fixes are in the installed file.

## Info
- **The setup candidate's mode is 777** in Platform's scratch, as of the stat at 05:53Z. Git keeps only the
  executable bit, so this doesn't reach the install. It does mean any local user could edit the file between this
  review and the commit. The hash check on the card covers that.
- **`test_check.py` still contains the personal home path** (4 lines in the frozen `fb08dc2b…`). It
  sits in scratch, not the repo. If it's ever added to the repo, template those paths.
