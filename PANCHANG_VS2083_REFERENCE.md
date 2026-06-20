# Panchang Reference — Vikram Samvat 2083 (Pūrṇimānta)

This file is the canonical data reference for the calendar generator. It consolidates
the panchang details for **Vikram Samvat 2083** .

## Reckoning system (pūrṇimānta)

- Each lunar month runs **full moon → full moon** (pūrṇimānta = "full-moon-ending").
- Two fortnights per month:
  - **Krishna Paksha** (waning): from the day after the previous Pūrṇimā
    (Krishna Pratipadā) down to **Amāvāsyā** (new moon).
  - **Shukla Paksha** (waxing): from the day after Amāvāsyā up to **Pūrṇimā**
    (full moon), which ends the month. Shukla paksha is always 15 tithis, so
    Pūrṇimā = Shukla 15.
- Consequence: Krishna-paksha festivals sit in the month *named after the following
  Pūrṇimā* — e.g. Janmāshtamī in Bhādrapada, Diwali on Kārtika Amāvāsyā,
  Mahā Shivarātri in Phālguna. (This is the key difference from an amānta calendar.)
- VS 2083 is a **leap year**: it has a thirteenth month, the **adhika (extra) month
  Adhika Jyeshtha**, marked with a leap flag.
- Tithi labels: shown as `K n` (Krishna tithi n) or `S n` (Shukla tithi n);
  `Amāvāsyā` = new moon, `S 15` = Pūrṇimā. Devanagari numerals are used in the design.
- Notes: festival placements are by tithi index (±1 day vs. a live local panchang);
  month boundaries are derived from verified 2026–27 new-moon (amāvāsyā) dates. For
  ritual-critical dates, cross-check a local panchang.

## Month boundaries (13 months, 4 Mar 2026 – 23 Mar 2027)

| # | Month (Devanagari / roman) | Start (Krishna 1) | Amāvāsyā | End (Pūrṇimā) | Season (ṛtu) |
|---|---|---|---|---|---|
| 1 | चैत्र Chaitra | 4 Mar 2026 | 18 Mar 2026 | 2 Apr 2026 | Vasanta (spring) |
| 2 | वैशाख Vaishākha | 3 Apr 2026 | 17 Apr 2026 | 2 May 2026 | Vasanta (spring) |
| 3 | अधिक ज्येष्ठ Adhika Jyeshtha ★leap | 3 May 2026 | 16 May 2026 | 31 May 2026 | Grīshma (summer) |
| 4 | ज्येष्ठ Jyeshtha | 1 Jun 2026 | 14 Jun 2026 | 29 Jun 2026 | Grīshma (summer) |
| 5 | आषाढ Āshādha | 30 Jun 2026 | 14 Jul 2026 | 29 Jul 2026 | Varshā (monsoon) |
| 6 | श्रावण Shrāvana | 30 Jul 2026 | 12 Aug 2026 | 27 Aug 2026 | Varshā (monsoon) |
| 7 | भाद्रपद Bhādrapada | 28 Aug 2026 | 10 Sep 2026 | 25 Sep 2026 | Sharad (autumn) |
| 8 | आश्विन Āshwina | 26 Sep 2026 | 10 Oct 2026 | 25 Oct 2026 | Sharad (autumn) |
| 9 | कार्तिक Kārtika | 26 Oct 2026 | 8 Nov 2026 | 23 Nov 2026 | Hemanta (pre-winter) |
| 10 | मार्गशीर्ष Mārgashīrsha | 24 Nov 2026 | 8 Dec 2026 | 23 Dec 2026 | Hemanta (pre-winter) |
| 11 | पौष Pausha | 24 Dec 2026 | 7 Jan 2027 | 22 Jan 2027 | Shishira (winter) |
| 12 | माघ Māgha | 23 Jan 2027 | 6 Feb 2027 | 21 Feb 2027 | Shishira (winter) |
| 13 | फाल्गुन Phālguna | 22 Feb 2027 | 8 Mar 2027 | 23 Mar 2027 | Shishira (winter) |

## Festivals / markers per month

Keyed by tithi (`K`/`S` + number), `Amāvāsyā`, or a fixed Gregorian date.

