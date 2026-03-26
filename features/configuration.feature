Feature: Action Configuration
  As a repository maintainer
  I want the Spec Guard action to validate its configuration on startup
  So that misconfigured workflows fail fast with clear error messages

  Scenario: Valid configuration with all defaults
    Given the workflow YAML provides input "model" set to "openai/gpt-4o"
    And the environment variable "OPENROUTER_API_KEY" is set to "sk-test-123"
    When the action initializes
    Then it should parse all inputs with defaults applied
    And "spec_extensions" should default to ".md,.feature"
    And "doc_extensions" should default to ".txt,.rst,.adoc"
    And "accepted_tag" should default to "specs-accepted"
    And "ai_review_tag" should default to "ai-review"
    And "senior_tag" should default to "senior-review"
    And "authorized_roles" should default to "maintain,admin"

  Scenario: Valid configuration with custom overrides
    Given the workflow YAML provides input "model" set to "anthropic/claude-3.5-sonnet"
    And the environment variable "OPENROUTER_API_KEY" is set to "sk-test-456"
    And the workflow YAML provides input "accepted_tag" set to "approved-specs"
    And the workflow YAML provides input "spec_extensions" set to ".md,.feature,.gherkin"
    When the action initializes
    Then "accepted_tag" should be "approved-specs"
    And "spec_extensions" should be ".md,.feature,.gherkin"

  Scenario: Missing model input
    Given the workflow YAML does not provide input "model"
    And the environment variable "OPENROUTER_API_KEY" is set to "sk-test-123"
    When the action initializes
    Then it should fail with error message containing "model"

  Scenario: Missing API key
    Given the workflow YAML provides input "model" set to "openai/gpt-4o"
    And the environment variable "OPENROUTER_API_KEY" is not set
    When the action initializes
    Then it should fail with error message containing "OPENROUTER_API_KEY"

  Scenario: Labels already exist in the repository
    Given the repository has label "specs-accepted"
    And the repository has label "ai-review"
    And the repository has label "senior-review"
    When the action initializes
    Then it should not create any labels
    And it should proceed normally

  Scenario: Labels do not exist in the repository
    Given the repository does not have label "specs-accepted"
    And the repository does not have label "ai-review"
    And the repository does not have label "senior-review"
    When the action initializes
    Then it should create label "specs-accepted" with a default color and description
    And it should create label "ai-review" with a default color and description
    And it should create label "senior-review" with a default color and description
    And it should log "Created label: specs-accepted"
    And it should log "Created label: ai-review"
    And it should log "Created label: senior-review"

  Scenario: Custom tag names trigger auto-creation
    Given the workflow YAML provides input "accepted_tag" set to "approved-specs"
    And the repository does not have label "approved-specs"
    When the action initializes
    Then it should create label "approved-specs" with a default color and description
    And it should use "approved-specs" for all subsequent operations
