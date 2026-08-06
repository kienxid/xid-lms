# Deployment

## Platform

GitHub Pages publishes the repository root from the `main` branch.

Production URL: <https://kienxid.github.io/xid-lms/>

## Automatic deployment

Every push to `main` triggers a GitHub Pages deployment. No build command or environment variables are required.

To publish a new training game:

1. Add a folder containing its own `index.html` and assets.
2. Add the folder link to the root `index.html`.
3. Commit and push both changes to `main`.
4. Confirm the Pages workflow succeeds in GitHub Actions.

## Custom domain

No custom domain is configured. Google Sites can link directly to the production URL or an individual game URL.

## Rollback

Revert the faulty commit and push the revert to `main`. GitHub Pages will automatically publish the restored version.
