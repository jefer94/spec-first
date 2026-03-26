Feature: Feedback Quality
  As a contributor
  I want AI feedback to be structured and spec-focused
  So that I can quickly understand what to fix and how

  Scenario: Rejection feedback follows the required structure
    Given the AI rejects an implementation with 2 unmet requirements
    When the feedback comment is generated
    Then the comment should have a "Spec Compliance" section
    And the "Spec Compliance" section should list each unmet requirement
    And each unmet requirement should reference the failing scenario
    And the comment should have an "Implementation Review" section
    And each issue should offer at least 2 alternative approaches
    And each alternative should describe trade-offs for complexity, performance, and maintainability
    And the comment should have a "Summary" section with clear next steps

  Scenario: Feedback references Given/When/Then scenarios
    Given the accepted specs contain scenario "Authorized user applies accepted tag"
    And the implementation fails to check user permissions
    When the feedback comment is generated
    Then the feedback should quote the scenario:
      """
      GIVEN a user with maintain or admin role on the repository
      WHEN that user adds the accepted_tag label to a PR
      THEN the action MUST allow the label to remain
      """
    And the feedback should explain how the implementation fails the THEN clause

  Scenario: Feedback prioritizes spec compliance over style
    Given the AI finds both spec violations and code style issues
    When the feedback comment is generated
    Then the "Spec Compliance" section should appear before any style observations
    And spec violations should be labeled as blocking
    And style issues should be labeled as non-blocking suggestions

  Scenario: Approval feedback includes per-file summary
    Given the AI approves the implementation
    And the PR changed 4 files
    When the approval comment is generated
    Then the comment should include a summary for each reviewed file
    And each file summary should note which spec requirements it satisfies
