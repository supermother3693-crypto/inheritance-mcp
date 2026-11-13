# ChatGPT app submission pack

**Name:** Faraid – Hanafi Inheritance
**Short description:** Calculates Islamic inheritance shares (Hanafi fiqh), including multi-generation munasakha, and creates an Excel + printable naqsha.
**Long description:** Give the heirs (and optionally the estate, debts, funeral costs and bequest). The app applies Hanafi rules – fixed shares, asaba, exclusion, awl, radd, Umariyyatayn – with exact fractions, and for several deaths in a row (munasakha) returns one combined naqsha with a single jamia. Not a fatwa; confirm with a qualified mufti.
**Category:** Education / Lifestyle (Religion)
**Languages:** Urdu, English (naqsha in Urdu or Gujarati)
**MCP URL:** https://<service>.onrender.com/mcp  (no authentication)
**Privacy policy:** https://<service>.onrender.com/privacy
**Terms:** /terms   **Support page:** /support   **Logo:** /logo.png (512x512, original artwork)
**Support email:** set env var SUPPORT_EMAIL on Render (use a dedicated address, not a personal one)

## Tools (both read-only, closed-world, non-destructive, annotations set explicitly)
- calculate_inheritance – one deceased person
- calculate_munasakha – several deaths in a row, one naqsha

## Test prompts (no account needed)
1. "Wife, two sons, one daughter and mother survive. Estate 1,000,000. Make the naqsha."  -> jamia 120; wife 15, sons 34 each, daughter 17, mother 20
2. "Husband, two full sisters and mother survive." -> awl 8 (3/8, 1/2, 1/8)
3. "Wife, father, mother survive." -> Umariyyatayn: wife 1/4, mother 1/4 of remainder, father rest
4. "Zaid died leaving wife, two sons (Bakr, Umar) and three daughters. Bakr then died leaving wife, son Khalid, two daughters. Then Khalid died leaving wife, two sons, one daughter. Use munasakha." -> ONE naqsha, jamia 2560
5. Invalid: "husband and wife both" -> clear error message

## Checklist (owner)
- [ ] Always-on hosting (free Render sleeps)
- [ ] SUPPORT_EMAIL set
- [ ] OpenAI Platform: identity verification
- [ ] Screenshots of tests 1 and 4 (desktop and mobile) from ChatGPT
- [ ] Submit in the Platform dashboard, then fix any review comments
