# Personalized Learning Agent

A lab project exploring how an AI agent can adapt teaching to individual students and help them describe barriers to learning.

## Project status

Planning scaffold. This repository contains a project brief, an agent prompt, a fictional example, and an evaluation plan. It does not yet include a running application or an AI model integration.

## Goal

Adapt explanations, practice difficulty, pacing, and feedback using demonstrated understanding and voluntary student feedback. Explore reasons studying feels difficult without assuming that disengagement indicates a mental health condition.

## Proposed first prototype

- One subject: introductory mathematics.
- Fictional student profiles for initial development.
- A short baseline quiz and optional learning-barrier check-in.
- One personalized lesson with guided practice.
- A follow-up quiz and feedback question to inform the next lesson.
- No permanent learner-type labels or mental health diagnoses.

Age group, curriculum, model provider, and interface are still to be selected.

## Learning loop

1. Ask what the student wants to learn and what feels difficult.
2. Check relevant prerequisite knowledge with a few questions.
3. Select an explanation and task size, explaining the choice briefly.
4. Teach, offer hints, and let the student attempt the task.
5. Check understanding with a new question rather than repeating the example.
6. Update the next lesson using performance and student feedback.

## Support boundaries

The agent offers educational support. It does not diagnose or treat mental health conditions. Students can skip personal questions. When concerns exceed educational support, it should offer a route to an appropriate human, such as a teacher, counselor, or trusted adult. It must not claim to have contacted anyone unless an authorized, implemented workflow has actually done so.

Use only fictional data during this initial lab. Do not commit student identities, private conversations, health information, or API keys. Before use with real students, define consent, access, retention, deletion, human oversight, and age-appropriate support procedures.

## Repository contents

- `docs/project-plan.md`: scope, architecture, milestones, and evaluation.
- `prompts/tutor.md`: draft behavioral instructions for the future agent.
- `examples/student-profile.json`: explicitly fictional input example.

## Next steps

1. Confirm the target age group and curriculum.
2. Implement a simple lesson-session interface and model adapter.
3. Add curriculum-grounded content and answer checking.
4. Evaluate fictional sessions before considering a supervised pilot.

No license has been selected yet.
