from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from llm_debate_hall.local_boundary import LocalOnlyMiddleware, is_loopback_client  # noqa: F401
from llm_debate_hall.config import custom_commands_enabled
from llm_debate_hall.models import BackendPresetModel


def backend_overrides_requested(
    preset: BackendPresetModel,
    *,
    command: list[str],
    args_template: list[str],
    env: dict[str, str],
) -> bool:
    return (
        command != preset.command or args_template != preset.args_template or bool(env)
    )


def assert_backend_configuration_is_safe(
    preset: BackendPresetModel,
    *,
    command: list[str],
    args_template: list[str],
    env: dict[str, str],
) -> None:
    if not backend_overrides_requested(
        preset,
        command=command,
        args_template=args_template,
        env=env,
    ):
        return
    if custom_commands_enabled():
        return
    raise HTTPException(
        status_code=403,
        detail=(
            "Custom command, argument, and environment overrides are disabled. "
            "Use a built-in provider configuration and set credentials in the server shell, or explicitly set "
            "MULTI_AGENT_COUNCIL_ENABLE_CUSTOM_COMMANDS=true for trusted local development."
        ),
    )


def redact_agent_environment(agent: dict[str, Any]) -> dict[str, Any]:
    public_agent = {**agent}
    environment = public_agent.get("env") or {}
    public_agent["env"] = {}
    public_agent["env_keys"] = sorted(str(name) for name in environment)
    return public_agent
