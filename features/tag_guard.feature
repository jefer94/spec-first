Feature: Tag Guard — Authorization
  As a repository maintainer
  I want only authorized roles to accept specs
  So that unauthorized users cannot bypass the review process

  Background:
    Given the action is configured with default settings
    And "authorized_roles" is "maintain,admin"
    And "accepted_tag" is "specs-accepted"

  Scenario: Maintainer applies accepted tag to a spec PR
    Given a PR exists with only spec files
    And user "lead-dev" has "maintain" permission on the repository
    When user "lead-dev" adds the label "specs-accepted"
    Then the label should remain on the PR
    And the PR should remain open
    And no enforcement action should be taken

  Scenario: Admin applies accepted tag to a spec PR
    Given a PR exists with only spec files
    And user "repo-owner" has "admin" permission on the repository
    When user "repo-owner" adds the label "specs-accepted"
    Then the label should remain on the PR
    And the PR should remain open

  Scenario: Contributor applies accepted tag
    Given a PR exists with only spec files
    And user "junior-dev" has "write" permission on the repository
    When user "junior-dev" adds the label "specs-accepted"
    Then the label "specs-accepted" should be removed
    And the PR should be closed
    And a comment should be posted using the "msg_unauthorized_tag" template
    And the comment should name the required roles "maintain,admin"

  Scenario: Read-only user applies accepted tag
    Given a PR exists with only spec files
    And user "external-user" has "read" permission on the repository
    When user "external-user" adds the label "specs-accepted"
    Then the label "specs-accepted" should be removed
    And the PR should be closed
    And a comment should be posted using the "msg_unauthorized_tag" template

  Scenario: Authorized user applies accepted tag to a code-only PR
    Given a PR exists with only code files
    And user "lead-dev" has "maintain" permission on the repository
    When user "lead-dev" adds the label "specs-accepted"
    Then the label "specs-accepted" should be removed
    And the PR should be closed
    And a comment should be posted using the "msg_no_specs_on_tag" template

  Scenario: Custom authorized roles
    Given the action is configured with "authorized_roles" set to "admin"
    And a PR exists with only spec files
    And user "lead-dev" has "maintain" permission on the repository
    When user "lead-dev" adds the label "specs-accepted"
    Then the label "specs-accepted" should be removed
    And the PR should be closed
    And a comment should be posted using the "msg_unauthorized_tag" template
    And the comment should name the required roles "admin"
