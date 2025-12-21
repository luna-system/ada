# Ada VS Code Monorepo - Package Distribution

## Workspace Protocol (Current Approach)

The `shared` package uses pnpm's `workspace:*` protocol for internal references:

```json
{
  "dependencies": {
    "shared": "workspace:*"
  }
}
```

**Why this works:**
- ✅ pnpm resolves to local package during development
- ✅ No npm publishing needed for internal use
- ✅ TypeScript project references handle build order
- ✅ Changes reflect immediately across packages

## Development Workflow

1. **Make changes in shared:**
   ```bash
   cd packages/shared
   # Edit src files
   pnpm build
   ```

2. **Changes available in ada-chat immediately:**
   ```bash
   cd ../ada-chat
   pnpm build  # Sees updated shared/dist/
   ```

3. **Package extension:**
   ```bash
   npx @vscode/vsce package --no-dependencies
   ```

## Distribution Strategy

- **Development:** `workspace:*` (current)
- **VS Code Extension:** Packages everything in VSIX (no external deps)
- **Shared package:** Internal only, not published to npm
