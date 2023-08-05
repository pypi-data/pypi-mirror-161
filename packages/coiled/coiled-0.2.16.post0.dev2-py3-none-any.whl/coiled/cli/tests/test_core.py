from coiled.cli.core import cli


def test_available_commands():
    assert set(cli.commands) == set(
        [
            "login",
            "setup",
            "install",
            "upload",
            "env",
            "create-kubeconfig",
            "diagnostics",
        ]
    )
