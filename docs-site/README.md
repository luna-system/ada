# Ada Documentation Site

This Astro project orchestrates Ada's complete documentation for GitHub Pages deployment.

## What This Does

**This is the unified docs site**, not the frontend chat UI. It:

1. **Builds Sphinx documentation** from `../docs/`
2. **Copies built HTML** into `public/docs/`
3. **Builds Astro site** with garden landing page at root
4. **Deploys to GitHub Pages** at `luna-system.github.io/ada/`

## Structure

```
docs-site/
├── src/pages/index.astro    # Garden landing page (solarpunk)
├── public/docs/              # Sphinx docs (copied during build)
├── astro.config.mjs          # GitHub Pages configuration
└── package.json              # Build scripts
```

## Local Development

```bash
# Install dependencies
npm install

# Build everything (Sphinx + Astro)
npm run build

# Preview built site
npm run preview
```

## Build Process

The `npm run build` command does:

1. `cd ../docs && make html` - Build Sphinx docs
2. `mkdir -p public/docs && cp -r ../docs/_build/html/* public/docs/` - Copy output
3. `astro build` - Build Astro site with garden landing

Output goes to `dist/`:
- `dist/index.html` - Garden landing page
- `dist/docs/` - Complete Sphinx documentation

## GitHub Pages Deployment

Deployed via `.github/workflows/build-docs.yml` to:
- **Root:** Garden landing at `luna-system.github.io/ada/`
- **Docs:** Sphinx docs at `luna-system.github.io/ada/docs/`

## Why Separate from Frontend?

**Frontend (`frontend/`)** is a runtime chat adapter (Docker service).  
**Docs-site (`docs-site/`)** is static documentation (GitHub Pages only).

This keeps:
- Chat UI independently forkable
- Docs always accessible (even without running Ada)
- Clean separation: presentation vs. function

## Architecture Decision

This approach was chosen to:
1. Keep frontend purely functional (just chat)
2. Unify docs presentation under one tool (Astro)
3. Enable rich landing page with solarpunk aesthetic
4. Maintain Sphinx for technical docs (best RST tooling)

## Files vs URLs

When building for GitHub Pages:
- Links use `/ada/docs/` prefix (see `astro.config.mjs` base)
- Local preview removes the prefix automatically
- Sphinx internal links work in both contexts
