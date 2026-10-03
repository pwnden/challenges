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

Player-visible problem titles are Korean. Name the actual scenario or task in
clear language. Repository directories, filenames and scenario slugs use English
identifiers; the manifest's `title` supplies the visible name independently.

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

### Plain, concrete language

Write Korean actions with an explicit actor and verb, following the
[scenario tone rules](scenario-authoring.md#어투). When the actor is unknown,
describe the observed state or what someone can do. Preserve the scenario's
facts when replacing passive phrasing, including requester dialogue and hints.

Name the actual account, document, file, permission or operation the player will
encounter. Introduce the target through familiar actions: signing in, reading a
document, searching a name, or comparing records. Use the same terms in requester
dialogue, the brief, target pages, hints and the walkthrough.

Explain a necessary technical term before asking the player to act on it. Start
with its everyday meaning and observable use, then name the term. For example,
"the browser stores a small name=value pair and sends it back to the site; this
is a cookie." A field such as `Resource` needs its meaning in this exercise:
"the name of the document this access rule applies to."

Each story element must correspond to an actual feature or supplied fact. State
what a secret value is used for in the scenario, who should be able to read it,
and why its disclosure matters. Keep code fields and inputs exact while explaining
them in ordinary language. Review the text with a reader who has only basic
browser skills: they should be able to describe the situation and their first
action in their own words.

Describe the intended objective and the actions the player can take directly. Each sentence adds relevant context, a required action, or a success condition. Keep solving strategy in progressive hints. Use the website's section headings and controls as the navigation, so the brief stays focused on the exercise.

- A concrete scenario that explains what the player has and why the target matters.
- One explicit objective and an observable success condition.
- Supplied resources and legitimate access, including credentials when appropriate.
- Enough prerequisite context to begin; explain unfamiliar concepts needed for the first action.
- Scoped prerequisite abilities and available learning references before the step
  that needs them. Supply the supporting explanation in the brief when a separate
  player-facing resource is unavailable.
- Starting access: supplied credentials, target address, scope and resource locations.
- The answer format and any instance-specific behavior, such as keys changing after restart.

The panel already displays title and category. Start the brief with the scenario or objective. The default brief supplies the situation, goal, scope, resources and submission target. Let players choose how to investigate. Put tool selection, command options, decisive fields, filtering rules and ordered solving steps in optional hints or the walkthrough. A supplied fact such as an export format may remain in the scenario; it does not need a second explanation or a matching command example in the resources section. Keep generic concept references independent of the exercise's files and solution. Author setup and automated verification details belong in maintainer documentation.

The platform owns the common workspace workflow: preparing environments, attaching
the terminal, presenting declared files and services, downloads, hints and answer
submission. Shared usage guidance belongs in the platform's documentation and UI.
Write each brief and walkthrough around its exercise, so changes to workspace
button names or layout leave the problem content valid. Adding a problem requires
its manifest and resources; catalog discovery and available player tools follow
those declarations automatically.

### Requester messages

Use the named `message` block for dialogue from the requester:

```markdown
::message{from="moru17"}
복구 키를 내보낸 파일이 공개됐어요. 다른 사람도 원래 값을 읽을 수 있나요?
::
```

The platform recognizes this md4x component name and renders the sender above the
message using the shared UI theme. `from` is an optional string; omit it for an
unnamed message. The body supports the existing allowed Markdown elements. The
renderer reads the sender as escaped text and applies its own fixed markup and
styles. Author-supplied event handlers, CSS and other DOM attributes are ignored.
Ordinary `>` quotations keep their general quotation style.

### Person names in narrative

Mark a person's first appearance in ordinary narrative with `:person[닉네임]`.
Explain their relationship to the target in the same sentence:

```markdown
운영 담당자 :person[솔개로그]는 작업 보드 서버를 관리한다.
```

This is a subtle text-color cue. Keep the body font, size and weight, and write
later appearances as plain text. Use the name as plain text inside the directive;
bold, links, inline code and decorative labels are unnecessary. Message senders
continue to use the existing `from` field. Authors declare the person explicitly;
the consumer does not guess names from ordinary words. Consumers without this
presentation hint retain the readable child text. This optional markup stays
within the current Markdown contract.

### Briefing sections

Use MDC blocks to declare the role of each part of the briefing. The platform
supplies one visible heading and the matching shared presentation.

| Block | Default heading | Content |
| --- | --- | --- |
| `::objective` | 의뢰 목표 | The action and observable completion result |
| `::resources` | 전달받은 정보 | Files, accounts, credentials and supplied facts |
| `::knowledge` | 시작 전 알아둘 것 | Essential neutral background; optional learning references carry general concepts |
| `::submission` | 정답 형식 | Answer format and any value changes after restart |

Close each block with `::`. An optional escaped `title` string supplies a more
specific heading, such as `::resources{title="접속 정보"}`. Write the content inside
the block; its heading is supplied once by the renderer. Keep narrative context
in ordinary paragraphs. Use normal Markdown headings in hints and walkthroughs.
All blocks retain the existing allowed body elements and attribute restrictions.

## Hints

Use `##` for primary content headings and `###` for subsections. Consumers place brief headings beneath the panel title and walkthrough headings beneath the learning section.

Hints are optional. Use `hints = []` when the brief and starting knowledge provide enough help. Choose the count from actual distinct reasoning obstacles in the exercise. Each hint helps with one obstacle and adds information beyond the brief and preceding hints. Keep exact answers and complete solution sequences in the walkthrough.

Declare selected Markdown files in `[content].hints`, in increasing specificity when more than one is useful. A hint suggests an observation, way of thinking or missing connection. It should help the player move forward without requiring source checkout navigation. The UI lets players choose which hints to open.

## Walkthrough

Every problem supplies `[content].walkthrough`. Explain the key insight, observations, intermediate reasoning, exact reproducible steps, how the result is confirmed and what the player learned. A final answer alone is insufficient. Use the browser and prepared terminal as the execution context. Include a fixed answer where appropriate; for generated answers explain how to retrieve the current instance's value. Give defensive lessons where they explain the vulnerability. The website labels the walkthrough as containing answers and opens it on explicit request.

## Author review

Review the rendered problem as a first-time solver, independently of whether `solve.command` passes.

- Can I state the goal and tell when I have succeeded?
- Can I explain the target's normal use, the incident, the requester’s reason for
  seeking help, and how the supplied resources support my investigation?
- Can I start using only the supplied context and visible controls?
- Do the words in dialogue, documents and target pages name the same actual
  features? Are unfamiliar terms explained before they are needed?
- Do the stated prerequisites match every step, including language features,
  calculations and tool operations? Does the exercise demonstrate its stated
  security learning objective?
- Can I inspect each required resource and perform every exercise step in the prepared environment?
- Are credentials, submission format, expected output and restart effects clear where relevant?
- Does each optional hint address a distinct reasoning obstacle and add useful help? Is the answer absent from the initial brief?
- Does the walkthrough explain why the approach works and reproduce the result?
- Does a failure to load content offer a retry, rather than sending players into repository files?

The format validator checks declarations, distinct regular Markdown files, repository containment, UTF-8, the 1 MiB limit and hint count. These checks cannot prove pedagogical quality. Author and learner review supply that judgment; runtime and API/UI tests verify execution and presentation. Record the evidence in `AUTHORING.md` using the [publication review](authoring-standard.md#review-before-publication).
