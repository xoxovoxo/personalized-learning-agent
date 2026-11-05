# Personalized Learning Agent

## A collaborative research project in adaptive education

A research project for a professor and three students investigating how AI teaching can adapt to demonstrated knowledge, learning goals, and voluntarily reported learning barriers.

**Status: research and implementation planning.** This repository contains project designs, a draft tutor prompt, and fictional examples. There is no running application, validated intervention, or experimental result yet. Roles and schedules below are proposals for team agreement.

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

## Longer-term scope

After evaluating the first prototype, expand topics, test accessibility options and retention, and explore teacher review tools. Multiple subjects, persistent profiles, and a real-student study require separate review gates. More features are not evidence of better learning.

## Open decisions

Target learners, curriculum, provider, budget, study approvals, sample size, licensing, and institutional ownership remain undecided. Literature review and efficacy testing have not been completed. Initial development uses fictional data only. Never commit student records or credentials to this public repository.

No license has been selected.
