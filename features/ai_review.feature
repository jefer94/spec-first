Feature: AI Review — Diff vs Specs
  As a repository maintainer
  I want an AI agent to review code against accepted specs
  So that seniors only review pre-validated, spec-compliant code

  Background:
    Given the action is configured with default settings
    And "accepted_tag" is "specs-accepted"
    And "ai_review_tag" is "ai-review"
    And "senior_tag" is "senior-review"

  # --- Trigger ---

  Scenario: AI review triggered when both tags are present
    Given a PR has the label "specs-accepted"
    And the PR references spec PR #42 with accepted specs
    And the PR contains code changes
    When the label "ai-review" is added
    Then the action should fetch specs from PR #42
    And the action should fetch the code diff from the current PR
    And the action should invoke the LangChain agent with the diff as primary input

  Scenario: AI review tag added without accepted tag
    Given a PR does not have the label "specs-accepted"
    When the label "ai-review" is added
    Then the action should take no review action

  # --- LangChain Tools ---

  Scenario: Agent uses read_file tool for context
    Given a diff that modifies function "authenticate" in "src/auth.py"
    And the accepted specs reference "Authentication" requirements
    When the LangChain agent processes the diff
    Then the agent should call the "read_file" tool for "src/auth.py"
    And the agent should call the "read_spec" tool to load spec requirements
    And the agent should produce a compliance verdict based on diff and context

  Scenario: read_file returns first page with total_lines when no offset given
    Given a file "src/large_module.py" has 2000 lines
    When the agent calls "read_file" for "src/large_module.py" with no offset or limit
    Then the tool should return the first page of content
    And the response should include "total_lines" equal to 2000

  Scenario: read_file returns specific range with offset and limit
    Given a file "src/large_module.py" has 2000 lines
    When the agent calls "read_file" with offset 150 and limit 50
    Then the tool should return only lines 150 through 200
    And the response should include "total_lines" equal to 2000

  Scenario: Agent paginates through a large file
    Given a file "src/large_module.py" has 2000 lines
    When the agent calls "read_file" and sees total_lines exceeds the page size
    Then the agent may call "read_file" again with a new offset to read the next page

  Scenario: Agent uses list_changed_files on large PRs
    Given a PR with changes across 12 files
    When the LangChain agent processes the diff
    Then the agent should call the "list_changed_files" tool to understand scope
    And the agent should call "read_file" selectively on files relevant to specs
    And the agent should not attempt to load all files into a single prompt

  Scenario: Agent uses get_repo_structure for new files
    Given a diff that adds a new file "src/payments/processor.py"
    When the LangChain agent processes the diff
    Then the agent may call the "get_repo_structure" tool
    And the agent should assess whether the file placement fits the architecture

  # --- Approval Path ---

  Scenario: AI approves a fully compliant implementation
    Given the LangChain agent concludes the code satisfies all spec requirements
    And "senior_members" is "alice,bob"
    When the AI review completes
    Then the label "senior-review" should be added
    And a reviewer should be assigned from "alice,bob"
    And a comment should be posted confirming spec compliance
    And the comment should include a per-file review summary

  Scenario: AI approves with minor non-blocking observations
    Given the LangChain agent finds the code is spec-compliant
    And the agent has non-blocking observations about code style
    When the AI review completes
    Then the label "senior-review" should be added
    And a senior reviewer should be assigned
    And a comment should list the observations as non-blocking suggestions

  Scenario: Senior assigned randomly when no senior_members configured
    Given the LangChain agent concludes the code satisfies all spec requirements
    And "senior_members" is empty
    When the AI review completes
    Then a reviewer should be assigned randomly from collaborators with write+ access
    And the label "senior-review" should be added

  # --- Rejection Path ---

  Scenario: AI rejects a non-compliant implementation
    Given the LangChain agent finds spec violations
    When the AI review completes
    Then the label "ai-review" should be removed
    And the label "senior-review" should not be added
    And a comment should be posted with:
      | section               | content                                             |
      | Spec Compliance       | unmet requirements referencing specific scenarios   |
      | Implementation Review | alternative approaches with trade-offs              |
    And the feedback should reference spec requirements by name

  Scenario: AI review fails due to API error
    Given the OpenRouter API returns a 500 error
    When the AI review is attempted
    Then the label "ai-review" should be removed
    And a comment should be posted using the "msg_ai_failure" template
    And the comment should suggest manual review as fallback

  Scenario: AI review fails due to token limit exceeded
    Given the diff exceeds the model's context window even after chunking
    When the AI review is attempted
    Then the label "ai-review" should be removed
    And a comment should be posted using the "msg_ai_failure" template
    And the comment should suggest manual review as fallback
