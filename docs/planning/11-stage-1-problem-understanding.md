# Stage 1: Problem understanding

Status: prepared for human review. The user problem below is a hypothesis. No application implementation is authorized by this document alone.

## Proposed problem

When a software delivery plan changes, a delivery lead must identify which customer commitments need review, who is accountable now, and what evidence supports the impact. That information may be distributed across tickets, planning documents, and conversations. Manual reconciliation can miss indirect dependencies or use outdated decisions.

The question to approve is whether we should focus on this problem. Product name, interface, agent framework, and detailed architecture remain open.

## Stakeholders

| Stakeholder | Job or concern | Evidence status |
| --- | --- | --- |
| Delivery lead, proposed primary user | Assemble an accurate impact assessment after a plan changes | Hypothesized user and workflow |
| Customer-success or account owner | Decide which promises need discussion with customers | Hypothesized stakeholder |
| Product or engineering owner | Establish current scope, dates, dependencies, and exceptions | Hypothesized stakeholder |
| Customer | Receive reliable expectations and timely updates | Expected downstream beneficiary |
| Hackathon participant | Demonstrate a useful graph-dependent agent within the event | Known project objective |

Do not assume the delivery lead and account owner are the same person. Finding technical impact and communicating a revised commitment are separate responsibilities.

## Root-cause hypotheses

The likely issue is not merely that documents are difficult to search. A plan change must propagate through dependencies into promises made elsewhere. Records can also disagree about dates, responsibility, and scope.

| Hypothesis | Why it matters | What would challenge it |
| --- | --- | --- |
| Dependencies span several systems | No single ticket contains the full answer | One maintained tracker already contains all relevant relationships |
| Old and proposed decisions remain visible | Latest mention can be mistaken for approved truth | Existing workflow keeps authoritative state explicit |
| Ownership changes independently of plans | A correct finding can reach the wrong person | Current ownership is already reliable and accessible |
| Missing dependencies are common | Empty results can create false reassurance | Required relationships are complete and audited |
| Reconciliation occurs often enough to matter | Recurring work may justify a dedicated tool | Changes are rare or a manual checklist is sufficient |

These are plausible explanations, not findings from user interviews.

## Concrete example

In a fictional company, export delivery moves from 19 to 23 October. One customer was promised export on 20 October. Another needs an audit bundle on 21 October that depends on export. A third has a later deadline. A fourth has an approved exception. A fifth has no documented dependency mapping.

The useful outcome is a justified distinction among affected, no identified date conflict, exception, and unknown. It must also identify the current responsible person. The example demonstrates the proposed job; it does not prove real demand or determine the implementation.

## Existing ways to solve it

The [landscape research](../research/04-company-brain-landscape.md) documents enterprise search, work agents, graph context, temporal memory, and close public projects. It provides evidence that this broad category is active. It does not establish that competing products fail at this exact workflow.

Compare a maintained spreadsheet or checklist, explicit links in an issue tracker, an existing suite agent, and a dedicated application. A simple operational process may be enough. Building a new product is justified only if it offers a useful improvement under the selected success criteria.

Our proposed workflow overlaps with Drift's changed-decision updates and Hopper's dependency-to-customer impact. Originality must be assessed at the actual workflow and evaluation level. A new name does not establish differentiation.

## Constraints and exclusions

The selected event requires meaningful FalkorDB use. The current preference is Company Brain. The build window is limited. Use the [rules document](../hackathon/01-hackathon-rules.md) for the previously researched entry requirements.

For the initial demonstration, use fictional company records with known expected outcomes. Exclude legal interpretations, autonomous customer messaging, unrestricted company-wide automation, and sensitive employee data. These exclusions keep the proposed problem testable within the event; they are not claims about the limits of a future product.

## Evidence still missing

We have not established actual reconciliation frequency, current effort, the cost of missed commitments, willingness to adopt another tool, or whether an existing suite agent already solves the task satisfactorily. We have not verified extraction accuracy or graph advantage.

Before a commercial claim, observe the workflow with a delivery or customer-success lead and test the same task in existing tools. For the hackathon, a disclosed synthetic task can validate technical behavior. It cannot replace customer validation.

## Recommendation and approval boundary

Recommend this as the initial problem hypothesis because it has a specific user, trigger, decision, and observable outcome. Approve investigating it through the next stages, rather than committing to PromiseGraph or its earlier architecture.

Proposed approved statement: “Help a delivery lead reconcile customer commitments after a software delivery plan changes, using current ownership and traceable evidence, while making uncertainty explicit.”

The user may approve this statement, revise the user or scope, or redirect the problem. After approval, Stage 2 defines measurable success before we choose a solution direction.
