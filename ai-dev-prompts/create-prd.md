# Rule: Generating a Product Requirements Document (PRD)

## Goal

To guide an AI assistant in creating a detailed Product Requirements Document (PRD) in Markdown format, based on an initial user prompt. The PRD should be clear, actionable, and suitable for a junior developer to understand and implement the feature.

## Process

1.  **Receive Initial Prompt:** The user provides a brief description or request for a new feature or functionality.
2.  **Ask Clarifying Questions:** Before writing the PRD, the AI *must* ask clarifying questions to gather sufficient detail. The goal is to understand the "what" and "why" of the feature, not necessarily the "how" (which the developer will figure out). Make sure to provide options in letter/number lists so I can respond easily with my selections.
3.  **Generate PRD:** Based on the initial prompt and the user's answers to the clarifying questions, generate a PRD using the structure outlined below.
4.  **Save PRD:** Save the generated document as `[n]-prd-[feature-name].md` inside the `/tasks` directory. (Where `n` is a zero-padded 4-digit sequence starting from 0001, e.g., `0001-prd-user-authentication.md`, `0002-prd-dashboard.md`, etc.)

## Clarifying Questions (Examples)

The AI should adapt its questions based on the prompt, but here are some common areas to explore:

*   **Problem/Goal:** "What problem does this feature solve for the user?" or "What is the main goal we want to achieve with this feature?"
*   **Target User:** "Who is the primary user of this feature?"
*   **Core Functionality:** "Can you describe the key actions a user should be able to perform with this feature?"
*   **User Stories:** "Could you provide a few user stories? (e.g., As a [type of user], I want to [perform an action] so that [benefit].)"
*   **Acceptance Criteria:** "How will we know when this feature is successfully implemented? What are the key success criteria?"
*   **Scope/Boundaries:** "Are there any specific things this feature *should not* do (non-goals)?"
*   **Data Requirements:** "What kind of data does this feature need to display or manipulate?"
*   **Design/UI:** "Are there any existing design mockups or UI guidelines to follow?" or "Can you describe the desired look and feel?"
*   **Edge Cases:** "Are there any potential edge cases or error conditions we should consider?"

## PRD Structure

The generated PRD should include the following sections:

1.  **Introduction/Overview:** Briefly describe the feature and the problem it solves. State the goal.
2.  **Goals:** List the specific, measurable objectives for this feature.
3.  **User Stories:** Detail the user narratives describing feature usage and benefits.
4.  **Functional Requirements:** List the specific functionalities the feature must have. Use clear, concise language (e.g., "The system must allow users to upload a profile picture."). Number these requirements.
5.  **Non-Goals (Out of Scope):** Clearly state what this feature will *not* include to manage scope.
6.  **Design Considerations (Optional):** Link to mockups, describe UI/UX requirements, or mention relevant components/styles if applicable.
7.  **Technical Considerations (Optional):** Mention any known technical constraints, dependencies, or suggestions (e.g., "Should integrate with the existing Auth module").
8.  **Success Metrics:** How will the success of this feature be measured? (e.g., "Increase user engagement by 10%", "Reduce support tickets related to X").
9.  **Open Questions:** List any remaining questions or areas needing further clarification.

## Target Audience

Assume the primary reader of the PRD is a **junior developer**. Therefore, requirements should be explicit, unambiguous, and avoid jargon where possible. Provide enough detail for them to understand the feature's purpose and core logic.

## Output

*   **Format:** Markdown (`.md`)
*   **Location:** `/tasks/`
*   **Filename:** `[n]-prd-[feature-name].md`

## Final instructions

1. Do NOT start implementing the PRD
2. Make sure to ask the user clarifying questions
3. Take the user's answers to the clarifying questions and improve the PRD

# Product Requirements Document (PRD): Automated Housecleaning Feature

## Objectives
The automated housecleaning feature aims to:
- Reduce clutter in the project directory by managing temporary, one-time-use, and outdated files.
- Ensure critical files are preserved while providing recovery options for accidental deletions.
- Automate routine cleanup tasks to improve user productivity and maintain a clean workspace.

## Scope
This feature will focus on:
1. Identifying and managing temporary files, one-time-use files, and outdated files.
2. Overwriting or prompting for overwriting debugging logs and test harness output files.
3. Managing the Trash folder for temporary deletions and recovery.
4. Automating cleanup tasks daily at 1 AM HST, with a manual option available.
5. Labeling files at creation with metadata to indicate their purpose.
6. Generating reports for cleanup actions and providing a feedback loop for errors.

## Functionalities
### File Management
- **Root Directory Cleanup**: Prevent clutter by ensuring temporary files and one-time-use files are not stored in the root directory.
- **Output File Overwriting**: Automatically overwrite debugging logs and test harness output files unless the user opts out.
- **Trash Folder Management**: Empty the Trash folder weekly, retaining files for a configurable period (default: 7 days).

### File Labeling
- Attach metadata to new files to classify them as:
  - Program-related (substantial)
  - One-time-use
  - Temporary (to be overwritten)

### Automation and Scheduling
- **Daily Cleanup**: Run automated cleanup tasks daily at 1 AM HST.
- **Manual Option**: Allow users to trigger cleanup manually.
- **User Prompts**: Prompt users for confirmation when confidence in file deletion is low.

### Reporting and Feedback
- Generate a report summarizing cleanup actions, including:
  - File name
  - Reason for deletion
  - Timestamp
- Provide a feedback loop for errors to improve automation accuracy.

### Retention Rules
- Retain files in the Trash folder for 7 days (or longer based on best practices).
- Exclude dependencies, large open-source programs, and Docker-related files from cleanup.

## Success Metrics
- **User Productivity**: Measure the percentage of time users spend on productive tasks versus manual cleanup.
- **Error Rate**: Track the number of critical files accidentally deleted and recovered.
- **Automation Efficiency**: Evaluate the percentage of files correctly identified and managed by the system.

## Constraints
- Dependencies and large open-source programs must not be removed.
- Conflicting dependencies should be flagged for user attention but not resolved automatically.

## Risks and Mitigation
- **Accidental Deletions**: Use the Trash folder as a recovery mechanism.
- **User Frustration**: Provide clear prompts and reports to maintain user trust.
- **Performance Impact**: Optimize the cleanup process to minimize resource usage during automation.

## Implementation Notes
- Follow best practices for file management and retention.
- Integrate with existing architectural documents to determine file necessity.
- Ensure the feature is configurable to adapt to user preferences.