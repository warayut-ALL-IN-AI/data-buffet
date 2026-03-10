# Data-Buffet

A modern BigQuery data warehouse built on Dataform, implementing a three-layer medallion architecture.

## 📚 Documentation

All project documentation has been moved to the **[DOCUMENT](./DOCUMENT/)** folder.

### Quick Links

- **[Project Overview](./DOCUMENT/README.md)** - Start here for project introduction
- **[Quick Reference](./.claude/QUICK-REFERENCE.md)** - Commands and templates
- **[Documentation Index](./DOCUMENT/DOCUMENTATION.md)** - Navigate all documentation

### Main Documentation Files

📁 **[DOCUMENT/](./DOCUMENT/)**
- [README.md](./DOCUMENT/README.md) - Complete project overview & quick start
- [CLAUDE.md](./DOCUMENT/CLAUDE.md) - Technical guide for Claude Code
- [CONTRIBUTING.md](./DOCUMENT/CONTRIBUTING.md) - Development guidelines
- [DOCUMENTATION.md](./DOCUMENT/DOCUMENTATION.md) - Documentation index
- [CHANGELOG.md](./DOCUMENT/CHANGELOG.md) - Version history
- [PROJECT-SUMMARY.md](./DOCUMENT/PROJECT-SUMMARY.md) - Complete summary

📁 **[.claude/](./.claude/)**
- [QUICK-REFERENCE.md](./.claude/QUICK-REFERENCE.md) - Fast lookup
- [DEVELOPMENT-GUIDE.md](./.claude/DEVELOPMENT-GUIDE.md) - Development workflow
- [knowledge/](./.claude/knowledge/) - Layer-specific guides

## 🚀 Quick Start

```bash
# Compile all transformations
dataform compile

# Run all transformations
dataform run

# Run specific layer
dataform run --tags validated
dataform run --tags curated
dataform run --tags fact
```

## 🏗️ Architecture

**Three-Layer Medallion Design:**
- **Layer 1: Validated** - Raw → Clean (89 tables)
- **Layer 2: Curated** - Clean → Business (6 transformations)
- **Layer 3: Fact** - Business → Analytics (1 fact table)

## 📖 For Developers

1. **New to the project?** Read [DOCUMENT/README.md](./DOCUMENT/README.md)
2. **Need commands?** Check [.claude/QUICK-REFERENCE.md](./.claude/QUICK-REFERENCE.md)
3. **Contributing?** See [DOCUMENT/CONTRIBUTING.md](./DOCUMENT/CONTRIBUTING.md)
4. **Layer-specific work?** Check [.claude/knowledge/](./.claude/knowledge/)

## 🤖 For Claude Code

All Claude-specific documentation is in the [.claude/](./.claude/) directory:
- [CLAUDE.md](./DOCUMENT/CLAUDE.md) - Main technical guide
- [.claude/README.md](./.claude/README.md) - Claude documentation overview
- [.claude/knowledge/](./.claude/knowledge/) - Deep layer knowledge

## 🔧 Technology Stack

- **Platform**: Google Cloud BigQuery
- **Framework**: Dataform 3.0.0
- **Language**: SQLX (SQL + JavaScript)
- **Version**: 3.1.0

## 📞 Support

- **Documentation**: See [DOCUMENT/](./DOCUMENT/) folder
- **Quick Help**: [.claude/QUICK-REFERENCE.md](./.claude/QUICK-REFERENCE.md)
- **Navigation**: [DOCUMENT/DOCUMENTATION.md](./DOCUMENT/DOCUMENTATION.md)

---

**Project**: databuffet-nonprd (GCP us-central1)
**Branch**: nonprod
**Last Updated**: 2026-01-05
