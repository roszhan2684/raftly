# Submitting Raftly to Anthropic's plugin directory

Anthropic's directory (claude.ai/directory) is how plugins get an official listing that people can add on claude.ai, in
Cowork and in Claude Code. **Only the account owner can submit**, from a browser, on a paid claude.ai plan (Pro, Max, or a
Team/Enterprise Owner). These steps were prepared on 2026-10-24 from Anthropic's docs. Re-check them if the portal changed.

## Already done in this repository

- [x] `claude plugin validate --strict .` passes (Claude Code 2.1.310)
- [x] Plugin at the repository root, with `.claude-plugin/plugin.json` (name `raftly`, version, description, author, license)
- [x] Square icon `.claude-plugin/icon.png` (1024 × 1024 PNG). **It becomes the listing icon only the first time you save or
      submit, so be sure you like it.**
- [x] `homepage`, `repository`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, `termsOfServiceUrl` set to the GitHub Pages site
- [x] README over 40 words, with a "What Raftly runs and accesses" disclosure for the security scan; LICENSE (Apache-2.0)
- [x] 356 files (limit 512), every file under 256 KiB, only text and PNG files, no `.DS_Store`, no symlinks, no submodules
- [x] No package launchers (`npx`/`uvx`), no MCP servers, no hooks, no credentials (the eval fixture uses an obvious fake value)

## Steps for you

1. Sign in at **https://claude.ai/directory/manage** with a paid plan.
2. Select **Submit new** → **Plugin bundle**.
3. Source: repository `https://github.com/roszhan2684/raftly`, plugin path: the repository root, branch `main` (or tag `v0.1.0`).
4. Select **Validate**. Fix anything marked **Blocking**, push, then select **Re-validate**.
   - Likely **policy holds** (not rejections): the name or brand check while the trademark isn't cleared (RaftLabs is the
     nearest existing name), and possibly scripts the validator reads only as text. A reviewer reads held versions.
5. Fill in the listing:
   - **Name:** Raftly · **Category:** developer tools / productivity
   - **Short description:** "Idea to production with the judgment of a senior product and engineering organization. One command: /raftly."
   - **Support:** https://github.com/roszhan2684/raftly/issues · **Privacy:** https://roszhan2684.github.io/raftly/privacy.html
6. Submit and follow the review on the plugin's page in the portal (Versions tab).

## Notes

- Raftly's skill runs local Python scripts through the Bash tool, so it's designed for **Claude Code**. On claude.ai or in Cowork,
  check the portal's component-support table; the review agents (`agents/`) are Claude Code-only.
- Anthropic's own marketplace (`claude-plugins-official`) doesn't take portal submissions. The directory listing is the official route.
- After a listing is live, raise `version` in `.claude-plugin/plugin.json` with every release so users receive updates.
- Submitting doesn't replace the open release blockers in `legal/release-gate.yaml` (trademark clearance in particular).
