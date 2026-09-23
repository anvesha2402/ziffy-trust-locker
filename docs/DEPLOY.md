# Deploying to GitHub and Streamlit Community Cloud (≈10 minutes)

## 1 · Put the code on GitHub
1. Create a new **public** repository at github.com/new called `ziffy-trust-locker`. Don't add a README; this repo already has one.
2. In a terminal inside this folder:
   ```bash
   git init            # skip if the folder already has .git
   git add .
   git commit -m "Health Data Locker — digital trust toolkit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/ziffy-trust-locker.git
   git push -u origin main
   ```
   No terminal? On the empty repo page, click **"uploading an existing file"** and drag the whole folder contents in.

## 2 · Deploy the app
1. Go to **share.streamlit.io** and sign in with GitHub.
2. Click **Create app → Deploy a public app from GitHub**.
3. Repository `your-username/ziffy-trust-locker`, branch `main`, main file `app.py`.
4. Under *Advanced settings*, choose Python 3.11 or 3.12.
5. Pick a custom subdomain, e.g. `health-data-locker`, then **Deploy**. The first build takes about 3 minutes.

## 3 · Polish for LinkedIn / recruiters
- Replace `<you>` in the README clone URL and add the live-app link at the top.
- In the GitHub repo **About** panel, add the app URL and topics: `streamlit`, `healthtech`, `data-privacy`,
  `dpdp`, `survey-analytics`, `product-management`.
- Pin the repository on your GitHub profile.
- Record a 60–90 s screen capture: consent wizard → blocked pharmacy access → tamper demo → ROI. Use it as the LinkedIn post video.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: core` | The main file must be `app.py` at the repo root |
| Graphviz diagram blank | It's rendered in the browser; hard-refresh the page |
| App sleeps after inactivity | Normal on the free tier; the first visitor wakes it in about 30 s |
