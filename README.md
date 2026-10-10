# Metal powder RFQ handoff checklist

A local Python utility and editable CSV/JSON templates for spotting incomplete handoffs between engineering, purchasing and a metal powder supplier. Python 3.10+; standard library only; no account, network calls or data upload.

The checker asks whether the request records a requirement, a supporting reference and its review status. **It does not decide whether a powder is suitable, certify a lot, verify a supplier, or approve an order.**

## Start with the template

1. Download this repository and copy `rfq-template.csv` or `rfq-template.json` outside the public repository.
2. Replace each instruction with your project requirement. Keep unresolved items `pending`.
3. Use `confirmed` only when the requirement and evidence reference have been recorded. Use `not_applicable` only with a reason in `notes`.
4. Run locally:

```sh
python rfq_check.py rfq-template.json
python rfq_check.py rfq-template.csv --json
python -m unittest -v
```

The unedited template intentionally returns 11 review items and exit code `1`. After the fields are recorded, exit code `0` means **handoff completeness only**. Invalid files return `2`. Machine-readable output always reports `material_accepted: false`.

## The eleven handoff fields

| Field | Record or resolve before comparison |
| --- | --- |
| Alloy and specification | Exact grade, specification revision or agreed composition table; do not assume similar designations are interchangeable. |
| Process and machine | Intended process, machine and trial/production context; identify the owner of process qualification. |
| Particle-size distribution | Required range or distribution limits, units, method and reporting basis; nominal cuts alone can hide differences. |
| Chemistry and interstitials | Alloy-specific acceptance limits, units and analytical methods for the controlled elements. |
| Flow and density | Required metrics, test methods, conditions and acceptance basis; distinguish apparent, tap and material density. |
| Powder condition | Virgin, blended or reused condition and the applicable history/change controls. |
| Lot traceability | Lot identifiers, container identification and the relationship between the sample and shipment. |
| Required documents | Purchase specification, TDS, lot COA and SDS as applicable; each answers a different question. |
| Sampling and acceptance | Sampling responsibility, test stage, acceptance owner and deviation workflow. |
| Quantity and packaging | Trial and production amounts, pack size, container and storage requirements. |
| Delivery requirements | Destination, requested timing and commercial delivery basis; resolve freight separately where necessary. |

## Example: a field can contain text and still be unresolved

```json
{
  "id": "chemistry_and_interstitials",
  "status": "pending",
  "requirement": "Oxygen acceptance limit to be confirmed by the buyer",
  "evidence": "",
  "notes": "Engineering owner: confirm alloy, numerical limit, units and test method before quotation comparison."
}
```

Do not change the status to `confirmed` just to silence the checker. A typical TDS number is not a measured batch result. Record the controlling specification reference and the agreed evidence needed at the relevant stage.

## What the checks cover

- Missing, duplicate or unknown field identifiers.
- Missing or invalid status values.
- Pending fields, even if the remaining text is populated.
- Blank requirements/evidence and common unresolved placeholders in confirmed fields.
- Missing rationale for a not-applicable decision.

The checks cannot detect every placeholder, resolve contradictory prose, authenticate documents, validate measurement units or methods, or judge numerical limits. A reference can be mistyped or misleading and still pass. Review the actual evidence separately. This is intentionally a small completeness tool, not a material qualification engine.

## Procurement background and disclosure

The field design accompanies the [Metal Powder Specification and COA Guide](https://metal3dpowder.com/posts/Alloys/metal-powder-specification-guide-psd-oxygen-flowability/). The guide explains the distinction between purchase requirements, product data and lot evidence, and why PSD, oxygen, flow and density need a stated measurement context.

Published for Metal 3D Powder, operated by SZCOMO — Suzhou Como Precision Materials Co., Ltd., which provides powder sourcing and supply coordination. This repository is an educational workflow resource; it makes no claim of factory ownership or universal powder qualification. Code and documentation were prepared with AI assistance.

Keep supplier quotations, customer drawings, personal contact details and real lot documents out of public issues and commits. The tool runs locally and does not require those documents to be uploaded.

## License

MIT. Contributions should improve the tool or clarify the workflow; do not submit promotional links or confidential RFQ data.
