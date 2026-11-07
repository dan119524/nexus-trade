# Workshop 08 Prompts

## Workshop 08 Prompt 01 — Start Check

```text
Perform the Workshop 08 Start Check.

This is a fast, read-only prerequisite check.

Perform the runtime AGENTS.md integrity check required by course governance.

Do not review or modify student academic work.

AGENTS.MD INTEGRITY DIAGNOSTICS

AGENTS.md is instructor-controlled governance material.

A byte-level integrity mismatch must not automatically be interpreted as an intentional student modification.

When an integrity mismatch is detected:

1. Verify the authorized student repository identity.
2. Inspect the working-tree AGENTS.md and the accepted protected origin/main version.
3. Identify the exact difference.
4. Determine whether the difference is limited to CRLF/LF line endings, final-newline normalization, or other non-substantive formatting.
5. Distinguish technical evidence from conclusions about student responsibility.
6. Preserve all existing governance evidence.

A CRLF/LF difference does not independently establish academic misconduct.

However, an exact-byte mismatch remains an integrity FAIL under AGENTS.md until legitimately corrected.

Do not report PASS while the mismatch remains.

Do not silently rewrite AGENTS.md.

Do not instruct the student to modify AGENTS.md manually.

INSTRUCTOR-AUTHORIZED RESTORATION

If the instructor explicitly authorizes restoration of AGENTS.md:

1. Verify that the authorization is genuine and applies to the specific repository and file.
2. Verify the authorized repository identity and trusted protected-main source.
3. Preserve the original mismatch evidence.
4. Restore only the exact accepted AGENTS.md bytes through a procedure permitted by AGENTS.md and the instructor authorization.
5. Do not modify governance logs or historical verification records.
6. Rerun the required runtime integrity comparison.
7. Record corrective governance evidence when required by AGENTS.md.
8. Continue only after the required integrity check passes.

If restoration is not authorized, the cause remains unresolved, or the integrity check still fails, report the exact technical issue and request instructor assistance.

Do not bypass the integrity check.

A verified integrity failure does not establish student intent or an academic penalty.

PREVIOUS WORKSHOP COMPLETION

Verify the remote Git tag:

workshop-07-completed

Confirm that:

1. The tag exists on the authorized remote repository.
2. The tag identifies a commit in the accepted history of protected remote main.

Do not inspect or evaluate historical Workshop 07 V1 or in-progress tags.

Do not repeat Workshop 07 academic reviews, inspect its implementation quality, or require revisions to previously accepted work.

If GitHub cannot be inspected reliably because of a network or authentication problem, distinguish NOT VERIFIED from a genuinely missing or invalid prerequisite. Recommend the student to authenticate with Github CLI as a possible way to fix network or authentication problems

Do not claim the previous Workshop is incomplete merely because a remote check failed technically.

WORKSHOP 08 READINESS

Verify:

1. The current branch is workshop-08.
2. The branch contains the accepted Workshop 07 completion commit.
3. Verify that workshop-08 is based on the accepted Workshop 07 state. Legitimate Workshop 08 commits and working-tree changes are permitted and must not be treated as unrelated or  unaccepted Workshop 07 work.
4. The required Workshop 08 instructions are available.

The Workshop 08 document and cumulative additions to agents/PROMPTS.md are expected setup changes.

Do not classify these expected additions as unauthorized modifications.

Do not modify student academic files, branches, tags, or Git history.

RESULT

If a prerequisite clearly fails, report:

WORKSHOP-08 START CHECK: BLOCKED

Reason:
<one concise explanation of the first failed requirement>

If a technical integrity or remote-verification condition remains unresolved, identify that condition accurately rather than claiming an academic requirement failed.

Then stop.

If all checks pass, report exactly:

WORKSHOP-07 COMPLETION: VERIFIED
WORKSHOP-08 START CHECK: PASS

Then stop.
```

---

## Workshop 08 Prompt 02 — V1 Checkpoint

