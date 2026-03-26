Feature: PR Gate — Content Classification
  As a repository maintainer
  I want PRs to be classified by content type
  So that only spec/doc PRs are allowed in the first iteration

  Background:
    Given the action is configured with default settings
    And "spec_extensions" is ".md,.feature"
    And "doc_extensions" is ".txt,.rst,.adoc"

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
