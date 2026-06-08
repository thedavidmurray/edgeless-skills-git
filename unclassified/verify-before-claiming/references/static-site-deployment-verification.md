# Static Site Deployment Verification

**Trigger:** When claiming a static site (Next.js export, Jekyll, Hugo, etc.) has been deployed with new content.

**Rule:** Never declare "deployed" until you see the new content on the live URL with your own `curl` output.

## Full Chain Verification

```bash
# 1. Verify commit is on origin/main
git log --oneline origin/main -3
# → Must show the new commit

# 2. Verify GitHub Actions triggered
gh api repos/OWNER/REPO/actions/runs?per_page=5 | \
  jq -r '.workflow_runs[0] | "\(.head_sha[0:7]) | \(.status) | \(.conclusion)"'
# → Must show the new commit hash, status "completed", conclusion "success"
# If not triggered after 2 min, manually trigger from GitHub Actions page

# 3. Verify live site content
curl -s https://YOURSITE.com/blog/ | grep -o 'href="/blog/[^"]*"' | head -5
# → Must show the new post slug in the expected position

# 4. Verify ordering (for list pages)
curl -s https://YOURSITE.com/blog/ | sed -n 's/.*<time[^>]*>\([^<]*\)<.*/\1/p' | head -5
# → Dates must be in descending order (newest first)

# 5. If ordering is wrong, the page.tsx isn't sorting — fix before declaring done
```

## Common Static Site Deployment Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| GitHub Actions doesn't trigger | Webhook delay or stuck queue | Wait 2-3 min, then manually trigger |
| Build succeeds but no new content | `out/` directory not committed | Check `git status` for untracked files |
| Posts appear at bottom of list | `page.tsx` doesn't sort by date | Add `sortedPosts` array before rendering |
| Missing CSS/styles | `postcss` or `tailwindcss` not installed | `npm install @tailwindcss/postcss` |
| TypeScript error on `ResolvingMetadata` | Next.js 16.2.0 type bug | Add `typescript: { ignoreBuildErrors: true }` to config |

## Next.js 16.2.0 Specific Build Issues

**Missing `@tailwindcss/postcss`:**
```bash
npm install @tailwindcss/postcss
```

**`ResolvingMetadata` type error:**
```ts
// next.config.ts
const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  // ... rest of config
};
```

**Turbopack config conflict:**
```ts
// Keep minimal — remove webpack: and turbopack: keys
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  typescript: { ignoreBuildErrors: true },
};
```

## Source Files Deleted

**Symptom:** `git status` shows `D src/lib/blog.ts`, `D src/app/blog/page.tsx`

**Fix:**
```bash
cd ~/claude-projects/edgeless-website
git status --short | grep "^ D" | awk '{print $2}' | \
  xargs -I{} git checkout HEAD -- {}
```

**Root cause:** The `out/` directory build process can overwrite or delete source files if the build script is misconfigured or if `.next/` cache corruption occurs.
