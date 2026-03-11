name: بناء موسوعة التفسير

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      test_surahs:
        description: "عدد السور للاختبار (اتركه فارغاً للكل)"
        required: false
        default: ""

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install requests beautifulsoup4 ebooklib lxml

      - name: Run scraper
        env:
          TEST_SURAHS: ${{ github.event.inputs.test_surahs || 'None' }}
        run: python scraper_kfgqpc_epub.py

      - name: Commit results to repo
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git pull --rebase
          git add dorar_tafseer_epub/
          git diff --cached --quiet || git commit -m "تحديث EPUB وملفات MD [skip ci]"
          git push