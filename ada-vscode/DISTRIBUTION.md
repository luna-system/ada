# Ada VS Code Monorepo - Package Distribution

## Workspace Protocol (Current Approach)

The `@ada-code/shared` package uses pnpm's `workspace:*` protocol for internal references:

```json
{
  "dependencies": {
    "@ada-code/shared": "workspace:*"
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

## Future: Publishing to npm (v1.1.0+)

If we want to publish `@ada-code/shared` to npm for external use:

1. **Publish shared package:**
   ```bash
   cd packages/shared
   npm publish --access public
   ```

2. **Update ada-chat to use published version:**
   ```json
   {
     "dependencies": {
       "@ada-code/shared": "^1.0.0"
     }
   }
   ```

**For v1.0.0:** Workspace protocol is PERFECT for our needs! ✨

## Distribution Strategy

- **Development:** `workspace:*` (current)
- **VS Code Extension:** Packages everything in VSIX (no external deps)
- **Future npm:** Only if other projects need `@ada-code/shared`

**Decision:** Keep `workspace:*` for v1.0.0. Publishing is a v1.1.0+ enhancement if needed.
