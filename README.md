# HPP-FS-Skills

Hydropower feasibility, bankability, investor decision support, and EPC bidding strategy skill for Kazakhstan and comparable Central Asian markets.

This repository packages a reusable AI-agent skill for evaluating hydropower projects (HPPs) from both an investor/developer perspective and an EPC contractor perspective. It is designed for feasibility studies, pre-FS reviews, auction preparation, market sounding, bankability assessment, and bid strategy.

## What This Skill Does

Use this skill when you need to assess a hydropower project such as a run-of-river, reservoir, pumped-storage, or cascade HPP.

It helps produce bank-grade outputs covering:

| Workstream | Coverage |
|---|---|
| Technical feasibility | Hydrology, P50/P75/P90 generation, dam type, tunnels, headworks, powerhouse, grid connection, geotechnical and seismic risk |
| E&S and permitting | EIA/ESIA, ecological flow, biodiversity, fish migration, sediment, land, resettlement, stakeholder engagement, water permits |
| Financial feasibility | CAPEX, OPEX, revenue stack, capacity payment, PPA/electricity tariff, NPV, IRR, equity IRR, DSCR, payback, LCOE |
| Kazakhstan market | Capacity market, single buyer, FSC/RFC, KOREM, KEGOC, auction structure, water and energy institutions |
| Risk analysis | Technical, hydrology, geological, climate, policy, FX, interest-rate, grid, permitting, E&S, and construction risks |
| Investor strategy | Bid/no-bid, due diligence, financing, bankability gaps, offtake and contract amendments |
| EPC strategy | Tender position, exclusions, GBR boundary, construction organization, local content, interface control, claims strategy |

## Repository Structure

```text
hpp-fs-skills/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   |-- default-assumptions.md
|   |-- epc-strategy.md
|   |-- hpp-fs-framework.md
|   `-- kazakhstan-bankability.md
`-- scripts/
    `-- hpp_financial_model.py
```

## Core Skill Files

| File | Purpose |
|---|---|
| `SKILL.md` | Main trigger, role definition, required output structure, workflow, and quantitative standards |
| `references/hpp-fs-framework.md` | Full HPP feasibility study framework |
| `references/kazakhstan-bankability.md` | Kazakhstan capacity-market and bankability checklist |
| `references/epc-strategy.md` | EPC contractor tender, risk, construction, and claims guidance |
| `references/default-assumptions.md` | Default Kazakhstan/Central Asia assumptions when project data is missing |
| `scripts/hpp_financial_model.py` | Runnable preliminary financial model for HPP screening |

## Quick Start in Codex

Install this folder into your Codex skills directory:

```powershell
Copy-Item -Path ".\hpp-fs-skills" -Destination "$env:USERPROFILE\.codex\skills\hpp-fs-skills" -Recurse -Force
```

Then invoke it in Codex:

```text
Use $hpp-fs-skills to evaluate this Kazakhstan hydropower project from investor and EPC perspectives.
```

For best results, attach or paste any available project data:

- Pre-FS or FS report
- Hydrology data or flow duration curve
- Layout drawings or technical memorandum
- CAPEX/OPEX estimate
- Power evacuation study
- EIA/ESIA screening
- Draft capacity agreement, PPA, EPC contract, or auction documents

## Financial Model

Run the included financial model with project-specific assumptions:

```powershell
python .\scripts\hpp_financial_model.py `
  --capacity-mw 171.66 `
  --generation-gwh 563.4 `
  --capex-usd 480000000 `
  --capacity-tariff-kzt-mw-month 15000000 `
  --energy-tariff-usd-mwh 35 `
  --csv-out model_output.csv
