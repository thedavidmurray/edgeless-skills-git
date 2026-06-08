# Blog Post File Corruption Case (2026-06-01)

## Incident

When adding 6 new blog posts to `edgeless-website/src/lib/blog.ts`, the `patch` tool corrupted the file — it duplicated the entire 210KB file content, creating a 420KB broken file. The `patch` tool returned success but actually produced a file with duplicate `export const posts` declarations and interleaved imports.

## Root Cause

`src/lib/blog.ts` is ~210KB with 2960 lines. The `patch` tool is not reliable for files over ~100KB. When it encounters large files, it may:
- Duplicate the entire file
- Create partial matches that corrupt the structure
- Return success even when the file is malformed

## Recovery

```bash
cd edgeless-website/src/lib
git checkout blog.ts  # Restore from git
```

Then use safe methods:
```bash
# Add import at top
sed -i '' '1s/^/import { newPosts } from "..\/blog-new-posts";\n\n/' blog.ts

# Add spread at end (python is safer than sed for end-of-file)
python3 -c "
with open('blog.ts', 'r') as f:
    c = f.read()
if c.endswith('];'):
    c = c[:-2] + '  ...newPosts,\n];'
with open('blog.ts', 'w') as f:
    f.write(c)
"
```

## Verification

After editing, verify the file is valid:
```bash
npm run build  # Must compile without errors
npx tsc --noEmit src/lib/blog.ts  # TypeScript check
```

## Rule

For files > 100KB, **never use `patch`**. Use:
- `sed` for simple prepend operations
- `python3` for safe append/replace operations
- `cat` + `heredoc` for complete rewrites