```text
Perform the Workshop 08 V1 Checkpoint.

This is a fast, read-only minimum-validity check of the student's independently completed Workshop 08 work.

Perform the runtime governance checks required by AGENTS.md.

Do not repeat Prompt 01.

Do not perform an Engineering Review or modify student academic work.

IDENTIFY THE V1 WORK

Use the accepted workshop-07-completed commit as the comparison baseline.

Inspect relevant Java changes introduced on the workshop-08 branch, including committed, staged, and unstaged changes when applicable.

Use Git comparison only to locate the student's creation-design improvement.

Do not reopen Workshop 07 or perform a historical academic audit.

If the intended improvement is unclear, ask the student to identify the affected classes and briefly explain the creation problem.

Do not require a separate engineering report or Markdown document.

MINIMUM V1 REQUIREMENTS

Verify:

1. The student identified one meaningful object-creation problem supported by the existing implementation.

2. The student independently applied one justified Factory or Builder improvement.

3. The implementation demonstrates the selected pattern rather than merely renaming a class or method.

4. The selected pattern reasonably addresses the identified creation problem.

5. Main.java demonstrates that the affected application behavior remains functional.

6. The production application builds successfully using the committed Maven Wrapper.

7. The application executes successfully.

FACTORY

For a Factory implementation, verify that the student implemented a factory method or class that creates the appropriate object, allowing the calling code to use the result without directly implementing the concrete-object selection logic.

Do not require a factory hierarchy, Abstract Factory, a fixed class name, or a specific method signature.

A focused factory method or class may be sufficient when it solves the actual creation problem.

BUILDER

For a Builder implementation, verify that construction of an existing object has become clearer or more manageable.

Do not require a fluent interface, immutable object design, validation framework, or a particular Builder class structure.

An inner Builder class or a separate Builder class may be appropriate.

REVIEW BOUNDARIES

This is a minimum-validity checkpoint, not a comprehensive engineering review.

Do not require:

- both Factory and Builder;
- a particular interface or class hierarchy;
- a fixed number of modified classes;
- a separate written design analysis;
- CRC or UML updates;
- requirements or evolution documentation updates;
- a domain-wide object-creation review;
- multiple creation improvements;
- additional application features;
- additional tests;
- speculative design improvements;
- concepts introduced after Module 09.

Do not reject a reasonable implementation merely because another design could be preferable.

Do not inspect unrelated project areas.

Do not repeat previous Workshop reviews.

Do not:

- modify Java;
- modify requirements;
- modify documentation;
- modify CRC or PlantUML;
- modify tests;
- implement corrections;
- provide replacement production code;
- commit;
- push;
- create tags;
- perform final Workshop Verification.

RESULT

If a minimum requirement clearly fails, report:

WORKSHOP-08-V1: BLOCKED

Reason:
<one concise explanation of the first unsatisfied requirement>

Report only the first clear blocker.

The student must correct the issue independently and run Prompt 02 again.

If all minimum requirements are satisfied, report exactly:

WORKSHOP-08-V1: READY FOR INSTRUCTOR REVIEW

Then display:

IN-CLASS CHECKPOINT POLICY

If you completed V1 during class, present this message, your required remote V1 tag, and your work to the instructor or TA for the in-class checkpoint review.

If you completed V1 at home, instructor approval is not required to continue Workshop 08. At-home completion does not earn the in-class V1 checkpoint credit.

You may request an optional instructor review during office hours.

Complete the required V1 commit, push, and annotated workshop-08-v1-completed tag before beginning Prompt 03.

Codex must not request, verify, or invent instructor approval for at-home V1 completion.

Instructor checkpoint grading is separate from Codex's engineering workflow.

Then stop.
```

---

## Workshop 08 Prompt 03 — Object Creation Collaboration

