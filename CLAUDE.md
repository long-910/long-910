# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a GitHub profile README repository (`long-910/long-910`). It contains no build system or test suite — the "code" is GitHub Actions workflows and Markdown content.

## Structure

- `README.md`, `README.ja.md`, `README.zh.md` — trilingual profile pages (English, Japanese, Chinese). All three must be kept in sync when making content changes.
- `.github/workflows/` — automation workflows
- `profile-summary-card-output/` — auto-generated SVG stat cards (committed by CI)

## GitHub Actions Workflows

| Workflow | Schedule | Purpose |
|---|---|---|
| `zenn-blog-post.yml` | Daily | Syncs Zenn RSS feed into `<!-- BLOG-POST-LIST:START/END -->` markers in all 3 READMEs |
| `recent-activity.yml` | Every 30 min | Updates `<!--START_SECTION:activity-->` markers in all 3 READMEs |
| `waka-readme.yml` | Daily | Updates `<!--START_SECTION:waka-->` markers with WakaTime coding stats |
| `profile-summary-cards.yml` | Daily | Generates SVGs into `profile-summary-card-output/` (requires `PROFILE_SUMMARY_CARDS` secret) |
| `snake.yml` | Daily + on push to main | Generates contribution snake SVGs pushed to `output` branch |

## Required GitHub Secrets

- `PROFILE_SUMMARY_CARDS` — token for `vn7n24fzkq/github-profile-summary-cards`
- `WAKATIME_API_KEY` — WakaTime API key for coding stats
- `GITHUB_TOKEN` — auto-provided by GitHub Actions

## Auto-updated Sections

These sections in all READMEs are managed by CI and should not be manually edited:

- Between `<!-- BLOG-POST-LIST:START -->` and `<!-- BLOG-POST-LIST:END -->` (Zenn posts)
- Between `<!--START_SECTION:activity-->` and `<!--END_SECTION:activity-->` (GitHub activity)
- Between `<!--START_SECTION:waka-->` and `<!--END_SECTION:waka-->` (WakaTime stats)

## Git Commit Convention

The `.gitmessage` template adds a co-author trailer:
```
Co-authored-by: Small Long <7323488+long-910@users.noreply.github.com>
```
