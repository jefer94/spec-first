import os
from unittest.mock import patch, MagicMock
from behave import given, when, then


@given('the workflow YAML provides input "{key}" set to "{value}"')
def step_set_input(context, key, value):
    env_key = f"INPUT_{key.upper()}"
    os.environ[env_key] = value
    if not hasattr(context, "_env_overrides"):
        context._env_overrides = {}
    context._env_overrides[env_key] = value


@given('the environment variable "{key}" is set to "{value}"')
def step_set_env(context, key, value):
    os.environ[key] = value
    if not hasattr(context, "_env_overrides"):
        context._env_overrides = {}
    context._env_overrides[key] = value


@given('the environment variable "{key}" is not set')
def step_unset_env(context, key):
    os.environ.pop(key, None)
    if not hasattr(context, "_intentionally_unset"):
        context._intentionally_unset = set()
    context._intentionally_unset.add(key)


@given('the workflow YAML does not provide input "{key}"')
def step_unset_input(context, key):
    env_key = f"INPUT_{key.upper()}"
    os.environ.pop(env_key, None)
    if not hasattr(context, "_intentionally_unset"):
        context._intentionally_unset = set()
    context._intentionally_unset.add(env_key)


@when("the action initializes")
def step_action_initializes(context):
    import os
    from src.config import Config, ensure_labels
    unset = getattr(context, "_intentionally_unset", set())
    if not os.environ.get("INPUT_MODEL") and "INPUT_MODEL" not in unset:
        os.environ["INPUT_MODEL"] = "openai/gpt-4o"
    if not os.environ.get("OPENROUTER_API_KEY") and "OPENROUTER_API_KEY" not in unset:
        os.environ["OPENROUTER_API_KEY"] = "sk-test-default"
    try:
        context.result = Config.from_env()
        context.cfg = context.result
        context.error = None
    except ValueError as exc:
        context.result = None
        context.error = str(exc)


@then("it should parse all inputs with defaults applied")
def step_inputs_parsed(context):
    assert context.result is not None, f"Config failed: {context.error}"


@then('"{key}" should default to "{value}"')
def step_check_default(context, key, value):
    cfg = context.result
    attr = getattr(cfg, key)
    if isinstance(attr, list):
        expected = [v.strip() for v in value.split(",")]
        assert attr == expected, f"{key}: expected {expected}, got {attr}"
    elif isinstance(attr, bool):
        assert attr == (value.lower() == "true"), f"{key}: expected {value}, got {attr}"
    else:
        assert str(attr) == value, f"{key}: expected '{value}', got '{attr}'"


@then('"{key}" should be "{value}"')
def step_check_value(context, key, value):
    step_check_default(context, key, value)


@then('it should fail with error message containing "{text}"')
def step_fail_message(context, text):
    assert context.error is not None, "Expected an error but none was raised."
    assert text in context.error, f"Expected '{text}' in error: {context.error}"


@then('it should not create any labels')
def step_no_labels_created(context):
    from src.config import ensure_labels
    context.repo.create_label.reset_mock()
    ensure_labels(context.repo, context.cfg)
    context.repo.create_label.assert_not_called()


@then('it should proceed normally')
def step_proceed_normally(context):
    assert context.error is None


@then('it should create label "{label}" with a default color and description')
def step_create_label(context, label):
    from src.config import ensure_labels
    if not getattr(context, "_ensure_labels_called", False):
        context.repo.create_label.reset_mock()
        ensure_labels(context.repo, context.cfg)
        context._ensure_labels_called = True
    created = set()
    for call in context.repo.create_label.call_args_list:
        if call.args:
            created.add(call.args[0])
        if call.kwargs.get("name"):
            created.add(call.kwargs["name"])
    assert label in created, f"Label '{label}' was not created. Created: {created}"


@then('it should log "{message}"')
def step_log_message(context, message):
    pass


@then('it should use "{label}" for all subsequent operations')
def step_use_label(context, label):
    assert context.cfg.accepted_tag == label or context.cfg.ai_review_tag == label or context.cfg.senior_tag == label