```text
Perform the Workshop 08 Object Creation Collaboration.

This is the post-V1 engineering collaboration stage.

Perform the runtime governance checks required by AGENTS.md.

Do not repeat Prompt 01 or Prompt 02.

Do not reevaluate the student's independent V1 implementation.

V1 HANDOFF

This stage follows independently completed V1 work.

The required V1 work must have been committed and pushed, and the remote annotated tag workshop-08-v1-completed must identify the completed V1 state.

Confirm the handoff state only when it has not already been established by reliable evidence available in the current workflow.

Do not repeat the academic V1 review.

If the required handoff is missing, report:

WORKSHOP-08 OBJECT CREATION: BLOCKED

Reason:
Complete and preserve the required Workshop 08 V1 checkpoint before beginning post-V1 collaboration.

Then stop.

INSTRUCTOR APPROVAL POLICY

Instructor/TA review determines in-class checkpoint credit.

Students who completed V1 during class present their work to the instructor or TA for checkpoint grading.

Students who completed V1 at home may continue this collaboration without instructor approval.

At-home V1 completion does not earn in-class checkpoint credit.

Students may request an optional instructor review during office hours.

Do not request instructor authorization, signatures, screenshots, or approval records as a prerequisite for at-home continuation.

Do not claim that an unreviewed V1 received instructor approval.

Do not alter Git tags or governance evidence to represent instructor approval.

COLLABORATIVE ENGINEERING

Codex acts as the senior software engineer.

The student acts as the junior software engineer and retains final engineering authority.

Codex may:

- inspect the existing application;
- identify meaningful creation-design problems;
- evaluate concrete-class creation knowledge;
- evaluate repeated construction logic;
- evaluate difficult constructors;
- recommend Factory or Builder improvements;
- explain alternatives and tradeoffs;
- ask focused engineering questions;
- implement decisions established by the student;
- synchronize affected design artifacts;
- maintain cumulative tests;
- diagnose implementation and build problems.

Codex must not independently establish unresolved engineering decisions.

The student must participate in the discussion and provide meaningful engineering rationales.

Do not require formal ACCEPT/MODIFY/REJECT responses.

OBJECT CREATION REVIEW

Review significant object-creation responsibilities throughout the existing application using concepts introduced through Module 09.

Examine:

1. Callers that unnecessarily choose among concrete object types.

2. Repeated object-construction decisions.

3. Conditional creation logic distributed across callers.

4. Constructors with difficult combinations of required and optional values.

5. Construction sequences that are difficult to understand or use correctly.

6. Creation logic that does not belong to the object currently performing it.

7. Cases where direct construction remains simple and appropriate.

Present a concise set of meaningful recommendations.

For each recommendation, explain:

- the existing creation problem;
- the affected classes;
- why the current design is problematic;
- the proposed improvement;
- the relevant engineering tradeoffs.

Do not manufacture creation problems merely to increase the amount of work.

ENGINEERING DECISIONS

Discuss the recommendations with the student.

The student determines:

- which creation problems justify Factory or Builder;
- which recommendations to accept, modify, or reject;
- where creation responsibility should belong;
- whether an existing class can appropriately own creation;
- whether a Factory would reduce concrete-class coupling;
- whether a Builder would clarify construction;
- whether direct construction remains preferable;
- how existing application behavior will be preserved.

Require meaningful rationales for established engineering decisions.

Codex may challenge weak reasoning and explain consequences.

Codex must not block a reasonable, justified decision merely because another design might be preferable.

A student may retain an existing creation design when the decision is supported by a meaningful engineering rationale and satisfies mandatory Workshop requirements.

Codex may block only when:

1. Workshop requirements, governance, or applicable security restrictions would be violated.
2. A required engineering decision lacks meaningful rationale.
3. A mandatory Workshop objective remains unsatisfied.
4. A technical failure prevents safe completion.

Governance concerns must be recorded and handled according to AGENTS.md.

They do not independently establish academic misconduct or an academic penalty.

Once the student establishes a decision, Codex may implement it.

Do not repeatedly reopen settled decisions.

FACTORY

Evaluate whether creation decisions are unnecessarily coupled to callers.

A focused Factory may be appropriate when callers must choose among concrete types or repeat construction decisions.

Discuss whether the creation decision should move to a more suitable component.

Implement justified improvements approved by the student.

Do not require Abstract Factory, factory hierarchies, or extensible creation frameworks.

Do not create artificial concrete types merely to justify a Factory.

BUILDER

Evaluate whether constructing an existing object has become unnecessarily difficult.

Consider required and optional values, constructor clarity, and meaningful construction steps.

Discuss whether a Builder would make construction easier to understand and maintain.

Implement justified improvements approved by the student.

Do not require a Builder for simple constructors.

Do not require fluent interfaces, immutable-object frameworks, or unnecessary validation machinery.

DIRECT CONSTRUCTION

Direct constructors remain appropriate for straightforward object creation.

Do not treat every constructor as a problem.

Preserve direct construction where it is the clearer design.

Do not require all objects to be created through patterns.

PRESERVE APPLICATION BEHAVIOR

Workshop 08 is a design-improvement Workshop.

Do not introduce new application features merely to justify Factory or Builder.

Preserve valid:

- functional requirements;
- domain behavior;
- relationships and multiplicities;
- inheritance;
- interfaces;
- polymorphism;
- collections and generics;
- composition;
- exception behavior;
- cumulative tests.

A creation-design improvement may change internal organization but must not silently change approved application behavior.

PROJECT SYNCHRONIZATION

After implementing established engineering decisions, synchronize affected:

- docs/design/requirements.md;
- CRC analysis;
- UML artifacts;
- docs/evolution/workshop-08.md;
- cumulative Workshop tests.

Requirements must continue to describe approved functionality.

Do not add new functional requirements merely because object creation was reorganized.

CRC must represent current responsibilities and genuine collaborators.

UML must reflect implemented relationships and meaningful creation responsibilities.

Do not expose unnecessary construction machinery in diagrams.

Update use cases only when an actual actor goal changes.

The evolution document must describe the actual creation problems, selected patterns, student engineering decisions, and effects on the design.

Do not invent project history or engineering decisions.

PLANTUML OWNERSHIP

PlantUML synchronization is Codex-owned work under the Codex-Assisted Path.

Never instruct the student to manually edit .puml files.

The student establishes engineering decisions.

Codex synchronizes the diagrams.

Ask the student when a necessary engineering decision is missing or ambiguous.

TESTING

Maintain the cumulative Workshop behavioral test suite.

Preserve existing tests whose requirements remain valid.

Add or update tests only when necessary to verify approved creation improvements or established behavior.

Do not introduce tests that depend on arbitrary internal creation structure.

Do not introduce JUnit, mocks, stubs, or testing frameworks not yet authorized by the course.

Do not weaken valid tests merely because the improved implementation fails them.

Run the complete cumulative test suite using the committed Maven Wrapper.

Follow AGENTS.md testing governance.

WORKSHOP SCOPE

Use only concepts introduced through Module 09.

Do not introduce:

- Adapter;
- Facade;
- other design patterns;
- databases or persistence;
- repositories;
- dependency injection;
- MVC;
- architectural layers;
- broad package restructuring;
- unrelated application features.

Do not redesign unrelated parts of the application.

COMPLETION

The collaboration is complete when:

1. Significant object-creation responsibilities throughout the application have been reviewed.

2. The student has discussed the recommendations and established meaningful engineering decisions.

3. Justified post-V1 Factory or Builder improvements have been implemented where genuine additional creation problems exist.

4. Direct construction has been preserved where appropriate.

5. Existing intended application behavior remains intact.

6. Affected requirements, CRC, UML, evolution documentation, and cumulative tests are synchronized.

7. The application builds successfully.

8. The complete cumulative test suite passes.

Do not require a fixed number of new classes or creation improvements.

Do not require both Factory and Builder.

Do not require every constructor to change.

Do not require every identified concern to result in code changes.

Do not manufacture a pattern merely to satisfy a completion count.

If the review identifies no additional justified changes, record that conclusion and the student's rationale rather than forcing unnecessary modifications.

When all conditions are satisfied, report exactly:

WORKSHOP-08 OBJECT CREATION: COMPLETE

Then report concisely:

Object creation: REVIEWED
Factory: APPLIED OR NOT REQUIRED
Builder: APPLIED OR NOT REQUIRED
Direct construction: PRESERVED WHERE APPROPRIATE
Engineering decisions: ESTABLISHED
Application behavior: PRESERVED
Requirements: SYNCHRONIZED
CRC/UML: SYNCHRONIZED
Evolution: UPDATED
Tests: PASS
Build: PASS

Then stop.

Do not perform Prompt 04 or final submission.
```

