# BetLabIQ Modern MVP

A modern, model-first sports analytics subscription starter website built for GitHub Pages.

## What is included

- Modern responsive homepage
- Dynamic daily picks dashboard powered by JSON
- Sport filters
- Premium/free pick labels
- Track record section
- Email capture demo section
- Responsible betting disclaimer
- Starter Python prediction updater
- Starter GitHub Actions workflow for one-click refresh

## How to launch on GitHub Pages

1. Create a GitHub repository named `betlabiq`.
2. Upload all files from this folder.
3. Go to `Settings > Pages`.
4. Choose `Deploy from a branch`.
5. Select `main` and `/root`.
6. Save.

Your site will publish at:

`https://YOURUSERNAME.github.io/betlabiq/`

## How to update picks manually

Edit:

`data/todays_picks.json`

Or run:

`python scripts/update_predictions.py`

## How to use the one-click refresh

After uploading to GitHub:

1. Go to `Actions`.
2. Select `Update Daily Picks`.
3. Click `Run workflow`.
4. Choose sport/mode.
5. Run.

The workflow will run the Python script and commit updated JSON data.

## Next upgrades

- Connect real sports data APIs
- Connect odds API
- Add results grading
- Add Beehiiv/Formspree email capture
- Add Gumroad/Stripe premium checkout
- Add separate premium page
- Add custom domain

## Responsible use

This project is for educational and entertainment purposes. Sports betting involves risk.
