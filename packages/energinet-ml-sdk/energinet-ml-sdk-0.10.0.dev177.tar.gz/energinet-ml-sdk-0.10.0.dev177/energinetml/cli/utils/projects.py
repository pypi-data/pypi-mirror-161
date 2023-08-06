#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
from __future__ import annotations

import os
from typing import Callable, Iterable, Union

import click

from energinetml.backend import default_backend as backend
from energinetml.core.backend import BackendException

# -- Helper classes ----------------------------------------------------------


class ArbitraryChoice(click.Choice):
    """
    An implementation of Click.Choice (for prompting for values) that allows
    the user to enter values which is outside the pre-defined range of choices.

    The pre-defined range of choices can be considered suggestions instead of
    absolute options.
    """

    def get_missing_message(self, param: click.Parameter) -> str:
        """[summary]

        Args:
            param (click.Parameter): [description]

        Returns:
            str: [description]
        """
        return f"{super().get_missing_message(param)} (or enter another value)"

    def convert(
        self,
        value: Union[str, int, float, bool],
        param: click.Parameter,
        ctx: click.Context,
    ) -> ArbitraryChoice:
        """[summary]

        Args:
            value (Union[str, int, float, bool]): [description]
            param (click.Parameter): [description]
            ctx (click.Context): [description]

        Returns:
            ArbitraryChoice: [description]
        """
        try:
            return super().convert(value, param, ctx)
        except click.BadParameter:
            return value


# -- Command parameter parsing -----------------------------------------------