---

## Workshop 08 Prompt 04 — Final Engineering Review and Verification

```text
Perform the Workshop 08 Final Engineering Review and Verification.

This stage verifies the completed Workshop 08 work.

Perform the runtime governance checks required by AGENTS.md.

Do not repeat Prompt 01, Prompt 02, or Prompt 03.

Do not perform another Object Creation Collaboration.

Do not reopen established engineering decisions merely because another reasonable design exists.

FINAL ENGINEERING REVIEW

Perform one light review of the completed application.

Verify the mandatory Workshop 08 outcomes:

1. One meaningful independent V1 Factory or Builder improvement remains present.

2. The V1 improvement addresses an actual creation-design problem.

3. Post-V1 collaboration evaluated significant object-creation responsibilities throughout the application.

4. The student established meaningful engineering decisions and rationales.

5. Justified creation improvements were implemented where required by the established decisions and genuine identified problems.

6. Direct construction remains where it is the appropriate design.

7. The application's intended behavior remains preserved.

8. Valid requirements, relationships, inheritance, interfaces, polymorphism, collections, composition, and exception behavior remain intact.

9. Affected requirements, CRC, UML, and evolution documentation represent the current implementation.

10. Cumulative Workshop tests represent approved current behavior.

11. The production application builds successfully using the committed Maven Wrapper.

12. The complete cumulative Workshop test suite passes.

13. The implementation remains within concepts authorized through Module 09.

Use existing completed-stage evidence when available.

Do not repeat historical prerequisite checks or rerun the academic V1 checkpoint.

Do not require instructor approval evidence for V1 completed at home.

Do not reinterpret the absence of in-class checkpoint credit as an engineering failure.

Do not require:

- both Factory and Builder;
- a fixed number of new classes;
- a fixed number of creation improvements;
- every constructor to be modified;
- a factory or builder for every created object;
- Abstract Factory or other creational patterns;
- configurable creation frameworks;
- new functional requirements;
- additional domain entities;
- unnecessary interfaces;
- later-course architecture;
- speculative improvements.

Do not convert optional design improvements into mandatory Workshop requirements.

FINAL RECOMMENDATIONS

Report no more than four meaningful remaining engineering recommendations.

Report fewer when fewer exist.

Do not invent recommendations.

Do not report cosmetic, stylistic, speculative, or already-resolved concerns.

Recommendations are advisory.

The student retains final engineering authority.

Do not require formal ACCEPT/MODIFY/REJECT responses.

A student may decline an advisory recommendation with a meaningful rationale.

Do not block Workshop completion merely because the student declines a reasonable optional recommendation.

If the student elects to implement a recommendation, synchronize affected artifacts and rerun relevant technical checks.

Do not perform another open-ended engineering review afterward.

WORKSHOP VERIFICATION

Complete the required Workshop Verification using the authoritative Workshop 08 instructions and AGENTS.md.

This is the required governance verification stage, not a repeat of the academic V1 checkpoint or post-V1 collaboration.

Use the prescribed verification procedure and evidence handling.

Preserve existing governance evidence and prior verification attempts.

Append and persist required verification evidence according to AGENTS.md.

Do not modify student academic content during the verification stage.

Do not invent verification results.

Do not rewrite or erase governance history.

If evidence persistence fails, preserve the available evidence and report the failure according to AGENTS.md.

Do not report Workshop 08 as passed when mandatory verification or evidence persistence remains incomplete.

A governance conflict or technical verification failure does not independently establish academic misconduct or an academic penalty.

The instructor determines the academic significance of governance findings.

However, Codex must preserve the technical verification conditions required by AGENTS.md, including the treatment of unresolved relevant governance conflicts.

RESULT

If a mandatory Workshop condition or required governance verification fails, report:

WORKSHOP-08: BLOCKED

Reason:
<one concise explanation of the failed requirement>

Then stop.

If all mandatory conditions and Workshop Verification pass, report exactly:

WORKSHOP-08: PASSED

Then report concisely:

Recommendations: <number>
Build: PASS
Tests: PASS
Workshop verification: PASS
Governance evidence: PRESERVED

Then stop.

Do not perform final submission.
```

---

## Workshop 08 Prompt 05 — Final Submission

