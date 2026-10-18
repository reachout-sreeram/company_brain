# Public walkthrough deployment

Public URL: [Company Brain walkthrough](https://company-brain-gules.vercel.app).

Vercel project: `company-brain`, in `reachoutsreeram-8103s-projects`. The connected GitHub repository is `reachout-sreeram/company_brain`; the production branch is `main`. Vercel Authentication is disabled for this public static site.

The source is [the transit-map HTML](../../presentation-assets/company-brain-transit-map/index.html). The [build script](../../scripts/build-walkthrough.mjs) copies it and its assets into the ignored `.vercel-static/` directory. [vercel.json](../../vercel.json) disables dependency installation and publishes only that output. No Python function, database, model API, or application secret is required. Geist and Geist Mono are served locally under their included SIL Open Font License.

The page labels its data as synthetic. Its animations and controls explain recorded behavior; they do not call MCP or query a live database. The MCP implementation and its local setup remain in the repository. See [Run locally](../../README.md#run-locally).

## Update

Edit the source HTML, then run:

```sh
node scripts/build-walkthrough.mjs
git diff --check
```

Check the resulting HTML in a browser. Commit the source and push `main` to trigger the connected Vercel deployment. Generated output stays untracked. `.vercelignore` excludes local credentials, environments, database files, evaluations, and backend source from CLI uploads.

## Verification on 18 October 2026

The redesign keeps all 17 scene hashes and the original graph behavior. It adds five chapter tabs, an all-scenes menu, a progress indicator, collapsed technical details, mobile diagram zoom and keyboard access to graph receipts. The desktop player has a stable layout; longer explanations scroll within the adjacent panel.

The headless browser check exercised all 17 scenes, scene navigation, replay, play/pause, scene buttons and range controls. No page errors occurred. Layout checks at 390, 768 and 1365 pixels found no document overflow. These checks validate the walkthrough, not new MCP or graph behavior.
