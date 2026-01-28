# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Session Completion Checklist

**Before ending a session**, let's make sure everything is synced and ready for next time! 💜

**Workflow:**

1. **Create issues for remaining work** - Anything that needs follow-up gets a task
2. **Run quality checks** (if code changed) - Tests, linters, builds
3. **Update task status** - Close finished work, update in-progress items
4. **Sync everything**:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # Should show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches if needed
6. **Verify** - All changes committed and pushed
7. **Hand off** - Leave notes for next session

**Important Notes:**
- Work persists across sessions when pushed to remote
- If push fails, resolve conflicts and retry
- Beads syncs with git, so everything stays coordinated

