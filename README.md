# Personalized Learning Agent

## A collaborative research project in adaptive education

A research project for a professor and three students investigating how AI teaching can adapt to demonstrated knowledge, learning goals, and voluntarily reported learning barriers.

**Status: early prototype.** This repository contains project designs, a draft tutor prompt, fictional examples, and a deterministic command-line demonstrator (no language model yet). There is no validated intervention or experimental result. Roles and schedules below are proposals for team agreement.

## Research question

Does adapting an AI tutor to both prior knowledge and self-reported learning barriers improve understanding compared with a tutor using the same content without those adaptations?

Explore knowledge gaps, unclear explanations, lack of relevance, task overload, and confidence concerns. Mental health diagnosis and treatment are outside the tutor's scope. Concerns beyond educational support should have a reviewed route to human help.

## Planned platform

| Module | Intended capability | Status |
| --- | --- | --- |
| Student check-in | Goals, optional barriers, accessibility preferences, baseline quiz | Specified |
| Learner model | Topic-level evidence and uncertainty | Planned |
| Adaptive planner | Select explanation, pace, hints, and practice | Planned |
| Grounded tutor | Teach using approved curriculum and checked examples | Draft prompt |
| Assessment engine | Equivalent quizzes and retention checks | Planned |
| Research instrumentation | Versioned conditions and minimal consented events | Specified |
| Teacher/researcher view | Review educational progress summaries and errors | Later phase |
| Human support pathway | Reviewed support options and urgent procedures | Design required |

## Project guide

- [Research proposal](RESEARCH.md): questions, comparison design, and literature review.
- [Architecture](ARCHITECTURE.md): modules, learning loop, and implementation sequence.
- [Roadmap](ROADMAP.md): proposed 12-week phases and completion criteria.
- [Team handbook](TEAM.md): responsibilities, meetings, and decisions.
- [Evaluation protocol](EVALUATION.md): outcomes, controls, and review scenarios.
- [Data and support policy](DATA_AND_SUPPORT.md): collection limits and human oversight.
- [Contribution guide](CONTRIBUTING.md): issues, reviews, and reproducibility.
- [Work backlog](BACKLOG.md): concrete tasks for the team to claim.
- [Draft tutor prompt](prompts/tutor.md) and [fictional student profile](examples/student-profile.json).
- [Original planning notes](docs/project-plan.md): early concept; the research documents above define the expanded plan.

## First demonstrator

Build one complete tutoring session for equivalent fractions. Use three fictional scenarios: a prerequisite gap, a relevance concern, and a need for smaller steps. Explain the teaching choice, offer a lesson, check understanding with a new question, and revise the next step. Allow students to skip personal questions and override the teaching format.

Begin with a deterministic planner and fixed curriculum, then add a language-model adapter. Keep adaptation rules separate from generated wording so the research comparison remains reproducible.

## Running the demonstrator

Requires Python 3.10+; no runtime dependencies.

```bash
pip install -e ".[dev]"      # or: export PYTHONPATH=src
python -m pla.session examples/scenarios/pace.json
python -m pla.session examples/scenarios/pace.json --condition fixed --record
pytest
```

| Path | Contents |
| --- | --- |
| `src/pla/contracts.py` | Typed session contract (evidence, self-reported barrier, plan, research record) |
| `src/pla/learner_model.py` | Session-only topic state with uncertainty and provenance |
| `src/pla/planner.py` | Rule-based planner: override > prerequisite gap > barrier > standard |
| `src/pla/session.py` | Scripted session runner and CLI |
| `src/pla/llm.py` | Provider-independent model adapter (Anthropic, standard library only) |
| `src/pla/tutor.py` | Grounded tutor: model rewording with validation and fallback |
| `curriculum/fractions-equivalence.json` | Draft lessons and items (needs teacher review) |
| `examples/scenarios/` | Fictional students: prerequisite gap, relevance, pace, override |

### Optional: model-written wording

```bash
export ANTHROPIC_API_KEY=...   # server-side only; never commit it
python -m pla.session examples/scenarios/pace.json --model anthropic --record
```

The planner still decides the strategy; the model only rewords the approved lesson steps (`src/pla/tutor.py`). Output that is empty, too long, or contains fractions not in the approved text is discarded, and the approved text is shown instead. Errors and timeouts fall back the same way, after bounded retries. Model ID, prompt version and every fallback are logged in the research record. Student free text is never sent to the model.

All three comparison conditions (`fixed`, `knowledge_only`, `knowledge_and_barrier`) share the same curriculum, so only the adaptation rules differ. The research record stores item IDs, correctness, strategies and reasons, but no free text.

## Longer-term scope

After evaluating the first prototype, expand topics, test accessibility options and retention, and explore teacher review tools. Multiple subjects, persistent profiles, and a real-student study require separate review gates. More features are not evidence of better learning.

## Open decisions

Target learners, curriculum, provider, budget, study approvals, sample size, licensing, and institutional ownership remain undecided. Literature review and efficacy testing have not been completed. Initial development uses fictional data only. Never commit student records or credentials to this public repository.

No license has been selected.