```

The model outputs capacity factor, annual revenues, project NPV, project IRR, equity IRR, minimum DSCR, and LCOE.

## Configuration on Major AI Models

Different AI platforms use different names for the same concept: system prompt, developer message, project instructions, custom instructions, knowledge base, files, tools, or actions. The portable configuration pattern is:

1. Put the content of `SKILL.md` into the model's system/developer/project instructions.
2. Upload the files in `references/` as project knowledge or retrieval documents.
3. Make `scripts/hpp_financial_model.py` available as an executable tool, code interpreter file, notebook helper, or local script.
4. Ask the model to follow the six-part HPP output structure and to prioritize user-provided project data over default assumptions.

### OpenAI ChatGPT / GPTs

Recommended setup:

- Put `SKILL.md` into the GPT Instructions field.
- Upload all `references/*.md` files as Knowledge files.
- Upload `scripts/hpp_financial_model.py` as a file for Advanced Data Analysis / code execution workflows.
- Use the default starter prompt:

```text
Use HPP-FS-Skills to evaluate the attached hydropower project for Kazakhstan bankability, investor decision-making, and EPC bidding strategy.
```

### OpenAI API

Use `SKILL.md` as a developer message and inject relevant reference files based on the task.

Minimal pattern:

```python
from openai import OpenAI

client = OpenAI()

skill = open("SKILL.md", encoding="utf-8").read()
framework = open("references/hpp-fs-framework.md", encoding="utf-8").read()
bankability = open("references/kazakhstan-bankability.md", encoding="utf-8").read()

response = client.responses.create(
    model="gpt-5",
    input=[
        {"role": "developer", "content": skill},
        {"role": "developer", "content": framework + "\n\n" + bankability},
        {"role": "user", "content": "Assess this 100 MW Kazakhstan reservoir HPP for investors and EPC bidders."}
    ],
)

print(response.output_text)
```

### Anthropic Claude

Recommended setup:

- Put `SKILL.md` in Project Instructions or the system prompt.
- Add `references/*.md` to Project Knowledge.
- Attach project files directly to the chat.
- Ask Claude to read only the relevant reference files before producing the assessment.

Suggested instruction:

```text
Follow the HPP-FS-Skills workflow. Use project data first, label assumptions, and always provide investor/developer and EPC contractor strategy sections.
```

### Google Gemini

Recommended setup:

- Put `SKILL.md` in system instructions or Gems custom instructions.
- Upload `references/*.md` as context files where supported.
- Use the financial script locally or in a notebook if code execution is available.

Suggested prompt:

```text
Using the HPP-FS-Skills framework and the attached project documents, prepare a bankability assessment of the HPP, including Kazakhstan market risks and EPC tender strategy.
```

### Microsoft Copilot / Azure OpenAI

Recommended setup:

- Use `SKILL.md` as the system/developer instruction in your agent or assistant.
- Index `references/*.md` in the agent knowledge base, SharePoint, Azure AI Search, or another retrieval layer.
- Expose `hpp_financial_model.py` through a function, notebook, or backend service if repeatable calculations are required.

### Mistral, Llama, Qwen, DeepSeek, and Other Local or Open-Weight Models

Recommended setup:

- Put `SKILL.md` at the top of the system prompt.
- Add only the relevant reference file to the prompt to preserve context.
- For longer reports, use retrieval-augmented generation over the `references/` directory.
- Run `scripts/hpp_financial_model.py` locally and feed the model the resulting metrics table.

Example local prompt layout:

```text
[SYSTEM]
<paste SKILL.md>

[REFERENCE]
<paste references/kazakhstan-bankability.md if Kazakhstan market terms are relevant>

[USER]
Evaluate the attached Tentek River cascade HPP for bankability and EPC participation.
```

## Recommended User Prompts

```text
Use $hpp-fs-skills to evaluate this Kazakhstan HPP from both investor and EPC perspectives.
```

```text
Use $hpp-fs-skills to build a bankability red-flag matrix for the attached capacity agreement.
```

```text
Use $hpp-fs-skills to generate a financial model and sensitivity analysis for a 100 MW reservoir HPP.
```

```text
Use $hpp-fs-skills to prepare an EPC bid strategy, risk exclusions, and claims register for this hydropower tender.
```

## Output Standard

Substantive assessments should include:

1. Project overview and technical feasibility
2. Environmental, social, and permitting feasibility
3. Economic and financial feasibility
4. Legal, policy, institutional, and market feasibility
5. Risk assessment and mitigation
6. Dual-track participation strategy

All assumptions must be clearly labeled. When project data is missing, use the default assumptions file only as a preliminary screening basis.

## License

No license is currently specified. Add a license before public commercial reuse if required.
