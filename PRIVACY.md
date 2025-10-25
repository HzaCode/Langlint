# Privacy Policy

**Effective Date:** January 1, 2025  
**Last Updated:** January 1, 2025

## Overview

LangLint is committed to protecting your privacy. This document explains how LangLint handles data when you use the software.

## Data Collection and Processing

### What LangLint Does

LangLint is a **local-first** tool that processes your code and documentation files:

- ✅ **Local Processing**: All file parsing and analysis happens on your machine
- ✅ **No Telemetry**: LangLint does not collect, transmit, or store any usage statistics
- ✅ **No Analytics**: No tracking, no cookies, no user behavior monitoring
- ✅ **Open Source**: All code is publicly auditable on [GitHub](https://github.com/HzaCode/Langlint)

### When Data Leaves Your Machine

LangLint **only** sends data to external services when you explicitly use translation features:

#### Google Translate (Default)
- **What is sent**: Text extracted from comments and docstrings
- **Where it goes**: Google's translation API servers
- **Your control**: Only sent when you run `langlint translate` or `langlint fix`
- **Third-party terms**: Subject to [Google's Terms of Service](https://policies.google.com/terms)

#### Mock Translator (Testing)
- **What is sent**: Nothing - all processing is local
- **Purpose**: For testing and development

## Data You Control

### Input Files
- Your source code files remain on your machine
- LangLint reads files only when you explicitly run commands
- Original files are never modified unless you use `langlint fix`

### Backups
- When using `langlint fix`, backups are created with `.backup` extension by default
- You can disable backups with `--no-backup` flag
- Backups remain on your local machine

### Cache
- LangLint may cache translation results locally in `~/.cache/langlint/` (or equivalent on your OS)
- Cache is stored only on your machine
- You can clear cache by deleting the cache directory

## Your Rights and Controls

### You Have Complete Control

1. **Opt-out of translation**: Simply don't use `translate` or `fix` commands
2. **Use mock translator**: Use `--translator mock` to avoid any external API calls
3. **Review before sending**: Use `--dry-run` to preview what would be translated
4. **Delete cache**: Remove `~/.cache/langlint/` at any time

### Data Minimization

LangLint follows data minimization principles:

- ❌ **Does NOT collect**: Personal information, IP addresses, file paths, or metadata
- ❌ **Does NOT store**: Your code, translations, or any user data on our servers
- ❌ **Does NOT share**: Any information with third parties (except translation APIs you explicitly choose)

## Third-Party Services

### Google Translate

When you use Google Translate:
- Google receives the text you choose to translate
- Google's [Privacy Policy](https://policies.google.com/privacy) applies
- Google may process data according to their terms

**Important**: If you translate sensitive code or proprietary information, consider:
- Using `--dry-run` first to review what will be sent
- Using `--translator mock` for testing
- Reviewing [Google's data processing terms](https://cloud.google.com/terms/data-processing-addendum)

## Security

### Local Data
- LangLint runs with your user's file system permissions
- No data is transmitted to LangLint developers
- No authentication or API keys are stored by LangLint (except in your environment variables or config files you create)

### API Keys
If you configure API keys (future translators):
- Keys are read from environment variables or config files **you** create
- Keys are never sent to LangLint servers (we don't have any servers)
- Keys are your responsibility to secure

## Open Source Transparency

LangLint is fully open source:
- **Source code**: https://github.com/HzaCode/Langlint
- **License**: MIT License
- **Audit**: You can review all code to verify privacy claims

## Children's Privacy

LangLint does not knowingly collect any data from anyone, including children under 13.

## Changes to This Policy

We may update this privacy policy to reflect:
- New features or translators
- Changes in data processing practices
- Regulatory requirements

Changes will be documented in our [GitHub repository](https://github.com/HzaCode/Langlint) with version history.

## Compliance

### GDPR (European Users)

LangLint's local-first design means:
- **No data controller**: LangLint developers do not process your personal data
- **Third-party processors**: Google (when you use their translator) processes data as described in their privacy policy
- **Your rights**: You control what data is sent to translation services

### CCPA (California Users)

- LangLint does not sell personal information
- LangLint does not collect personal information
- Third-party translation services may have their own data practices

## Contact

If you have questions about this privacy policy:

- **Email**: ang@hezhiang.com
- **GitHub Issues**: https://github.com/HzaCode/Langlint/issues
- **Discussions**: https://github.com/HzaCode/Langlint/discussions

## Summary

**TL;DR:**
- ✅ LangLint processes files locally on your machine
- ✅ No telemetry, tracking, or analytics
- ✅ Translation text only sent to APIs you explicitly choose to use
- ✅ You have complete control over what data leaves your machine
- ✅ Fully open source and auditable

---

*This privacy policy is part of the LangLint open source project, licensed under MIT.*