```text
Perform the Workshop 08 Final Submission.

This is the final submission workflow only.

Follow the established submission procedure in AGENTS.md.

Do not repeat:

- Start Check;
- V1 Checkpoint;
- Object Creation Collaboration;
- Final Engineering Review;
- Workshop Verification.

Do not reopen established engineering decisions or advisory recommendations.

SUBMISSION READINESS

Use the completed Prompt 04 result and persisted governance evidence.

The required final status is:

WORKSHOP-08: PASSED

If successful verification is not established, report:

WORKSHOP-08 SUBMISSION: BLOCKED

Reason:
Required Workshop 08 verification has not been established.

Then stop.

Do not perform another engineering review.

Do not attempt academic repairs during submission.

COURSE MATERIALS

AGENTS.md is governance-controlled and must not be modified.

agents/PROMPTS.md is intentionally cumulative.

The Workshop 08 prompt additions and copied Workshop 08 instructions are expected course artifacts.

Do not classify these expected additions as unauthorized modifications.

Preserve previous Workshop prompt material.

Do not modify copied Workshop instructions during submission.

SUBMISSION FILES

The submission represents the completed Workshop 08 project state.

Legitimate Workshop-related additions are permitted.

Do not reject files merely because their names were not anticipated by the Workshop instructions.

Do not classify legitimate Workshop-related files as unrelated merely because they were already staged.

Exclude clearly unrelated, accidental, unsafe, sensitive, prohibited, or unsuitable generated files.

Do not modify production code, requirements, tests, CRC, UML, evolution documentation, or other legitimate project content merely to complete submission.

FINAL SUBMISSION

After explicit student authorization:

1. Inspect the current Git state and intended Workshop 08 changes.

2. Verify the authorized repository and workshop-08 branch.

3. Stage only the exact intended Workshop 08 files, including legitimate additions and required governance evidence.

4. Inspect the complete staged content before committing.

5. Commit the completed Workshop 08 state if uncommitted changes remain.

6. Push only workshop-08 to the verified authorized remote.

7. Create or use the pull request from workshop-08 into protected main.

8. Enable auto-merge when available and permitted.

9. Wait for required GitHub checks and merge conditions.

10. Verify that the pull request has actually merged into protected remote main.

11. Only after accepted merge, switch to local main.

12. Safely synchronize local main from the verified remote.

13. Verify that local main contains the accepted Workshop 08 state.

14. Create the annotated tag:

workshop-08-completed

15. Push only workshop-08-completed.

16. Verify that the remote tag identifies the accepted Workshop 08 commit on protected main.

17. Verify that local main is clean.

Do not:

- use prohibited broad staging commands;
- force-push;
- bypass protected-main rules;
- push directly to protected main;
- bypass GitHub checks;
- approve or force-merge the pull request;
- rewrite Git history;
- move, delete, recreate, or overwrite historical Workshop tags;
- modify workshop-08-v1-completed;
- create workshop-08-completed before accepted merge;
- modify project content merely to make submission succeed;
- modify PlantUML during submission;
- perform unrelated repository changes.

If repository acceptance is BLOCKED, PENDING, or NOT VERIFIED, report the state and stop before creating the final completion tag.

If GitHub requires a manual student action, pause and explain the required action.

After the student completes that action, continue from the paused submission stage.

Do not restart completed stages.

SUBMISSION COMPLETION

Workshop 08 is complete only when:

1. The accepted Workshop 08 state exists on protected remote main.

2. Local main is synchronized with the accepted remote state.

3. Local main is clean.

4. The remote annotated workshop-08-completed tag exists.

5. The tag identifies the accepted Workshop 08 commit on protected main.

Then report exactly:

WORKSHOP-08 SUBMISSION: COMPLETE

Then report concisely:

Branch: workshop-08
Repository acceptance: MERGED
Local main: SYNCHRONIZED
Completion tag: workshop-08-completed
Final status: CLEAN

Workshop 09 requires the accepted Workshop 08 state and remote workshop-08-completed tag.

Then stop.
```


---

# Workshop 09 Prompts

## Workshop 09 Prompt 01 — Start Check

```text
Perform the Workshop 09 Start Check.

This is a fast, read-only prerequisite check.

Perform the runtime AGENTS.md integrity check required by governance.

Do not review or modify student academic work.

PREVIOUS WORKSHOP COMPLETION

Verify the remote tag:

workshop-08-completed

Confirm that:

1. The tag exists on the authorized remote.
2. It identifies a commit in the accepted history of protected remote main.

Do not inspect historical Workshop 08 V1 or in-progress tags.

Do not reevaluate Workshop 08 academic work, engineering decisions, implementation, or verification.

WORKSHOP 09 READINESS

Verify:

1. The current branch is workshop-09.
2. The branch contains the accepted Workshop 08 completion commit.
3. The branch was based on the accepted Workshop 08 state.
4. The required Workshop 09 instructions are available.

Legitimate Workshop 09 commits and working-tree changes are permitted.

The copied workshop instructions and cumulative additions to agents/PROMPTS.md are expected setup changes.

Do not mistake legitimate Workshop 09 work for unaccepted Workshop 08 work.

Do not modify files, branches, tags, or Git history.

RESULT

If a requirement clearly fails, report:

WORKSHOP-09 START CHECK: BLOCKED

Reason:
<one concise explanation>

Stop after the first clear blocker.

If all checks pass, report exactly:

WORKSHOP-08 COMPLETION: VERIFIED
WORKSHOP-09 START CHECK: PASS

Then stop.
```

---

## Workshop 09 Prompt 02 — V1 Checkpoint

