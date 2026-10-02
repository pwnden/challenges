# Scenario authoring standard

## Purpose and ownership

Use this standard to design, classify and review security exercises for pwnden.
The challenges repository owns these criteria. A problem is ready for publication
when its learning design, player content and execution have each been reviewed.

Start here before using the [scenario generator](creating.md). Use the
[scenario writing framework](scenario-authoring.md) to connect the actual target
and learning objective to a request, player role and observable mission outcome.
Record that setting in `AUTHORING.md`. The [player content
standard](player-content.md) covers briefs, hints and walkthroughs; the
[contract](contract.md) defines supported metadata and execution rules;
[verification](verification.md) covers automated checks.

## Define what the player will learn

Write one primary learning objective as an observable action: what the player
will inspect, discover, demonstrate or explain after solving the problem.
Identify the security principle that action illustrates, the information and
access the player starts with, and the evidence that confirms success.

For example, an access-control exercise can ask the player to demonstrate whether
an individual resource request enforces the logged-in user's permissions. Its
walkthrough explains the permission failure and the corrected behavior. A reverse
engineering exercise can ask the player to reconstruct an input check and explain
which transformations preserve enough information to recover its input.

Choose the learning area and topic from this objective, then map the actual
exercise to one category supported by the current contract. Learning areas grow
independently of that compatibility field. Choose file or service execution
from the resources needed to perform it. The implementation language supplies the
exercise; language knowledge contributes to the player's workload and must be
accounted for explicitly. Record how each substantial coding or calculation step
supports the security objective.

Use the [learning map](learning-map.md) to select an area and topic and scope the
observable experiment and prerequisites. Record the learning area, topic and
category choice in `AUTHORING.md`; the current contract has no structured
learning-area or topic field. Check the [execution feasibility map](execution-feasibility.md)
for the exact experiment's support and required preparation. A learning topic's
presence does not establish target or tool readiness.

Keep an introductory exercise focused on one new security concept. Supporting
steps should make that concept observable. Each additional concept needs a reason
to be present and contributes to the assessment of prerequisites and difficulty.

### Make security knowledge observable

Prefer player actions that directly reveal the security behavior: change an
input, compare responses, follow access to a resource, inspect an artifact or
observe a boundary being crossed. Provide prepared commands, analysis tools or
small visual experiments when these let the player focus on the principle.

Keep Python primarily an authoring and automated verification tool. Target
implementation and solution-script languages are separate from the abilities
required of the player. Design the usual player path to work without Python
knowledge. When understanding or writing code is essential to the security
objective, state the exact ability, explain why it is needed in `AUTHORING.md`
and provide the scoped context and examples. Assess that workload explicitly.

## Identify the intended learner and prerequisites

The common starting point is a person who can use a browser, read the supplied
instructions and enter or copy text. State any additional prerequisite as a
concrete ability. A necessary code-reading prerequisite becomes "follow the
condition and values used by this input check."
"Networking" becomes the specific ability needed, such as interpreting an HTTP
request and response.

Distinguish three roles for knowledge:

| Role | Author responsibility |
| --- | --- |
| Prerequisite | The player needs this ability before the first step that uses it. State its scope and provide a learning reference or sufficient player-facing explanation. |
| Learning objective | The player develops this ability through the problem. Connect observations, hints and the walkthrough to it. |
| Supporting context | Explain the small amount of information needed for the scenario or tools at the point where it is used. |

Trace the intended solution step by step. For each step, identify every required
language feature, tool operation, protocol detail, calculation and security
concept. Decide which role each has. An installed interpreter makes execution
available; the ability to understand or write code still needs to be accounted for.

Intro problems are approachable from the common starting point through the brief
and a small amount of supporting explanation. When coding knowledge or specialized
operations are prerequisites, state them explicitly and assess the complete
workload for a higher level. A learning reference should cover the ability needed
for this exercise. Requiring study of an entire language or domain adds substantial
work even when a reference is provided.

Before publication, place the required abilities and starting context in the
player brief or link to an available player-facing document. Author records and
answer-containing walkthroughs serve their own readers; first-time players need
enough context before they open a hint or answer.

## Select difficulty from evidence