- **Chaitra:** S1 Gudi Padwa · Ugadi; S9 Rāma Navamī; S15 Hanumān Jayantī.
- **Vaishākha:** S3 Akshaya Tritīyā; S15 Buddha Pūrṇimā.
- **Adhika Jyeshtha:** (leap month — no major festivals).
- **Jyeshtha:** S10 Gangā Dussehra; S11 Nirjalā Ekādashī; S15 Vat Pūrṇimā.
- **Āshādha:** S2 Rath Yātrā; S11 Devshayanī Ekādashī; S15 Guru Pūrṇimā.
- **Shrāvana:** S5 Nāg Panchamī; S15 Rakshā Bandhan.
- **Bhādrapada:** K8 Janmāshtamī; S4 Gaṇesha Chaturthī; S14 Anant Chaturdashī.
- **Āshwina:** K1 Pitru Paksha begins; S1 Sharad Navrātri; S10 Dussehra; S15 Sharad Pūrṇimā.
- **Kārtika:** K13 Dhanteras; Amāvāsyā **DIWALI**; S1 Govardhan Pūjā; S2 Bhai Dooj; S11 Dev Uthanī Ekādashī; S15 Kārtik Pūrṇimā.
- **Mārgashīrsha:** S11 Gītā Jayantī; S15 Dattātreya Jayantī.
- **Pausha:** S15 Pausha Pūrṇimā; fixed date 14 Jan 2027 Makar Sankrānti.
- **Māgha:** S5 Vasant Panchamī; S15 Māghī Pūrṇimā.
- **Phālguna:** K14 Mahā Shivarātri; S14 Holikā Dahan; S15 **HOLI**.

## Per-month quote (paired with the month photo)

Each month carries a short quote shown alongside its photo (all attributed to
**Sadhguru** in the prior build). These are configurable per month.

1. **Chaitra** — "When stillness arises from intense alertness and awareness, your perception opens up in ways that you have never thought possible."
2. **Vaishākha** — "Devotion means keeping your intellect aside to let a larger intelligence function through you."
3. **Adhika Jyeshtha** — "If you want Transformation, the largest part has to happen in your Body, because the Body carries substantially more memory than the Mind."
4. **Jyeshtha** — "Success means doing something the way it works."
5. **Āshādha** — "May you realize the true purpose and potential of life. On this Guru Purnima, grace is upon you. I am with you."
6. **Shrāvana** — "Your ways of thinking and feeling, your likes and dislikes, your philosophies and ideologies all melt down when you fall in love."
7. **Bhādrapada** — "If you want to explore the deepest dimensions of life playfully, you need a heart full of love, a joyful mind, and a vibrant body."
8. **Āshwina** — "If you treat your tools, including your own body and mind, with reverence, every activity will be a fruitful and joyful process."
9. **Kārtika** — "Lighting up in joy, love, and consciousness is vital in times of crisis. This Diwali, light up your Humanity to its full glory."
10. **Mārgashīrsha** — "The word Yoga means union. That means you consciously obliterate the boundaries of individuality and reverberate with the rest of the cosmos."
11. **Pausha** — "This is an ideal day to clear your home, your mind, and your emotions of all that is redundant, and make a Fresh Start."
12. **Māgha** — "Life is not in its goal. Life is in its process – in how you Experience it within yourself right now."
13. **Phālguna** — "Adiyogi Shiva is the source of the science of yoga. His relevance is not in his ancientness but of the future."

## Season (ṛtu) accent colours

From the existing generator — usable as the design's accent palette per month:

| ṛtu | accent | light (shukla) | deep (krishna) |
|---|---|---|---|
| Vasanta | #4E8B3A | #e8f2e2 | #d2e4c8 |
| Grīshma | #C8771B | #f7ecda | #f0dcc2 |
| Varshā | #1F8A8A | #ddf0f0 | #c8e2e2 |
| Sharad | #C0561E | #f9e8dd | #f0d4c4 |
| Hemanta | #5B4B9A | #eae5f4 | #d9d2ea |
| Shishira | #3F6B8C | #e2ecf2 | #cddde8 |

## Existing project assets to reuse

- `vs2083_calendar/generate.py` — working HTML/PDF generator (data + logic source of truth).
- `vs2083_calendar/README.md` — full documentation of the reckoning and customisation.
- `vs2083_calendar/images/01.jpg … 13.jpg` — one photo per month.
- `Long-desktop_design.png` — the target visual design (photo-left, calendar-right tent panel).
- `calendar_pages/`, `images/` — rendered pages and month images from the prior build.
