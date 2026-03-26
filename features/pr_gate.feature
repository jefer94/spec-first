Feature: PR Gate — Content Classification
  As a repository maintainer
  I want PRs to enforce SDD by requiring specs with code
  So that every code change is backed by specifications

  Background:
    Given the action is configured with default settings
    And "spec_extensions" is ".md,.feature"
    And "doc_extensions" is ".txt,.rst,.adoc"
    And "accepted_tag" is "specs-accepted"
    And "ai_review_tag" is "ai-review"
    And "senior_tag" is "senior-review"
    And "bypass_roles" is "maintain,admin"

  # --- Label Auto-Creation ---

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

  # --- Content Classification ---

  Scenario: PR contains only spec files
    Given a PR is opened by user "contributor" with "write" permission
    And the PR has changed files:
      | file                    |
      | specs/auth.md           |
      | specs/payments.feature  |
    When the action runs on "pull_request.opened"
    Then the PR should remain open
    And a comment should be posted acknowledging the spec submission

  Scenario: PR contains only doc files
    Given a PR is opened by user "contributor" with "write" permission
    And the PR has changed files:
      | file              |
      | docs/readme.txt   |
      | docs/guide.rst    |
    When the action runs on "pull_request.opened"
    Then the PR should remain open

  Scenario: PR contains spec and doc files
    Given a PR is opened by user "contributor" with "write" permission
    And the PR has changed files:
      | file                    |
      | specs/auth.md           |
      | docs/readme.txt         |
      | specs/payments.feature  |
    When the action runs on "pull_request.opened"
    Then the PR should remain open

  Scenario: PR contains code AND spec files together
    Given a PR is opened by user "contributor" with "write" permission
    And the PR has changed files:
      | file                    |
      | specs/auth.md           |
      | src/auth.py             |
      | specs/payments.feature  |
    When the action runs on "pull_request.opened"
    Then the PR should remain open
    And a comment should be posted acknowledging that specs accompany the code

  Scenario: PR contains only code files — no specs — by contributor
    Given a PR is opened by user "junior-dev" with "write" permission
    And the PR has changed files:
      | file              |
      | src/main.py       |
      | src/utils.py      |
    When the action runs on "pull_request.opened"
    Then the PR should be closed
    And the conversation should be locked
    And a comment should be posted using the "msg_no_specs" template
    And the comment should list accepted extensions ".md,.feature"
    And the comment should reference the SDD workflow

  Scenario: Synchronized PR adds code without specs
    Given an existing open PR by user "contributor" with "write" permission
    And new commits are pushed with changed files:
      | file              |
      | src/auth.py       |
    When the action runs on "pull_request.synchronize"
    Then the PR should be closed
    And the conversation should be locked
    And a comment should be posted using the "msg_no_specs" template

  Scenario: Synchronized PR adds code with specs
    Given an existing open PR by user "contributor" with "write" permission
    And new commits are pushed with changed files:
      | file              |
      | src/auth.py       |
      | specs/auth.md     |
    When the action runs on "pull_request.synchronize"
    Then the PR should remain open

  # --- Bypass SDD Enforcement ---

  Scenario: Maintainer submits code-only PR — bypass allowed
    Given a PR is opened by user "lead-dev" with "maintain" permission
    And the PR has changed files:
      | file              |
      | src/hotfix.py     |
    When the action runs on "pull_request.opened"
    Then the PR should remain open
    And a comment should note SDD enforcement was bypassed due to the author's role

  Scenario: Admin submits code-only PR — bypass allowed
    Given a PR is opened by user "repo-owner" with "admin" permission
    And the PR has changed files:
      | file              |
      | src/infra.py      |
    When the action runs on "pull_request.opened"
    Then the PR should remain open

  Scenario: Contributor cannot bypass SDD enforcement
    Given a PR is opened by user "junior-dev" with "write" permission
    And the PR has changed files:
      | file              |
      | src/feature.py    |
    When the action runs on "pull_request.opened"
    Then the PR should be closed
    And a comment should be posted using the "msg_no_specs" template

  Scenario: Read-only user cannot bypass SDD enforcement
    Given a PR is opened by user "external" with "read" permission
    And the PR has changed files:
      | file              |
      | src/feature.py    |
    When the action runs on "pull_request.opened"
    Then the PR should be closed
    And a comment should be posted using the "msg_no_specs" template

  Scenario: Custom bypass_roles excludes maintainers
    Given "bypass_roles" is "admin"
    And a PR is opened by user "lead-dev" with "maintain" permission
    And the PR has changed files:
      | file              |
      | src/hotfix.py     |
    When the action runs on "pull_request.opened"
    Then the PR should be closed
    And a comment should be posted using the "msg_no_specs" template

  # --- review_on_pr auto-trigger ---

  Scenario: Code+spec PR auto-triggers AI review when review_on_pr is true
    Given "review_on_pr" is "true"
    And a PR is opened by user "contributor" with "write" permission
    And the PR has changed files:
      | file              |
      | src/auth.py       |
      | specs/auth.md     |
    And the PR body contains "Implements #42"
    And PR #42 has the label "specs-accepted"
    When the action runs on "pull_request.opened"
    Then the AI review should be automatically triggered
    And the "ai_review_tag" label should not be required

  Scenario: Code+spec PR does not auto-trigger when review_on_pr is false
    Given "review_on_pr" is "false"
    And a PR is opened by user "contributor" with "write" permission
    And the PR has changed files:
      | file              |
      | src/auth.py       |
      | specs/auth.md     |
    When the action runs on "pull_request.opened"
    Then the AI review should not be triggered
