# Disambiguation note: Teece 2016 Appendix B entry #26

## Issue

Teece 2016 (Denise-Marie Teece, "Vessels of Verse, Ships of Song: Persian Anthologies of the Qara Quyunlu and Aq Quyunlu Period," NYU IFA PhD dissertation) Appendix B "Manuscripts Associated with Pir Budaq Qara Quyunlu" entry #26 records:

> Fatih 4054 | Kulliyat of Imad al-Din (d. 1371) | date TBD | Istanbul, Suleymaniye Mosque Library

The "date TBD" placeholder is the operative ambiguity. The witness-census survey for the diwan of Jahanshah Qaraqoyunlu (Hakîkî) initially treated this entry as a Pir-Budaq-era manuscript (governorship of Shiraz 1452 to 1459, governorship of Baghdad 1460 to 1466). A YEK precision-search resolution was needed.

## Verification

Two independent YEK queries were run against portal.yek.gov.tr using authenticated YEK catalogue access:

1. Precision search: `term="04054"` in `yer_numarasi` AND `term="Fatih"` in `koleksiyon_adi`. Returned 7 component records (YEK ids 242536, 242537, 242538, 242539, 242540, 242541, 242542) corresponding to shelfmarks 04054-001 through 04054-007.
2. Detail extraction on all 7 component records. Uniform metadata across components: `date_ah = 0898`, dimensions 340 by 172 mm with text block 150 by 82 mm, 21 lines per page, Arap harfli-Talik script, Persian language, Süleymaniye Kütüphanesi / Fatih collection.

Date 898 AH converts to 1492-1493 CE.

## Resolution

Süleymaniye Fatih 04054 is a 400-folio multi-text composite of the Kulliyat of Imad al-Din Faqih Kermani (d. 1371) dated 898 AH / 1492-1493 CE. It postdates Pir Budaq Qaraqoyunlu's death in 871 AH / 1466 CE by 26 years. It is not a Pir-Budaq-era commission and was therefore mis-classified in Teece Appendix B once the colophon date is consulted.

Teece's Pir-Budaq-era Imad-i Faqih Kulliyat attribution applies instead to TIEM 02030 (Türk ve İslam Eserleri Müzesi, shelfmark 02030), which YEK precision-resolves with `date_ah = 04 Zilhicce 863` (1459 CE). TIEM 02030 contains the same Penc Genc + Divan structure (Tarikatname, Safaname, Husnname, Sohbetname, Muhabbetname, Dehname, Zeyl-i Dehname, Divan) and falls within Pir Budaq's governorship years (Fars / Shiraz 1452 to 1459 then Iraq / Baghdad 1460 to 1466). The 4 Zilhicce 863 date converts to 1 October 1459 CE, at the Shiraz-to-Baghdad transition.

## Implication for the witness census

Neither manuscript is a Hakîkî witness. Both are single-author commissions of Imad-i Faqih Kermani's 14th-century Kulliyat and cannot contain Cihanşah-era ghazals. The disambiguation is therefore zero-impact on the witness register itself.

For a future future scope "Cihanşah-era Qaraqoyunlu court corpus" context section, TIEM 02030 is the citable Pir-Budaq-era manuscript and Süleymaniye Fatih 04054 should be footnoted as a late-Turkmen / early-Safavid independent copy of the same text tradition rather than as a Pir Budaq library member.

## Sources

- Teece 2016 thesis pp. 294 to 296 (Appendix B), as extracted to `data/extracts/teece_2016_pir_budaq_corpus.json`.
- YEK precision search and detail records, as captured in `data/searches/probe_2026-05-12_teece_corpus_bodleian_yek.json` (probes B4 for TIEM 02030 and B5 for Süleymaniye Fatih 04054).
- YEK component detail pages: https://portal.yek.gov.tr/works/detail/242536 through https://portal.yek.gov.tr/works/detail/242542 (Süleymaniye Fatih 04054); https://portal.yek.gov.tr/works/detail/705037 and 705044 (TIEM 02030).
