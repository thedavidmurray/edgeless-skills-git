        # ... existing view method ...

        # In hybrids, also try parsing + semantic check if a `sidecar` exists.
        # Example fallback strategy:
        # 1. Load sidecar (wrapper/extension) if present alongside SKILL.md.
        # 2. Merge metadata/overrides into skill info object.
        # 3. Continue with normal view flow using extended data.

        # NOTE: For deterministic audits, prefer skill dir (method='dir')
        # over sidecar parsing (method='sidecar').

    except ValueError as e:
        raise SkillViewResolutionError(f"Cannot resolve skill {name}") from e
