# Emergency Rollback Procedures

*"Sometimes you've got to go back to go forward"*

This document provides quick rollback procedures for BoxOfPorts releases when issues are discovered.

## 🚨 Quick Rollback (Stable Docker Tag)

If a stable release has critical issues, rollback the Docker tag immediately:

```bash
# Rollback stable to previous version (replace 1.2.5 with target version)
./scripts/retag_by_digest.sh \
  altheasignals/boxofports:1.2.5 \
  altheasignals/boxofports:stable

# Verify the rollback
docker inspect altheasignals/boxofports:stable --format='{{index .Config.Labels "version"}}'
```

## 📋 Rollback Decision Tree

### 1. **Issue with Stable Release (X.Y.0)**
**Symptoms**: Users report issues with `bop` commands (default stable track)

**Actions**:
1. **Immediate**: Rollback stable Docker tag (see above)
2. **Communication**: Update GitHub release notes with known issues
3. **Investigation**: Determine if fix requires new patch or rollback is sufficient
4. **Resolution**: Either promote previous stable or create hotfix version

### 2. **Issue with Development Release (X.Y.Z where Z>0)**  
**Symptoms**: Issues reported by development track users (`BOP_RELEASE_TRACK=dev`)

**Actions**:
1. **Assessment**: Development issues are expected - determine severity
2. **If Critical**: Rollback latest tag to previous dev version
3. **If Minor**: Document in GitHub release and fix in next development release

### 3. **Workflow Issues**
**Symptoms**: GitHub Actions failing, incorrect version bumps

**Actions**:
1. **Disable problematic workflow** (temporarily) 
2. **Revert workflow commits** using `git revert`
3. **Manual version correction** if needed
4. **Test workflow fix** on feature branch before re-enabling

## 🔧 Rollback Commands

### Stable Tag Rollback
```bash
# Find previous stable version
git tag -l 'v*.*.*' | grep -E 'v[0-9]+\.[0-9]+\.0$' | sort -V | tail -n 2

# Rollback stable tag (example: back to 1.1.0)
./scripts/retag_by_digest.sh \
  altheasignals/boxofports:1.1.0 \
  altheasignals/boxofports:stable
```

### Latest Tag Rollback  
```bash
# Find previous dev version
git tag -l 'v*.*.*' | grep -v -E 'v[0-9]+\.[0-9]+\.0$' | sort -V | tail -n 2

# Rollback latest tag (example: back to 1.2.3)  
./scripts/retag_by_digest.sh \
  altheasignals/boxofports:1.2.3 \
  altheasignals/boxofports:latest
```

### Git Version Rollback
```bash
# Revert version bump commit
git revert <commit-hash>
git push origin main

# Or reset version manually
# Edit pyproject.toml to correct version
git add pyproject.toml
git commit -m "fix(version): rollback to 1.2.5 due to release issues"
git push origin main
```

## 📝 Rollback Checklist

When performing any rollback:

- [ ] **Identify root cause** - Don't rollback without understanding the issue
- [ ] **Check impact scope** - Stable vs dev track, which users affected  
- [ ] **Communicate early** - Update GitHub releases, notify team
- [ ] **Execute rollback** - Use appropriate method above
- [ ] **Verify rollback** - Test that users get expected version
- [ ] **Document incident** - Add to promotion log with timestamp and reason
- [ ] **Plan resolution** - Hotfix, new release, or investigation needed?

## 🔍 Verification Commands

After any rollback, verify the changes:

```bash
# Check Docker tags
docker inspect altheasignals/boxofports:stable --format='{{index .Config.Labels "version"}}'
docker inspect altheasignals/boxofports:latest --format='{{index .Config.Labels "version"}}'

# Test wrapper behavior
bop --bop-version                    # Should show stable track version
BOP_RELEASE_TRACK=dev bop --bop-version   # Should show dev track version

# Check Git state  
git log --oneline -5                 # Recent commits
git tag -l 'v*.*.*' | sort -V | tail -5    # Recent tags
```

## 🎯 Prevention

To minimize rollbacks:

- **Use dry-run modes** in workflows before real execution
- **Test stable releases** thoroughly before promotion  
- **Monitor post-release** for user reports
- **Keep rollback tools ready** (scripts tested and documented)

## 📞 Escalation

If rollback procedures don't resolve the issue:

1. **Stop automatic processes** (disable relevant workflows)
2. **Assess blast radius** (how many users affected)  
3. **Consider communication** (GitHub issue, user notification)
4. **Plan systematic fix** (don't rush, methodical approach)

---

*"Every mistake's a lesson, every rollback's a song that teaches us harmony."*

The system is designed to flow forward, but sometimes the river needs to find a new course.