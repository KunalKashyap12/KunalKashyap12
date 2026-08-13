<a href="https://github.com/KunalKashyap12/KunalKashyap12">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/KunalKashyap12/KunalKashyap12/main/dark_mode.svg">
    <img alt="KunalKashyap12's GitHub Profile README" src="https://raw.githubusercontent.com/KunalKashyap12/KunalKashyap12/main/light_mode.svg">
  </picture>
</a>

---

## Setup instructions

1. **Create the special repo.** Make a repo named exactly `KunalKashyap12`
   (same as your GitHub username) — GitHub auto-shows its README on your
   profile page.

2. **Add these files** to that repo's root:
   - `generate_readme_stats.py`
   - `requirements.txt`
   - `.github/workflows/main.yml`
   - `placeholder_profile.png` (a stand-in avatar, used until you add your own)
   - this `README.md`

   To use your own photo instead of the placeholder, add a file named
   `profile.png` (or `profile.jpg`) to the repo root — the script checks
   for that first and converts it to the ASCII-art block automatically.
   Square-ish, high-contrast photos convert best.

3. **Create a Personal Access Token.**
   Settings → Developer settings → Personal access tokens → generate one
   with `read:user` and `repo` scopes.

4. **Add it as a repo secret** named `GH_TOKEN`:
   repo Settings → Secrets and variables → Actions → New repository secret.

5. **Run the workflow once manually** (Actions tab → "Update GitHub Stats
   README Cards" → Run workflow) to generate `light_mode.svg` and
   `dark_mode.svg` for the first time. After that it re-runs daily and on
   every push.

6. Your profile page will now show the light or dark card automatically,
   matching the visitor's OS/browser theme.
