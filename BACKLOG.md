# Team work backlog

All tasks are unassigned and not started. This version-controlled backlog does not imply a GitHub Projects board has been created.

| ID | Priority | Work package | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- |
| R01 | P0 | Research scope | Learners, topic, question, comparator, exclusions reviewed | — |
| R02 | P0 | Literature review | Search log, evidence matrix, supported gap statement | R01 |
| R03 | P0 | Team charter | Owners, reviewers, meeting cadence, budget, licensing decisions | R01 |
| C01 | P0 | Curriculum | Objectives, examples, misconceptions, reviewed answers | R01 |
| C02 | P0 | Assessment bank | Equivalent pre/post and transfer items with rubrics | C01 |
| E01 | P0 | Data/support review | Collection boundaries, access plan, support owner, review requirements | R01 |
| S01 | P1 | Session runner | Check-in, practice, feedback, reset using fictional data | C01, E01 |
| S02 | P1 | Learner model | Evidence provenance and uncertainty; no permanent labels | S01, C02 |
| S03 | P1 | Planner | Three scenarios plus skip and override behavior | S02 |
| S04 | P1 | Model adapter | Isolated provider, server credentials, timeout/fallback | S01 |
| S05 | P1 | Grounded tutor | Approved sources, checked answers, uncertainty handling | S03, S04 |
| S06 | P1 | Accessible interface | Keyboard use, readable feedback, optional questions, reset | S01 |
| X01 | P1 | Experiment modes | Reproducible fixed, knowledge-only, and barrier-informed modes | S05 |
| X02 | P1 | Evaluation harness | Scenario suite, failures, versions, run instructions | X01 |
| X03 | P1 | Analysis protocol | Outcomes, scoring, sample-size rationale, uncertainty reporting | R02, C02 |
| X04 | P2 | Supervised pilot | Approvals obtained; protocol followed; deviations recorded | E01, X02, X03 |
| D01 | P2 | Report and demo | Methods, findings/feasibility, limitations, reproducibility | X02, X03 |
| D02 | P3 | Teacher review view | Minimal educational summaries, reviewed access | D01, E01 |

P0: decisions/content before implementation. P1: core prototype. P2: evaluation/report. P3: stretch work.

## First sprint proposal

Student A drafts adaptation scenarios and learner-state contracts. Student B drafts objectives and the literature search plan. Student C sketches the interface and event schema. The professor reviews scope and feasibility. These assignments require team agreement.
