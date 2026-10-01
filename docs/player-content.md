# Player content standard

## Reader and goal

Write for a person solving the exercise in the pwnden website. The learning loop is: understand the situation and objective, inspect provided material or open the target service, experiment in the prepared workspace, submit an answer, then use hints and explanations to learn from the result. Content is authored in challenges; platform presents it and supplies the controls.

A player can complete the exercise and read its explanation using the browser workspace and its terminal. Docker is prepared before entering this flow. Players need no host language SDK, repository layout knowledge or maintainer CLI. Downloads are an optional convenience. Text materials open in the workspace; binary and large materials are already accessible in the terminal.

## Brief

Provide the following information in concise, natural prose. Use sections only where they improve reading.

Describe the intended objective and the actions the player can take directly. Each sentence adds relevant context, a required action, or a success condition. Keep solving strategy in progressive hints. Use the website's section headings and controls as the navigation, so the brief stays focused on the exercise.

- A concrete scenario that explains what the player has and why the target matters.
- One explicit objective and an observable success condition.
- Supplied resources and legitimate access, including credentials when appropriate.
- Enough prerequisite context to begin; explain unfamiliar concepts needed for the first action.
- Starting actions tied to actual UI labels: 자료 열기, 문제 실행, 문제 열기, 터미널 연결 and 플래그 제출.
- The answer format and any instance-specific behavior, such as keys changing after restart.

The panel already displays title and category. Start the brief with the scenario or objective, preserving a useful heading hierarchy rather than repeating the title. Keep the brief free of the answer. Show language names, protocols and commands when understanding them is part of the exercise. When a command is useful, identify the prepared website terminal as its execution location. Explain expected output. Author setup, Go runner commands, image digests, Compose internals, host architecture and automated verification details belong in maintainer documentation.

## Hints

Use `##` for primary content headings and `###` for subsections. Consumers place brief headings beneath the panel title and walkthrough headings beneath the learning section.

Declare Markdown files in `[content].hints`, in increasing specificity. Early hints suggest an observation or way of thinking. Later hints connect the observation to a concrete next step. Each should help the player move forward without requiring source checkout navigation. A hint may intentionally reveal a partial result late in the sequence. The UI lets players choose how many steps to open.

## Walkthrough

Every problem supplies `[content].walkthrough`. Explain the key insight, observations, intermediate reasoning, exact reproducible steps, how the result is confirmed and what the player learned. A final answer alone is insufficient. Use the browser and prepared terminal as the execution context. Include a fixed answer where appropriate; for generated answers explain how to retrieve the current instance's value. Give defensive lessons where they explain the vulnerability. The website labels the walkthrough as containing answers and opens it on explicit request.

## Author review

Review the rendered problem as a first-time solver, independently of whether `solve.command` passes.

- Can I state the goal and tell when I have succeeded?
- Can I start using only the supplied context and visible controls?
- Can I inspect each required resource and perform every exercise step in the prepared environment?
- Are credentials, submission format, expected output and restart effects clear where relevant?
- Do hints progress from direction to specific help? Is the answer absent from the initial brief?
- Does the walkthrough explain why the approach works and reproduce the result?
- Does a failure to load content offer a retry, rather than sending players into repository files?

The format validator checks declarations, distinct regular Markdown files, repository containment, UTF-8, the 1 MiB limit and hint count. These checks cannot prove pedagogical quality. Author review supplies that judgment; runtime and API/UI tests verify execution and presentation.