def parse_input_path(project_files: Iterable[str]) -> Callable:
    """[summary]

    Args:
        project_files (Iterable[str]): [description]

    Returns:
        Callable: [description]
    """

    def _parse_input_path(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> str:
        """[summary]

        Args:
            ctx (click.Context): [description]
            param (click.Parameter): [description]
            value (str): [description]

        Raises:
            click.Abort: [description]

        Returns:
            str: [description]
        """
        if value is None:
            value = os.path.abspath(
                click.prompt(
                    text="Enter project location",
                    default=os.path.abspath("."),
                    type=click.Path(dir_okay=True, resolve_path=True),
                )
            )

        # Path points to a file?
        if os.path.isfile(value):
            click.echo("Failed to init project.")
            click.echo(
                "The path you provided me with points to a file, and not a "
                "folder. I need a folder to put the project files in. "
                "Check your -p/--path parameter."
            )
            click.echo("You provided me with: %s" % value)
            raise click.Abort()

        # Confirm overwrite files if they exists
        for filename in project_files:
            if os.path.isfile(os.path.join(value, filename)):
                click.echo("File already exists: %s" % os.path.join(value, filename))
                if not click.confirm("Really override existing %s?" % filename):
                    raise click.Abort()

        return value

    return _parse_input_path


def parse_input_project_name() -> Callable:
    """[summary]

    Returns:
        Callable: [description]
    """

    def _parse_input_project_name(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> str:
        """[summary]

        Args:
            ctx (click.Context): [description]
            param (click.Parameter): [description]
            value (str): [description]

        Returns:
            str: [description]
        """
        if value is None:
            default = (
                os.path.split(ctx.params["path"])[1] if ctx.params.get("path") else None
            )

            value = click.prompt(
                text="Please enter a project name", default=default, type=str
            )

        return value

    return _parse_input_project_name


def parse_input_subscription_id() -> Callable:
    """[summary]

    Returns:
        Callable: [description]
    """

    def _parse_input_subscription_id(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> str:
        """[summary]

        Args:
            ctx (click.Context): [description]
            param (click.Parameter): [description]
            value (str): [description]

        Returns:
            str: [description]
        """
        subscriptions = backend.get_available_subscriptions()
        subscriptions_mapped = {
            s.display_name: s.subscription_id for s in subscriptions
        }

        if value not in subscriptions_mapped:
            if value is not None:
                click.echo(f"Azure Subscription '{value}' not found")

            value = click.prompt(
                text="Please enter Azure Subscription",
                type=click.Choice(subscriptions_mapped.keys()),
            )

        return subscriptions_mapped[value]

    return _parse_input_subscription_id


def parse_input_resource_group() -> Callable:
    """[summary]

    Returns:
        Callable: [description]
    """

    def _parse_input_resource_group(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> str:
        """[summary]

        Args:
            ctx (click.Context): [description]
            param (click.Parameter): [description]
            value (str): [description]

        Returns:
            str: [description]
        """
        if "subscription_id" in ctx.params:
            subscription_id = ctx.params["subscription_id"]
            resource_groups = backend.get_available_resource_groups(subscription_id)
            resource_group_names = [g.name for g in resource_groups]
        else:
            resource_group_names = []

        if value is None or (
            resource_group_names and value not in resource_group_names
        ):

            if value is not None:
                click.echo(f"Azure Resource Group '{value}' not found")

            value = click.prompt(
                text="Please enter Azure Resource Group",
                default="",
                type=(
                    click.Choice(resource_group_names) if resource_group_names else str
                ),
            )

        return value

    return _parse_input_resource_group


def parse_input_workspace_name() -> Callable:
    """[summary]

    Returns:
        Callable: [description]
    """

    def parse_input_workspace_name(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> str:
        """[summary]

        Args:
            ctx (click.Context): [description]
            param (click.Parameter): [description]
            value (str): [description]

        Raises:
            RuntimeError: [description]
            click.Abort: [description]

        Returns:
            str: [description]
        """
        if "subscription_id" not in ctx.params:
            raise RuntimeError('Requires a "subscription_id" parameter')
        if "resource_group" not in ctx.params:
            raise RuntimeError('Requires a "resource_group" parameter')

        if value is None:
            existing_workspaces = backend.get_available_workspace_names(
                subscription_id=ctx.params["subscription_id"],
                resource_group=ctx.params["resource_group"],
            )

            value = click.prompt(
                text="Please enter AzureML Workspace name",
                default=existing_workspaces[0] if existing_workspaces else None,
                type=ArbitraryChoice(existing_workspaces)
                if existing_workspaces
                else str,  # noqa: E501
            )

        project_meta = {
            "subscription_id": ctx.params["subscription_id"],
            "resource_group": ctx.params["resource_group"],
            "workspace_name": value,
        }
        try:
            backend.get_workspace(project_meta)
        except BackendException:
            click.echo(
                'Workspace "{}" not found in resource group: {}'.format(
                    value, ctx.params["resource_group"]
                )
            )
            raise click.Abort()

        return value

    return parse_input_workspace_name


def parse_input_service_connection() -> Callable:
    """[summary]

    Returns:
        Callable: [description]
    """

    def _parse_input_service_connection(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> str:
        """[summary]

        Args:
            ctx (click.Context): [description]
            param (click.Parameter): [description]
            value (str): [description]

        Returns:
            str: [description]
        """
        if value is None:
            value = click.prompt(
                text="Please enter DevOps Service Connection name", default="", type=str
            )
        return value

    return _parse_input_service_connection


def parse_input_webapp_kind() -> Callable:
    """[summary]

    Returns:
        Callable: [description]
    """

    def _parse_input_webapp_kind(
        ctx: click.Context, param: click.Parameter, value: str
    ) -> str:
        """[summary]

        Args:
            ctx (click.Context): [description]
            param (click.Parameter): [description]
            value (str): [description]

        Returns:
            str: [description]
        """
        if value is None:
            click.echo("-" * 79)
            click.echo("Select which kind of webserver you will use.")
            click.echo("This option can be changed later.")
            click.echo("")
            click.echo("For apps written in flask, Django, or Dash select WSGI.")
            click.echo("For apps written in fastapi select ASGI.")
            click.echo("")
            value = click.prompt(
                text="Please enter webserver kind",
                default=None,
                type=click.Choice(["ASGI", "WSGI"]),
            )
        return value

    return _parse_input_webapp_kind
