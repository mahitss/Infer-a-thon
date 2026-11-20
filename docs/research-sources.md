# Research Sources & Verification Notes

Reviewed 2026-11-19; supplemental source verification 2026-11-21. Links are public sources used for the preliminary discovery package. See the verification log below for access status and limitations.

## SIE
- SIE overview and four primitives: https://superlinked.com/docs
- SIE model catalogue (includes document OCR and speech-to-text task families): https://superlinked.com/models
- Speech-to-text task details and example: https://superlinked.com/speech-to-text
- SIE integration options: https://superlinked.com/docs/integrations

SIE documentation describes Encode, Score, Extract and Generate. Its model catalogue lists document-to-Markdown/OCR and speech-to-text models as task families. These are model capabilities, not additional top-level SIE primitives. SIE is self-hostable; Serverless publishes usage prices. Verify exact model availability and local hardware fit before selection.

Verified 2026-11-21 from `https://superlinked.com/about`: Superlinked states that new accounts receive **$20 in free credits and need no card**, with **usage billed after those credits are consumed**. This is a possible one-time, eligibility-dependent experiment allowance, **not a guaranteed permanent free tier**, and no paid service is authorized for this project. The same page describes SIE Local/Cluster as open source and free under **Apache 2.0**; individual model licenses still require separate checking. `https://superlinked.com/docs` was accessible and confirms the four primitives.

## Competitive products
- Redrawn Procurement: https://redrawn.ai/solutions/procurement
- Kinnow Contract Intelligence: https://kinnow.ai/agents/contract-intelligence.html
- Riffit: https://www.riffit.in/
- TextMine invoice dispute evidence: https://textmine.com/learn/how-to-build-invoice-dispute-evidence-packs
- Uttos: https://uttos.in/
- Munshi: https://askmunshi.ai/
- Tagaada: https://tagaada.com/
- Kendraa (dedicated WhatsApp investigation page): https://kendraa.co.in/whatsapp-investigations/
- Kendraa (general site): https://kendraa.co.in/
- BinaxPay: https://www.binaxpay.nl/connected-industry/trade-disputes-claims
- Name collision checks: https://saudasetu.com/ and https://www.techindium.com/

## Academic prior art (distinct topics)
- **IJCAI 2025 — one-to-many agent negotiation and interdependency:** Florijn, Yolum & Baarslag, *A Survey on One-To-Many Negotiation: A Taxonomy of Interdependency*, IJCAI 2025, pp. 10436–10444, DOI 10.24963/ijcai.2025/1159: https://ijcai.org/proceedings/2025/1159
- **Germesin & Wilson 2009 — agreement/disagreement detection and addressee identification in multiparty conversation:** https://www.dfki.de/fileadmin/user_upload/import/4513_germesin_agree_icmi09-7.pdf
- **Purver et al. 2007 — action-item proposal, discussion and commitment detection in multiparty dialogue:** *Detecting and Summarizing Action Items in Multi-Party Dialogue*, SIGDIAL 2007: https://aclanthology.org/2007.sigdial-1.pdf

These are **related prior art**, not direct demonstrations of the proposed asynchronous B2B transaction-reconstruction workflow. They inform the risk that agreement/action detection is not itself novel; they do not establish novelty or a market gap for this product.

## Indian MSME payment context
- Rajya Sabha Standing Committee on Industry, Report No. 333 (March 2026): https://sansad.in/getFile/rsnew/Committee_site/Committee_File/ReportFile/17/215/333_2026_3_14.pdf?source=rajyasabha
- MSME Samadhaan dashboard: https://dashboard.msme.gov.in/msme_samadhaan.aspx

The committee report gives 2,56,892 Samadhaan applications involving ₹55,244.31 crore as at 31 December 2025 and cites an Economic Survey 2025–26 estimate of ~₹8.1 lakh crore locked in delayed MSME payments. These figures establish scale of the delayed-payment issue, not demand for this specific solution or causation by agreement mismatches.

## Limits

This is a targeted public-web scan, not exhaustive competitor diligence, private customer research, product testing, legal clearance, trademark clearance, or proof of global uniqueness. Record competitor overlap honestly in all submissions.

## Supplemental verification log (2026-11-21)

| Source | Status | What was checked |
|---|---|---|
| https://kendraa.co.in/whatsapp-investigations/ | HTTP 200 | Dedicated WhatsApp-investigation interface; terms `WhatsApp`, `chat`, `investigation`, `forensic`, `provenance` present. Adjacent forensic/provenance product, not classified as direct competitor without further evidence. |
| https://superlinked.com/about | HTTP 200 | $20 new-account credits without card, billing after credits, SIE open source under Apache 2.0. |
| https://superlinked.com/docs | HTTP 200 | SIE Encode/Score/Extract/Generate primitives and self-hosting references. |
| https://ijcai.org/proceedings/2025/1159 | HTTP 200 | Survey title, 2025 IJCAI, DOI 10.24963/ijcai.2025/1159. |
| https://aclanthology.org/2007.sigdial-1.pdf / landing page | HTTP 200 | Purver et al. 2007 action-item paper confirmed in SIGDIAL 2007 proceedings. |
| https://www.dfki.de/fileadmin/user_upload/import/4513_germesin_agree_icmi09-7.pdf | **HTTP 403 (Cloudflare)** | Full text NOT re-verified on 2026-11-21; citation metadata retained from the earlier scan. |

Limitations: verification was page accessibility plus content-keyword confirmation, not hands-on product testing, license review, or independent replication of research results. Public product-page descriptions are claims, not independently tested functionality.
