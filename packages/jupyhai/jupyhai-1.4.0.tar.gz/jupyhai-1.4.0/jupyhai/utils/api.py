from typing import Optional

from valohai_cli.settings import settings

from jupyhai._version import __version__


def configure_user_agent_header(frontend: Optional[str] = None) -> None:
    """
    Configure valohai-cli's api-user-agent-prefix setting.
    """
    bits = [
        f'jupyhai/{__version__}'
    ]
    if frontend:
        # Currently `jupyterlab` or `notebook`.
        bits.append(f'jupyhai-{frontend}')
    settings.api_user_agent_prefix = ' '.join(bits)  # type: ignore[assignment]
