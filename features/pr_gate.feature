Feature: PR Gate — Content Classification
  As a repository maintainer
  I want PRs to be classified by content type
  So that only spec/doc PRs are allowed in the first iteration

  Background:
    Given the action is configured with default settings
    And "spec_extensions" is ".md,.feature"
    And "doc_extensions" is ".txt,.rst,.adoc"
    And "accepted_tag" is "specs-accepted"
    And "ai_review_tag" is "ai-review"
    And "senior_tag" is "senior-review"

  Scenario: Labels are auto-created if missing
    Given the repository does not have label "specs-accepted"
    And the repository does not have label "ai-review"
    And the repository does not have label "senior-review"
    When the action initializes
    Then the label "specs-accepted" should be created
    And the label "ai-review" should be created
    And the label "senior-review" should be created

  Scenario: Labels already exist are not recreated
    Given the repository has label "specs-accepted"
    And the repository has label "ai-review"
    And the repository has label "senior-review"
    When the action initializes
    Then no labels should be created

  Scenario: PR contains only spec files
    Given a PR is opened with changed files:
      | file                    |
      | specs/auth.md           |
      | specs/payments.feature  |
    When the action runs on "pull_request.opened"
    Then the PR should remain open
    And a comment should be posted acknowledging the spec submission

  Scenario: PR contains only doc files
    Given a PR is opened with changed files:
      | file              |
      | docs/readme.txt   |
      | docs/guide.rst    |
    When the action runs on "pull_request.opened"
    Then the PR should remain open

  Scenario: PR contains spec and doc files mixed
    Given a PR is opened with changed files:
      | file                    |
      | specs/auth.md           |
      | docs/readme.txt         |
      | specs/payments.feature  |
    When the action runs on "pull_request.opened"
    Then the PR should remain open

  Scenario: PR contains no spec files at all
    Given a PR is opened with changed files:
      | file              |
      | src/main.py       |
      | src/utils.py      |
    When the action runs on "pull_request.opened"
    Then the PR should be closed
    And the conversation should be locked
    And a comment should be posted using the "msg_no_specs" template
    And the comment should list accepted extensions ".md,.feature"
    And the comment should reference the SDD workflow

  Scenario: PR mixes spec files and code files
    Given a PR is opened with changed files:
      | file                    |
      | specs/auth.md           |
      | src/auth.py             |
      | specs/payments.feature  |
    When the action runs on "pull_request.opened"
    Then the PR should be closed
    And the conversation should be locked
    And a comment should be posted using the "msg_mixed_pr" template

  Scenario: PR is synchronized with only spec files
    Given an existing open PR
    And new commits are pushed with changed files:
      | file                   |
      | specs/auth-v2.md       |
    When the action runs on "pull_request.synchronize"
    Then the PR should remain open

  Scenario: PR is synchronized adding code to a spec PR
    Given an existing open PR that originally had only spec files
    And new commits are pushed with changed files:
      | file              |
      | src/auth.py       |
      | specs/auth.md     |
    When the action runs on "pull_request.synchronize"
    Then the PR should be closed
    And the conversation should be locked
    And a comment should be posted using the "msg_mixed_pr" template

  # --- review_on_pr auto-trigger ---

  Scenario: Code PR auto-triggers AI review when review_on_pr is true
    Given "review_on_pr" is "true"
    And a PR is opened with changed files:
      | file              |
      | src/auth.py       |
      | src/utils.py      |
    And the PR body contains "Implements #42"
    And PR #42 has the label "specs-accepted"
    When the action runs on "pull_request.opened"
    Then the AI review should be automatically triggered
    And the "ai_review_tag" label should not be required

  Scenario: Code PR does not auto-trigger when review_on_pr is false
    Given "review_on_pr" is "false"
    And a PR is opened with changed files:
      | file              |
      | src/auth.py       |
    And the PR body contains "Implements #42"
    When the action runs on "pull_request.opened"
    Then the AI review should not be triggered

  Scenario: Code PR without spec reference does not auto-trigger
    Given "review_on_pr" is "true"
    And a PR is opened with changed files:
      | file              |
      | src/auth.py       |
    And the PR body does not reference any spec PR
    When the action runs on "pull_request.opened"
    Then the PR should be closed
    And a comment should be posted using the "msg_no_specs" template
