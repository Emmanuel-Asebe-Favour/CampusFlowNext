# AI Learning Log — CampusFlow

**Role:** Engineer A
**Focus:** Ticket workflow safety, note validation, and JSON storage.

## Learning Cycle 1 — Ticket Workflow Safety and Notes

### Concept I Needed to Understand
I needed to understand how to prevent invalid ticket operations from changing data. I also needed to understand how to validate notes and generate unique note IDs.

### Prompt Used
I asked the AI assistant to help me update `tests/test_workflow.py` with complete tests for ticket assignment, status transitions, reopening resolved tickets, and note validation.

*Note: Check the conversation and replace this description with the exact prompt if the assignment requires verbatim prompts.*

### Summary of the AI Explanation
I learned that validation should happen before modifying ticket data. A ticket must be assigned before moving to `in_progress`. A resolved ticket must be reopened before reassignment or adding notes. Notes need a valid author, a message between 5 and 300 characters, and a unique ID.

### Independent Experiment
I ran the workflow tests in the terminal and checked whether valid operations succeeded and invalid operations were rejected.

### Verification Evidence
- Command: `python3 -m unittest discover -s tests -p "test_workflow.py" -v`
- Result: 22 tests passed.
- What I learned: Automated tests help verify both successful operations and rejected operations.

### My Final Decision
I kept the validation checks and added tests for resolved tickets, malformed existing notes, duplicate numeric note IDs, and rejected notes not consuming an ID.

## Learning Cycle 2 — JSON Storage and Validation

### Concept I Needed to Understand
I needed to understand how to validate saved ticket data, handle malformed JSON, and prevent ticket IDs from colliding after reloading data.

### Prompt Used
I worked with the AI assistant to review and test the JSON storage implementation, including validation of ticket fields, schema versions, and ID generation.

*Note: Check the conversation and replace this description with the exact prompt if the assignment requires verbatim prompts.*

### Summary of the AI Explanation
I learned that JSON data should be validated after loading and before saving. Invalid data should produce a clear error rather than being silently accepted. A missing file can return an empty ticket list, and ticket ID generation should consider the highest existing numeric ID.

### Independent Experiment
I ran the storage tests and the complete test suite to verify JSON loading, saving, invalid data handling, and ticket ID generation.

### Verification Evidence
- Storage and workflow test command: `python3 -m unittest discover -s tests -v`
- Result: 39 tests passed.
- What I learned: Running the complete suite helps identify problems across different parts of the project.

### My Final Decision
I kept the storage validation and ID generation changes because the tests passed. I also updated the README to explain the JSON structure and validation rules.

## Reflection

I learned that writing code is not enough; I must also test what happens when inputs are invalid. I now better understand how validation, exceptions, and automated tests help protect application data. I will continue checking test results and reviewing changes before committing and opening a pull request.

