# Player content standard

Use the [authoring standard](authoring-standard.md) to establish the security
learning objective, learner profile, prerequisite abilities and difficulty.
This page describes how to present that design to the player.

Use the [scenario writing framework](scenario-authoring.md) for the shared
voice: the player receives a hacking request, investigates it, and completes
the mission. The brief introduces the request, hints deliver additional
information, and the walkthrough reports the investigation and security lessons.
Keep the technical objective and required starting information precise.

## Reader and goal

Write for a person solving the exercise in the pwnden website. The learning loop is: understand the situation and objective, inspect provided material or open the target service, experiment in the prepared workspace, submit an answer, then use hints and explanations to learn from the result. Content is authored in challenges; platform presents it and supplies the controls.

A player can complete the exercise and read its explanation using the browser workspace and its terminal. Docker is prepared before entering this flow. Players need no host language SDK, repository layout knowledge or maintainer CLI. Downloads are an optional convenience. Text materials open in the workspace; binary and large materials are already accessible in the terminal.

## Brief

Provide the following information in natural prose with enough context for a
first-time reader. Use sections where they improve reading. Explain the target's
normal use, what prompted the investigation, why the requester supplies these
resources, and what the player can establish with them. Give this chain room to
develop across paragraphs; choose length by the information needed to understand
the situation.

Introduce each nickname through its relationship to the target. Define unfamiliar
features in terms of what users do with them. Explain the role of each file and
account before using it as a clue, and distinguish suspicions from established
facts. Keep investigation discoveries in progressive hints while supplying all
context needed to understand the assignment in the default brief.

Describe the intended objective and the actions the player can take directly. Each sentence adds relevant context, a required action, or a success condition. Keep solving strategy in progressive hints. Use the website's section headings and controls as the navigation, so the brief stays focused on the exercise.

- A concrete scenario that explains what the player has and why the target matters.
- One explicit objective and an observable success condition.
- Supplied resources and legitimate access, including credentials when appropriate.
- Enough prerequisite context to begin; explain unfamiliar concepts needed for the first action.
- Scoped prerequisite abilities and available learning references before the step
  that needs them. Supply the supporting explanation in the brief when a separate
  player-facing resource is unavailable.
- Starting actions within the target exercise: sign in with the supplied credentials, inspect a provided resource, or run a problem-specific command.
- The answer format and any instance-specific behavior, such as keys changing after restart.

The panel already displays title and category. Start the brief with the scenario or objective, preserving a useful heading hierarchy rather than repeating the title. Keep the brief free of the answer. Show language names, protocols and commands when understanding them is part of the exercise. When a command is useful, identify the prepared website terminal as its execution location. Explain expected output. Author setup, Go runner commands, image digests, Compose internals, host architecture and automated verification details belong in maintainer documentation.

The platform owns the common workspace workflow: preparing environments, attaching
the terminal, presenting declared files and services, downloads, hints and answer
submission. Shared usage guidance belongs in the platform's documentation and UI.
Write each brief and walkthrough around its exercise, so changes to workspace
button names or layout leave the problem content valid. Adding a problem requires
its manifest and resources; catalog discovery and available player tools follow
those declarations automatically.

## Hints

Use `##` for primary content headings and `###` for subsections. Consumers place brief headings beneath the panel title and walkthrough headings beneath the learning section.

Declare Markdown files in `[content].hints`, in increasing specificity. Early hints suggest an observation or way of thinking. Later hints connect the observation to a concrete next step. Each should help the player move forward without requiring source checkout navigation. A hint may intentionally reveal a partial result late in the sequence. The UI lets players choose how many steps to open.

## Walkthrough

Every problem supplies `[content].walkthrough`. Explain the key insight, observations, intermediate reasoning, exact reproducible steps, how the result is confirmed and what the player learned. A final answer alone is insufficient. Use the browser and prepared terminal as the execution context. Include a fixed answer where appropriate; for generated answers explain how to retrieve the current instance's value. Give defensive lessons where they explain the vulnerability. The website labels the walkthrough as containing answers and opens it on explicit request.

## Author review

Review the rendered problem as a first-time solver, independently of whether `solve.command` passes.

- Can I state the goal and tell when I have succeeded?
- Can I explain the target's normal use, the incident, the requester’s reason for
  seeking help, and how the supplied resources support my investigation?
- Can I start using only the supplied context and visible controls?
- Do the stated prerequisites match every step, including language features,
  calculations and tool operations? Does the exercise demonstrate its stated
  security learning objective?
- Can I inspect each required resource and perform every exercise step in the prepared environment?
- Are credentials, submission format, expected output and restart effects clear where relevant?
- Do hints progress from direction to specific help? Is the answer absent from the initial brief?
- Does the walkthrough explain why the approach works and reproduce the result?
- Does a failure to load content offer a retry, rather than sending players into repository files?

The format validator checks declarations, distinct regular Markdown files, repository containment, UTF-8, the 1 MiB limit and hint count. These checks cannot prove pedagogical quality. Author and learner review supply that judgment; runtime and API/UI tests verify execution and presentation. Record the evidence in `AUTHORING.md` using the [publication review](authoring-standard.md#review-before-publication).