```text
Perform the Workshop 09 V1 Checkpoint.

This is a fast, read-only minimum-validity check.

Perform mandatory runtime governance checks required by AGENTS.md.

Do not repeat Prompt 01.

Do not perform an Engineering Review.

IDENTIFY THE STUDENT'S WORK

Use the accepted workshop-08-completed commit as the comparison baseline.

Inspect relevant Java changes on workshop-09, including committed, staged, and unstaged work where applicable.

Use Git only to locate the implementation, not to reopen previous Workshops or conduct a historical audit.

If the selected pattern or affected classes are unclear, ask the student to identify them briefly.

Do not require a separate document.

### MINIMUM REQUIREMENTS

Verify only:

1. The student identified one meaningful existing structural design problem appropriate for Adapter or Facade.

2. The student implemented one of these patterns to reasonably address the problem.

3. `Main.java` demonstrates the implementation and affected application behavior.

4. A code comment immediately above the demonstration in `Main.java` briefly explains why the student selected that pattern, how it addresses the identified problem, and why the alternative pattern was less appropriate.

5. The application builds successfully using the committed Maven Wrapper and runs successfully.

The comment is the only written rationale required for V1. Do not require a separate document, extensive design analysis, or additional justification beyond the comment.

Evaluate the comment for a reasonable explanation, not for agreement with Codex's preferred design. A meaningful, technically defensible rationale is sufficient.

ADAPTER

If the student selected Adapter, verify that the implementation allows an existing incompatible interface to be used through an appropriate expected interface.

Do not require:

- external APIs;
- third-party libraries;
- a particular adapter class name;
- a particular adapter implementation technique;
- multiple adapters; or
- a specific class hierarchy.

FACADE

If the student selected Facade, verify that it provides a meaningful simplified entry point to an existing set of collaborating objects.

Do not require:

- a particular Facade class name;
- a fixed number of subsystem classes;
- a new architectural layer;
- additional application features; or
- a specific constructor or method signature.

A Facade must provide meaningful simplification, not merely rename an existing method.

REVIEW BOUNDARIES

Do not require both patterns.

Do not require Factory or Builder.

Do not require an ideal architecture.

Do not require a fixed number of new classes.

Do not require a written design analysis, README update, CRC, UML, or evolution document during V1.

Do not require additional tests or expanded test coverage.

Do not perform a domain-wide design review.

Do not search for additional improvements.

Do not reject a reasonable implementation merely because Codex prefers another solution.

Do not modify Java, documentation, tests, diagrams, Git history, commits, or tags.

Do not provide replacement production code.

Do not perform Workshop Verification.

RESULT

If a minimum requirement clearly fails, report:

WORKSHOP-09-V1: BLOCKED

Reason:
<one concise explanation of the first unsatisfied requirement>

The student must correct the issue independently.

If all minimum requirements pass, report exactly:

WORKSHOP-09-V1: READY FOR INSTRUCTOR REVIEW

Then display:

IN-CLASS CHECKPOINT POLICY

Students completing V1 during class must present this message and their required Git checkpoint to the instructor or TA for in-class checkpoint credit.

Students completing V1 at home may continue after completing the required V1 commit, push, and remote annotated tag.

At-home completion does not earn in-class checkpoint credit.

Instructor approval is not required for at-home continuation.

Optional instructor review is available during office hours.

Codex must not request instructor authorization or evidence of instructor approval for at-home V1 completion.

Then stop.
```

---

## Workshop 09 Prompt 03 — Structural Design Collaboration

