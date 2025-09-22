# Docker Hub Setup Instructions

Follow these steps to enable automatic publishing of BoxOfPorts to Docker Hub:

## 1. Create Docker Hub Repository

1. Go to [Docker Hub](https://hub.docker.com)
2. Create a new repository: `altheasignals/boxofports`
3. Make it public (or private if you prefer)

## 2. Generate Docker Hub Access Token

1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Name: `github-actions-boxofports`
4. Permissions: "Read, Write, Delete"
5. Copy the generated token (you won't see it again!)

## 3. Add GitHub Secrets

In your GitHub repo settings → Secrets and variables → Actions:

- `DOCKERHUB_USERNAME`: Your Docker Hub username (e.g., `altheasignals`)
- `DOCKERHUB_TOKEN`: The access token from step 2

## 4. Update GitHub URLs

Replace `<GITHUB_OWNER>` in these files with your actual GitHub username/org:
- `scripts/install-bop.sh` (line 34)
- `docs/DISTRIBUTION.md` (line 24)  
- `README.md` (line 7)

## 5. Test the Workflow

1. Commit and push these changes to your main branch
2. Check GitHub Actions tab - the workflow should run automatically
3. Verify images appear on Docker Hub: `altheasignals/boxofports:latest` and `altheasignals/boxofports:1.0.0`

## 6. Test End-to-End

Once published, test the user installation:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/gateway-manager/main/scripts/install-bop.sh | bash
bop --help
```

## 7. Future Releases

- Update version in `pyproject.toml`
- Create a git tag: `git tag v1.0.1 && git push --tags`
- GitHub Actions will automatically build and push the new version

That's it! Your users can now install BoxOfPorts with a single command, no Python or local setup required.