Assess the complete intended journey using the default brief, supplied resources
and prepared tools, with hints and the walkthrough closed. Account for prerequisite
learning as well as solving. The [contract's five values](contract.md#difficulty)
remain the published difficulty scale.

| Level | Expected journey and evidence |
| --- | --- |
| 1 Intro | A browser-literate newcomer can start from the supplied explanation, learn one new security concept and perform a small observable experiment. Required operations are explained with a small example at the point of use. |
| 2 Easy | A learner with the stated limited prerequisites independently recognizes and applies one basic security technique. Required code reading or short scripting is scoped and already familiar to that learner. |
| 3 Medium | The learner connects several observations or concepts, chooses an analysis method and performs meaningful analysis or scripting. Explain the intermediate discoveries and required implementation. |
| 4 Hard | The learner analyzes a complex target or restrictive conditions and constructs a sequence of dependent techniques. Explain the dependencies, target behavior and implementation burden. |
| 5 Expert | The learner relies on deep domain knowledge and develops an approach requiring substantial original reasoning. Identify the specific technical or conceptual obstacles. |

Record the following evidence before choosing a level:

- **Prerequisite burden:** the abilities assumed and the preparation needed from
  the common starting point.
- **Discovery:** the observations supplied, those the player must find and the
  reasoning connecting them to an approach.
- **Implementation:** the code, calculations, tools and debugging needed to carry
  out that approach.
- **Dependencies:** the number and interaction of new security concepts and
  dependent solving steps.

Explain why the chosen level fits and how it differs from its neighboring levels.
Use the most demanding material part of the journey to avoid averaging away a
large obstacle. Code length, category, tool availability and the author's own
completion time each supply context; they do not establish a level by themselves.
Observed learner time is useful evidence alongside the causes of progress or
confusion. The generator's default level is an authoring placeholder to review.

For example, Rotor Lock requires following Python functions and loops, byte
values, XOR, shifts and rotation, then constructing an inverse transformation.
Those abilities need to appear in its prerequisite assessment and player context.
Assessing the number of lines in its checker alone misses that workload.

## Record concepts and relationships

Give each concept one focused meaning and a title that can be reused across
problems. Keep a problem's objective distinct from its scenario. An objective such
as validating object-level access permissions can recur in several scenarios.

Record relationships by their meaning:

| Relationship | Meaning |
| --- | --- |
| Problem requires concept | The ability is needed before solving the relevant step. |
| Problem teaches concept | The exercise develops the ability and its walkthrough explains it. |
| Concept requires concept | One concept must be understood before learning the other. |
| Concept relates to concept | The connection supports further reading without imposing a learning order. |

Reuse an existing concept document when available and record its link. Check that
each prerequisite chain reaches explainable starting abilities and has no cycle.
Related-reading links may connect in both directions. If a concept label would
reveal the key attack or solving technique, give the brief sufficient starting
context and put that specific connection in the answer-labelled walkthrough.

Contract v5 currently declares difficulty, tools and learning-content paths.
Concepts and these relationships are author records and document links today;
the platform has no concept graph or prerequisite API. Keep structured concept
metadata and graph presentation changes within a separately versioned contract
change when they are implemented.

## Keep a problem-specific author record

Keep `AUTHORING.md` beside the problem manifest. It records the intended learner,
security learning objective, prerequisite abilities and their references,
intended steps and observations, concept relationships, difficulty rationale,
alternative solutions, and review evidence. The generator creates a shared
starter for file and service problems. Existing problems use the same
[record template](../tools/templates/common/authoring.md).
Complete its prompts and match the recorded difficulty to the manifest value.

This is maintainer documentation and may discuss the solution. Its location
distinguishes its purpose; local problem files remain accessible to the player.
The website displays only declared player content. Publish the required context
in that content as well. Revisit the record when the solution, supplied resources,
prerequisites or explanations change.

## Review before publication

First reproduce the intended solution in a fresh prepared environment. Check
every required resource and operation against the declared player tools and
the supported contract. Exercise failure and restart behavior, and reproduce
alternative valid solutions that the author or reviewer identifies.

Then review the problem from the intended learner's position. For new problems
and material changes to learning design or difficulty, obtain an independent
review from someone with the stated learner profile. Record their actual
experience and the resulting changes. Keep technical reproducibility and learner
review as separate evidence; a passing solution script establishes one of them.

Publication requires evidence for each of these checks:

- The objective teaches a stated security principle and success is observable.
- Required abilities are scoped, explained or linked before they are needed.
- The learner can start and complete the exercise using its visible tools.
- The difficulty rationale covers the full journey and matches learner evidence.
- The brief, progressive hints and complete walkthrough pass the
  [content review](player-content.md#author-review).
- The intended and alternative accepted results can be verified. Avoid accidental
  answer leaks in the default content or target behavior that bypass the learning
  objective. Retain the explicit answer reveal in the walkthrough.
- [Format and execution checks](verification.md) pass, including patch behavior
  when declared and resource cleanup.
- The author record states the reviewer, date, exercise revision, checks run,
  observations, and publication readiness.

Automation verifies metadata and execution. Authors and learner reviewers
establish pedagogical suitability. Reassess the problem when learner evidence
shows missing prerequisites, an unexpected obstacle or a different effective
level.
