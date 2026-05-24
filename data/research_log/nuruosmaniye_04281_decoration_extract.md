# Nuruosmaniye 04281: YEK Detail

**Discovery context**: Recovered 2026-05-02 via authenticated YEK detail-page lookup for shelfmark 178787. Prior YEK title-field searches for "Cihansah", "Cihan Şah", "Hakiki" returned nothing; the manuscript is catalogued only as `Dîvân` with attribution evident from the reference field, not the title or author field.

**YEK ID**: 178787
**URL**: https://portal.yek.gov.tr/works/detail/178787

**Current register status note (2026-05-11)**: This extract is superseded for witness-status purposes by the final register entry. A later IIIF visual-confirmation pass read the colophon and reclassified Nuruosmaniye 04281 as `rejected` with `rejection_type: scribal_homonym_misidentification`. The decoration data below is retained as audit material for a non-Cihanşah codex, not as Cihanşah-corpus decoration evidence.

**Surrogate access note**: the YEK metadata table below records `Has digitised images: false`, but the IIIF manifest endpoint later resolved during the authenticated/read pass used for the 2026-05-11 colophon check. The manifest URL is preserved in `data/witness_register.json` under `nuruosmaniye_04281.colophon.iiif_manifest`.

## Verbatim YEK fields

| Field | Verbatim Value |
|---|---|
| Title | `Dîvân / ديوان` |
| Library | Nuruosmaniye Kütüphanesi |
| Collection | Nuruosmaniye |
| Shelfmark | **04281** |
| Language | Farsça (Persian) |
| Subject | 891.5 / İran edebiyatı (Iranian literature) |
| Material type | Yazma eser (manuscript) |
| Folio count | 326 yk. (326 folios) |
| Dimensions | 237 × 135-160 × 65 mm |
| Script | Arap harfli: Nestalik |
| Date AH | **1088** (= 1677/78 CE) |
| Reference | **Muhammed Muîn, Ferheng-i Fârsî, V.961-962** |
| Has digitised images | false |

## Verbatim DECORATION DATA

> **Paper**: "Aharlı, ince, su yolu dikey, krem renk."
> *Translation*: Sized [aharlı], thin, water-mark vertical [vertical chain-lines = European laid paper or similar laid format], cream colour.

> **Binding**: "Mukavva üzeri vişne renk meşin kaplı miklebli yaldız gömme şemseli, salbekli, zencerekli cetvelli şemse cilt."
> *Translation*: Pasteboard core, covered with cherry-red leather, miklebli (with envelope flap), gilt-tooled gömme (sunken/recessed) şemse (central medallion), salbek (pendant lobes), zencerek (chain-pattern) cetvel (border ruling), shemse cilt (medallion binding).

> **Seals**: "Mühür: III. Osman tuğralı vakıf mührü, 1a sayfasında. Mühür: İbrahim Hanif, 1a sayfasında. Vakıf Notları: 1a sayfasında."
> *Translation*: Seal of Osman III's tughralı waqf, on f. 1a. Seal of Ibrahim Hanif, on f. 1a. Waqf notes on f. 1a.

> **Decoration field**: NULL (no illumination/headpiece data captured by YEK cataloguer).

## Attribution status

The YEK cataloguer cited Mu'in's *Ferheng-i Fârsī* vol V (the proper-name supplement / *aʻlām*), pp. 961-962. Mu'in's vol V entry on **Ḥaqīqī** is the locus where Cihanşah Karakoyunlu's pen-name is registered. The codex is therefore **plausibly** identified as a Hakiki Divan, but the catalogue does NOT explicitly print "Hakikî" or "Cihanşah" anywhere in the title/author fields. The attribution rests entirely on the reference-citation chain.

**Caveats**:

1. Date (1088 AH = 1677/78 CE) is a 17th-century OTTOMAN copy: 189/190 years after BL Or 9493. Not a Karakoyunlu-period codex.
2. 326 folios is much larger than any other Hakîkî witness (BL Or 9493 = 85; Mat 965 = 54; Süleymaniye Fatih 3808 = 107; Tehran 8198 = 133; DTCF 2221 = 26). This raises the question whether it is a Hakîkî divan PLUS additional content (mecmua), a different "Hakikî" homonym (e.g. Yusuf Hakîkî, the Aksaray Sufi who has a 326-folio divan in some recensions), or fully the divan with massive scholia.
3. **Mu'in's V.961-962 entries on Hakîkî are MULTIPLE: Yusuf Hakîkî, Cihanşah Hakîkî, and other namesakes share contiguous lexicon entries.** Without a Mu'in V text-check, the reference alone cannot disambiguate which Hakîkî this codex represents.
4. The 7-way pen-name disambiguation (per the witness register) is highly relevant here. Yusuf Hakîkî is the more probable identification for a 326-folio divan in 1677 Ottoman copyings, since Yusuf Hakîkî was MUCH more widely copied in Ottoman scriptoria than Cihanşah Hakîkî.

## Codicological significance

The final register no longer treats this codex as a Cihanşah Hakîkî witness. Its codicological value for the witness census is therefore audit-only:

- It records the type of rich YEK decoration data that can be recovered for misattributed candidates.
- It is a 17th-century Ottoman copy with aharlı paper and a gilt-tooled shemse binding.
- Its decoration data is not evidence for the Cihanşah corpus and is not useful as a Karakoyunlu/Aq-Qoyunlu comparator for BL Or 9493's paper question.

**Decoration profile**: classic 17th-century Ottoman shemse cilt (medallion binding) with sized cream paper. Codicologically irrelevant to the verified Cihanşah corpus after the colophon-based rejection.

## recommendation

If further audit confirmation is desired:
1. Collate the underlying text against Yusuf Hakiki editions to identify the non-Cihanşah author more precisely.
2. Recheck f. 1a-2b through YEK/IIIF or a reading-room visit only if the binding/seal evidence is needed for a separate Ottoman codicology question.
3. Do not promote this entry without new primary evidence that overcomes the colophon-based scribal-homonym rejection.

## Witness register implication

Final register status: `rejected`. The terminal rationale is in `data/witness_register.json` under `nuruosmaniye_04281`: the colophon names the scribe as Jahanshah b. Baba Gejelu, not the author, and the codex fails the Cihanşah attribution test on size, genre, date/context, and authorial silence.