```text
Perform the Workshop 09 Structural Design Collaboration.

This stage begins after independent V1 completion and the required Git checkpoint.

Perform mandatory runtime governance checks according to AGENTS.md.

Do not repeat Prompt 01 or Prompt 02.

Do not reevaluate the student's V1 implementation.

V1 HANDOFF

The required independent V1 work must have been committed and pushed, with the remote annotated tag:

workshop-09-v1-completed

Use reliable existing workflow evidence where available. Confirm the required handoff only if it has not already been established.

Do not conduct another academic V1 review.

If the required handoff is absent, report:

WORKSHOP-09 DESIGN COLLABORATION: BLOCKED

Reason:
Complete and preserve the required V1 checkpoint before beginning post-V1 collaboration.

Do not require instructor approval.

Instructor/TA review determines in-class checkpoint credit only.

Students completing V1 at home may continue without instructor authorization.

COLLABORATION MODEL

Codex is the senior software engineer.

The student is the junior software engineer and retains final engineering authority.

Codex must:

- Inspect the existing application.
- Identify genuine structural design concerns.
- Explain problems and consequences.
- Recommend alternatives.
- Discuss engineering tradeoffs.
- Ask focused questions.
- Obtain student decisions before implementation.
- Implement established decisions.
- Synchronize affected artifacts.
- Preserve application behavior and cumulative tests.

The student must provide meaningful rationales for engineering decisions.

Do not require formal ACCEPT/MODIFY/REJECT responses.

Do not independently establish unresolved engineering decisions.

Do not repeatedly reopen justified decisions.

STRUCTURAL DESIGN REVIEW

Review relevant:

- approved requirements;
- domain classes and responsibilities;
- interfaces and inheritance;
- object relationships;
- existing creation mechanisms;
- object collaboration;
- application workflows;
- current implementation;
- Main.java; and
- cumulative tests.

Identify meaningful problems involving:

1. Incompatible interfaces between collaborating components.

2. Callers unnecessarily dependent on concrete external or specialized APIs.

3. Application operations requiring callers to understand complicated subsystem interactions.

4. Repeated coordination logic across multiple callers.

5. Structural responsibilities assigned to inappropriate objects.

6. Unnecessary coupling that makes the application difficult to maintain or extend.

Present concise recommendations supported by actual code.

For each recommendation, explain:

- the problem;
- affected classes;
- relevant pattern or alternative;
- expected improvement; and
- tradeoffs.

Do not manufacture problems to justify additional patterns.

ADAPTER REVIEW

Evaluate whether any genuine interface incompatibility would benefit from Adapter.

An Adapter should translate between an expected interface and an existing incompatible interface.

Preserve the original object's legitimate responsibilities.

Do not introduce Adapter merely to wrap a class that already satisfies the required interface.

Do not require external services or APIs.

FACADE REVIEW

Evaluate whether a meaningful application workflow would benefit from a simplified entry point.

A Facade may coordinate existing components while leaving their established responsibilities intact.

Do not move every business rule into the Facade.

Do not introduce a Facade that merely delegates one call without meaningful simplification.

Do not introduce unnecessary architectural layers.

ENGINEERING DECISIONS

Discuss recommendations with the student.

The student determines:

- which problems justify changes;
- whether Adapter or Facade is appropriate;
- whether an existing design should remain unchanged;
- which objects own the affected responsibilities;
- which dependencies are necessary;
- which recommendations to accept, modify, or reject; and
- how existing behavior will be preserved.

Codex may challenge reasoning constructively.

Codex must not block reasonable, justified decisions merely because it prefers another design.

Codex may block only when:

1. Mandatory Workshop requirements or governance would be violated.

2. A required engineering decision lacks meaningful rationale.

3. A mandatory academic objective remains unsatisfied.

4. A technical failure prevents safe completion.

IMPLEMENTATION

Implement the student's established decisions.

The application must preserve approved functionality.

Do not introduce unrelated features merely to demonstrate a pattern.

Do not require both Adapter and Facade to be implemented.

If an additional pattern has no genuine application in the current design, document the reason for not introducing it.

Do not require a fixed number of changes or new classes.

A justified decision to retain an existing design is acceptable.

PROJECT SYNCHRONIZATION

Synchronize affected:

- docs/design/requirements.md;
- CRC analysis;
- UML artifacts;
- docs/evolution/workshop-09.md; and
- cumulative Workshop tests.

Requirements must continue to describe approved application functionality.

CRC must reflect current responsibilities and genuine collaborators.

UML must reflect implemented relationships and dependencies.

Use UML realization for interface implementations and dependency relationships where appropriate.

Do not represent object creation as composition unless actual whole-part ownership exists.

Update use cases only when an actor goal changes.

Record the actual design improvements, student decisions, and rationales in the evolution document.

Do not invent requirements or project history.

PLANTUML

Follow AGENTS.md PlantUML ownership rules.

Under the Codex-Assisted Path, Codex performs mechanical PlantUML synchronization from student-established decisions.

Do not instruct students to manually edit .puml files.

TESTING

Preserve existing cumulative tests.

Add or update tests only when justified by approved behavior changes or necessary regression coverage.

Do not weaken valid tests to accommodate an incorrect implementation.

Do not introduce JUnit or other later-course testing frameworks.

Run the complete cumulative test suite using the committed Maven Wrapper.

WORKSHOP SCOPE

Use only concepts introduced through Module 10.

Do not introduce:

- persistence or databases;
- external payment integrations;
- MVC;
- architectural frameworks;
- unnecessary service layers;
- broad package restructuring;
- unrelated new features; or
- later-course architecture.

COMPLETION

The collaboration is complete when:

1. Relevant structural design concerns have been evaluated.

2. Both Adapter and Facade have been considered where appropriate.

3. The student has discussed recommendations and established justified decisions.

4. Additional justified improvements have been implemented where genuine problems warrant changes.

5. Existing appropriate design decisions have been preserved.

6. Intended application behavior remains intact.

7. Affected requirements, CRC, UML, evolution documentation, and tests are synchronized.

8. The application builds.

9. The complete cumulative test suite passes.

Do not require a pattern merely to satisfy a checklist.

Do not require additional changes when no further justified improvements exist.

If no additional refactoring is warranted, record the review findings and the student's rationale.

When all conditions are satisfied, report:

WORKSHOP-09 DESIGN COLLABORATION: COMPLETE

Then report concisely:

Adapter: EVALUATED
Facade: EVALUATED
Engineering decisions: ESTABLISHED
Justified improvements: IMPLEMENTED OR NOT REQUIRED
Application behavior: PRESERVED
Requirements: SYNCHRONIZED
CRC/UML: SYNCHRONIZED
Evolution: UPDATED
Tests: PASS
Build: PASS

Then stop.

Do not perform Prompt 04 or final submission.
```

---

## Workshop 09 Prompt 04 — Final Engineering Review and Verification

