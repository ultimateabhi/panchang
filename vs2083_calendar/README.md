# Vikram Samvat 2083 — 13-Month Lunisolar Calendar (Pūrṇimānta)

A printable wall calendar covering all **thirteen lunar months** of Vikram Samvat 2083
in the **pūrṇimānta** (full-moon-ending) reckoning
(4 March 2026 – 23 March 2027), including the leap month Adhika Jyeshtha.

## What's in this package

```
vs2083_calendar/
├── generate.py    ← the generator script (run this)
├── image.jpg      ← photo embedded on each month page
├── sg_b64.txt     ← pre-computed base64 of image.jpg (auto-generated if missing)
└── README.md      ← this file
```

## Output

The script produces two files:

| File | Description |
|------|-------------|
| `Vikram_Samvat_2083_Purnimanta_Calendar.html` | Opens in any browser. References each month's image locally from `images/NN.jpg` (easy to swap). Print from browser → Save as PDF for highest quality. |
| `Vikram_Samvat_2083_Purnimanta_Calendar.pdf`  | Ready to print directly. 14 pages (cover + 13 months) at 21.6 × 16.5 cm. Images embedded as base64. |

## Quotes & images

Each month carries a Sadhguru quote and a matching image, chosen per month and
defined in the `PICKS` dictionary near the top of `generate.py` (month number →
`(quote, image URL)`). On first run the script downloads each image into
`images/NN.jpg`; the HTML then points at those local files and the PDF embeds them.

- To re-choose: open `quote_picker.html` in a browser, pick one card per month,
  copy the pick-code, and update `PICKS` accordingly (or ask to regenerate).
- To swap a single image: replace the corresponding `images/NN.jpg` file.
- `--no-download` skips downloading and references Isha's remote URLs instead
  (handy offline-preview or if you don't want local copies).

Quotes and images are © Isha Foundation — fine for personal use, not redistribution.

## Requirements

- **Python 3.8+**
- **wkhtmltopdf** — for PDF generation (HTML works without it)
- **Pillow** *(optional)* — only needed if you replace `image.jpg` with an AVIF/WebP/PNG

### Install on Ubuntu / Debian

```bash
sudo apt install wkhtmltopdf
pip install Pillow          # optional, only for image conversion
```

### Install on macOS

```bash
brew install wkhtmltopdf
pip install Pillow          # optional
```

## Usage

### Generate both HTML and PDF

```bash
cd vs2083_calendar
python3 generate.py
```

Output files appear in the current directory.

### Generate to a specific folder

```bash
python3 generate.py --outdir ~/Desktop/calendar
```

### Generate HTML only (no wkhtmltopdf needed)

```bash
python3 generate.py --html-only
```

Then open `Vikram_Samvat_2083_Calendar.html` in a browser and use
**Print → Save as PDF** (enable "Background graphics" in print settings).

## Customisation

### Replace the image

Drop your image as `image.jpg` in the script directory (alongside `generate.py`),
delete `sg_b64.txt`, and re-run. The script will auto-encode the new image.

If your image is AVIF, PNG, or WebP, name it `image.avif` (or `.png` / `.webp`)
and the script will convert it (requires Pillow).

### Change quotes

Open `generate.py` and edit the `QUOTES` list near the top. Each entry is a
tuple of `(quote_text, attribution)`. Use `\n` for line breaks within a quote.

### Change festivals

Each month's `fest` dictionary maps a **(paksha, tithi)** key → festival name:
`("K", n)` = Krishna (waning) tithi n, `("S", n)` = Shukla (waxing) tithi n
(`("S",15)` = Pūrṇimā / month-end), and the string key `"amavasya"` = the new-moon
day. For Gregorian-fixed festivals (like Makar Sankrānti), use the `greg_fest`
dictionary with `datetime.date` keys.

### Change page size

Find the `@page` rule and the `wkhtmltopdf` command arguments in `generate.py`.
Both need to match. Current size: **21.6 cm × 16.5 cm**.

## Calendar structure

- **Pūrṇimānta reckoning**: each month runs full moon → full moon
- **Two fortnights per month**: Krishna Paksha (waning, १→ to Amāvāsyā)
  then Shukla Paksha (waxing, १→१५ to Pūrṇimā, which ends the month)
- Krishna-paksha festivals therefore sit in the month *named after the following
  Pūrṇimā* — e.g. Janmāshtamī falls in Bhādrapada, Diwali on Kārtika Amāvāsyā,
  Mahā Shivarātri in Phālguna (the key difference from an amānta calendar)
- **Tithi numbers** in bold Devanagari numerals (main number in each cell)
- **Gregorian dates** in small text (top-right of each cell)
- **Season colours**: two shades per ṛtu (lighter = shukla, deeper = krishna)
- **Weekday headers** in Hindi: र सो मं बु गु शु श
- **Month 3 (Adhika Jyeshtha)** is the leap month (★)

## Notes

- Festival placements are by tithi index (±1 day vs. a live panchang for your city)
- The month boundaries are derived from verified 2026–27 new-moon (amāvāsyā) dates
- For ritual-critical dates, always cross-check a local panchang
