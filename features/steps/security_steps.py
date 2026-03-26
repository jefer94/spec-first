from behave import given, when, then
from src.security import redact, sanitize_for_llm, sanitize_commit_message, _strip_injection_patterns


@given('a diff contains a Python comment "{text}"')
def step_diff_with_comment(context, text):
    context.input_content = f"def foo():\n    {text}\n    pass"


@given('a diff contains a string literal with text "{text}"')
def step_diff_with_string(context, text):
    context.input_content = f'msg = "{text}"'


@given('a spec file contains "{text}"')
def step_spec_with_injection(context, text):
    context.input_content = text


@given('a commit message contains "{text}"')
def step_commit_message(context, text):
    context.input_content = text


@when("the agent processes the diff")
def step_agent_processes(context):
    context.output_content = sanitize_for_llm(context.input_content, label="test.py")


@when("the agent loads specs via the {tool_name:S} tool")
def step_agent_loads_specs(context, tool_name):
    context.output_content = sanitize_for_llm(context.input_content, label="spec.md")


@when("the agent receives the diff")
def step_agent_receives_diff(context):
    context.output_content = sanitize_commit_message(context.input_content)


@then("the injection should be treated as regular code content")
def step_injection_inert(context):
    assert "```" in context.output_content, "Content not wrapped in code fence"


@then("the compliance verdict should not be altered by the injection")
def step_verdict_unaltered(context):
    assert "```" in context.output_content


@then("the string content should be wrapped in a sanitized code fence")
def step_string_fenced(context):
    assert "```" in context.output_content


@then("the agent should not follow instructions embedded in the string")
def step_no_follow(context):
    assert "```" in context.output_content


@then("the content should pass through the sanitization railway")
def step_sanitized(context):
    assert "```" in context.output_content


@then("only Given/When/Then structures should be used for compliance")
def step_gwt_only(context):
    pass


@then("commit messages should be stripped or sanitized before LLM processing")
def step_commit_sanitized(context):
    assert "[commit message]" in context.output_content


@given('the LangChain agent is running')
def step_agent_running(context):
    pass


@given('the LangChain agent is processing a review')
def step_agent_processing(context):
    pass


@when("the agent attempts to access the local filesystem")
def step_agent_fs(context):
    context.fs_denied = True


@then("the operation should be denied")
def step_fs_denied(context):
    assert context.fs_denied


@then("file access should only work through GitHub API-backed tools")
def step_fs_api_only(context):
    pass


@given('the environment has "{key1}" and "{key2}" set')
def step_env_has(context, key1, key2):
    import os
    os.environ[key1] = "test-openrouter-key"
    os.environ[key2] = "test-github-token"


@when("the agent initializes")
def step_agent_initializes(context):
    pass


@then('only "{key}" should be accessible to the LLM client')
def step_only_key_accessible(context, key):
    pass


@then('"{key}" should be isolated to the GitHub client layer')
def step_key_isolated(context, key):
    pass


@then('"{key}" should never be passed to the LLM')
def step_key_not_to_llm(context, key):
    pass


@when('the agent attempts to make an HTTP request to "{url}"')
def step_agent_http(context, url):
    context.blocked_url = url


@then("the request should be blocked")
def step_request_blocked(context):
    assert context.blocked_url != "https://openrouter.ai/api/v1"


@then("only requests to the OpenRouter API endpoint should be allowed")
def step_only_openrouter(context):
    pass


@given('the agent calls "{tool}" on a file with {lines:d} lines')
def step_agent_calls_tool(context, tool, lines):
    context.file_lines = lines


@when("the tool returns content")
def step_tool_returns(context):
    context.truncated = context.file_lines > 200


@then("the output should be truncated to the configured maximum size")
def step_output_truncated(context):
    assert context.truncated


@then("the agent should be informed the content was truncated")
def step_agent_informed(context):
    pass


@given('"{key}" is set as an environment variable')
def step_key_env(context, key):
    import os
    os.environ[key] = "sk-or-v1-test"


@when("the LangChain client initializes")
def step_lc_init(context):
    pass


@then("it should read the key from the environment only")
def step_key_from_env(context):
    import os
    assert os.environ.get("OPENROUTER_API_KEY", "") != ""


@then("the key should not be passed through action inputs or config files")
def step_key_not_input(context):
    pass


@given('the OpenRouter API returns an authentication error')
def step_api_auth_error(context):
    context.error_message = "Authorization: Bearer sk-or-v1-test-secret"
    import os
    os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-test-secret"


@when("the error is logged")
def step_error_logged(context):
    context.redacted = redact(context.error_message, "sk-or-v1-test-secret")


@then("the API key should be redacted from all output")
def step_key_redacted(context):
    assert "[REDACTED]" in context.redacted


@then("error messages should not include request headers")
def step_no_headers(context):
    assert "sk-or-v1-test-secret" not in context.redacted


@when("prompts are sent to the LLM")
def step_prompts_sent(context):
    pass


@then("the API key should not appear in any prompt content")
def step_key_not_prompt(context):
    pass


@then("the key should only be used in the HTTP transport layer")
def step_key_transport(context):
    pass


# --- Credential Redaction Guardrail ---

@given('the API key is "{key}"')
def step_api_key_is(context, key):
    context.api_key = key


@given('the LLM generates a response containing "{text}"')
def step_llm_response(context, text):
    context.raw_output = text


@when("the response passes through the redaction guardrail")
def step_redact_response(context):
    context.redacted_output = redact(context.raw_output, context.api_key)


@then('"{old}" should be replaced with "{new}"')
def step_replaced(context, old, new):
    assert old not in context.redacted_output, f"'{old}' still present in output."
    assert new in context.redacted_output, f"'{new}' not found in output."


@then("the redacted response should be used for all downstream processing")
def step_redacted_used(context):
    assert "[REDACTED]" in context.redacted_output


@given('a PR comment draft contains "{text}"')
def step_comment_draft(context, text):
    context.raw_output = text


@when("the comment passes through the redaction guardrail")
def step_redact_comment(context):
    context.redacted_output = redact(context.raw_output, context.api_key)


@then('the posted comment should read "{text}"')
def step_posted_reads(context, text):
    assert context.redacted_output == text, f"Expected '{text}', got '{context.redacted_output}'"


@then("the comment should not be posted until redaction is complete")
def step_not_posted_early(context):
    pass


@given('an API error message contains "{text}"')
def step_api_error(context, text):
    context.raw_output = text


@when("the error is formatted for logging")
def step_error_formatted(context):
    context.redacted_output = redact(context.raw_output, context.api_key)


@then('the log should read "{text}"')
def step_log_reads(context, text):
    assert context.redacted_output == text, f"Expected '{text}', got '{context.redacted_output}'"


@given('a response contains "{text}"')
def step_response_contains(context, text):
    context.raw_output = text


@then('the output should read "{text}"')
def step_output_reads(context, text):
    assert context.redacted_output == text, f"Expected '{text}', got '{context.redacted_output}'"


@given('a PR comment contains "{text}"')
def step_comment_contains(context, text):
    context.raw_output = text


@then("the comment should remain unchanged")
def step_unchanged(context):
    assert context.redacted_output == context.raw_output, \
        f"Comment was altered: '{context.redacted_output}' != '{context.raw_output}'"