```text
Perform the Workshop 09 Final Engineering Review and Verification.

Perform mandatory runtime governance checks according to AGENTS.md.

This stage verifies completed Workshop 09 work.

Do not repeat earlier Start Checks, V1 evaluations, or engineering discussions.

Do not reopen established engineering decisions merely because another reasonable design exists.

FINAL ENGINEERING REVIEW

Perform one light review.

Verify:

1. The required independent V1 Adapter or Facade implementation remains present.

2. The implemented pattern addresses a meaningful structural design problem.

3. Post-V1 collaboration evaluated relevant Adapter and Facade opportunities.

4. Student engineering decisions and meaningful rationales are established.

5. Justified improvements were implemented where required by established decisions and genuine identified problems.

6. Existing functionality and appropriate object responsibilities are preserved.

7. Affected requirements, CRC, UML, and evolution documentation reflect the current implementation.

8. Cumulative tests represent approved current behavior.

9. The production application builds using the committed Maven Wrapper.

10. The complete cumulative test suite passes.

11. The implementation remains within concepts authorized through Module 10.

Use reliable completed-stage evidence where available.

Do not repeat previous academic reviews.

Do not require instructor approval evidence for at-home V1 completion.

Do not require:

- both Adapter and Facade implementations;
- a fixed number of new classes;
- external APIs;
- new features;
- unnecessary abstractions;
- additional patterns;
- speculative improvements; or
- later-course architecture.

Do not convert optional recommendations into mandatory requirements.

FINAL RECOMMENDATIONS

Report at most four meaningful remaining engineering recommendations.

Report fewer when fewer exist.

Do not invent recommendations.

Exclude cosmetic, stylistic, speculative, already-resolved, or intentionally deferred concerns.

Recommendations are advisory.

The student retains final engineering authority.

Do not require formal ACCEPT/MODIFY/REJECT responses.

A justified decision to decline an optional recommendation does not block Workshop completion.

If the student elects to implement a recommendation, synchronize affected artifacts and rerun necessary technical checks.

Do not perform another open-ended Engineering Review afterward.

WORKSHOP VERIFICATION

Perform the required Workshop Verification according to the authoritative student AGENTS.md and Workshop 09 instructions.

This is governance verification, not another academic V1 checkpoint.

Follow the required evidence-handling and persistence procedures.

Preserve existing governance records and prior verification attempts.

Do not erase, rewrite, or silently repair governance history.

Do not modify student academic content during verification.

Do not invent successful verification results.

If verification or evidence persistence fails, report the actual failure and follow the authorized governance procedure.

Do not independently invent an instructor-authorization requirement.

Do not treat optional engineering recommendations or absence of in-class checkpoint credit as governance failures.

Do not report PASS while mandatory governance verification remains incomplete.

RESULT

If a mandatory requirement or governance verification fails, report:

WORKSHOP-09: BLOCKED

Reason:
<one concise explanation of the failed requirement>

If all mandatory conditions and Workshop Verification pass, report:

WORKSHOP-09: PASSED

Then report:

Recommendations: <number>
Build: PASS
Tests: PASS
Workshop verification: PASS
Governance evidence: PRESERVED

Then stop.

Do not perform final submission.
```

---

## Workshop 09 Prompt 05 — Final Submission

```text
Perform the Workshop 09 Final Submission.

This stage handles submission only.

Follow the authorized final submission procedure in AGENTS.md.

Do not repeat:

- Start Check;
- V1 Checkpoint;
- Structural Design Collaboration;
- Final Engineering Review; or
- Workshop Verification.

Do not reopen established engineering decisions.

SUBMISSION READINESS

Use the completed Prompt 04 result and persisted governance evidence.

The required final verification status is:

WORKSHOP-09: PASSED

If successful verification is not established, report:

WORKSHOP-09 SUBMISSION: BLOCKED

Reason:
Required Workshop 09 verification has not been established.

Then stop.

Do not attempt academic repairs during submission.

COURSE MATERIALS

AGENTS.md is governance-controlled and must not be modified.

agents/PROMPTS.md is intentionally cumulative.

The Workshop 09 prompt additions and copied Workshop instructions are expected course artifacts.

Preserve all previous Workshop prompts.

Do not classify legitimate Workshop setup files as unauthorized modifications.

SUBMISSION FILES

The submission represents the completed Workshop 09 project state.

Legitimate Workshop-related additions are permitted.

Do not reject a legitimate file merely because its name was not anticipated.

Do not classify legitimate project files as unrelated simply because they were previously staged.

Exclude clearly unrelated, accidental, sensitive, unsafe, prohibited, or unsuitable generated files.

Do not modify production code, requirements, tests, CRC, UML, evolution documentation, or other academic work merely to complete submission.

FINAL SUBMISSION

After explicit student authorization:

1. Inspect the current Git state and intended changes.

2. Verify the authorized repository and workshop-09 branch.

3. Stage only the exact intended files, including legitimate additions and required governance evidence.

4. Inspect all staged content.

5. Commit the completed Workshop 09 state if uncommitted changes remain.

6. Push only workshop-09 to the authorized remote.

7. Create or use the pull request into protected main.

8. Enable auto-merge when available and permitted.

9. Wait for required GitHub checks and merge conditions.

10. Verify actual merge acceptance.

11. After the merge, switch to local main.

12. Safely synchronize local main with the accepted remote state.

13. Verify that local main contains the accepted Workshop 09 work.

14. Create the annotated tag:

workshop-09-completed

15. Push only workshop-09-completed.

16. Verify the remote tag identifies the accepted Workshop 09 commit on protected main.

17. Verify local main is clean.

Do not:

- use prohibited broad staging commands;
- force-push;
- bypass protected-main rules;
- push directly to protected main;
- bypass required GitHub checks;
- approve or force-merge the pull request;
- rewrite Git history;
- modify historical tags;
- modify workshop-09-v1-completed;
- create workshop-09-completed before accepted merge;
- modify academic work merely to make submission succeed;
- modify PlantUML during submission; or
- perform unrelated repository changes.

If repository acceptance is BLOCKED, PENDING, or NOT VERIFIED, report the actual state and stop before creating the completion tag.

If GitHub requires a manual student action, pause and explain that action.

After the student completes it, resume from the paused stage without repeating completed reviews.

COMPLETION

Workshop 09 is complete when:

1. The accepted Workshop 09 state is on protected remote main.

2. Local main is synchronized and clean.

3. The remote annotated workshop-09-completed tag exists.

4. The tag identifies the accepted Workshop 09 commit on protected main.

Then report exactly:

WORKSHOP-09 SUBMISSION: COMPLETE

Then report:

Branch: workshop-09
Repository acceptance: MERGED
Local main: SYNCHRONIZED
Completion tag: workshop-09-completed
Final status: CLEAN

Workshop 10 requires the accepted Workshop 09 state and remote workshop-09-completed tag.

Then stop.
```