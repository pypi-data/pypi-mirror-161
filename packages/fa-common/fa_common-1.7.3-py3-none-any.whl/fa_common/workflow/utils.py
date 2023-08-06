import oyaml as yaml
from fastapi import FastAPI

from fa_common import get_current_app, get_settings, logger


def setup_gitlab(app: FastAPI) -> None:
    """
    Helper function to setup MongoDB connection & `motor` client during setup.
    Use during app startup as follows:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            setup_mongodb(app)

    :param app: app object, instance of FastAPI
    :return: None
    """
    settings = get_settings()
    if (
        settings.GITLAB_PRIVATE_TOKEN is not None
        and settings.GITLAB_URL is not None
        and settings.GITLAB_GROUP_ID is not None
    ):
        import gitlab

        gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_PRIVATE_TOKEN)
        app.gitlab = gl  # type:ignore
        logger.info("Gitlab client has been setup")

    else:
        raise ValueError(
            "Insufficient configuration to create gitlab client need (GITLAB_URL, GITLAB_PRIVATE_TOKEN and "
            + "GITLAB_GROUP_ID)."
        )


def get_workflow_client():
    """
    Gets instance of GitlabClient for you to make gitlab calls.
    :return: GitlabClient
    """
    try:
        app = get_current_app()
        if app.gitlab is not None:
            from .client import GitlabClient

            return GitlabClient()
    except Exception:
        raise ValueError("Problem returning gitlab client, may not be initialised.")
    raise ValueError("Gitlab client has not been initialised.")


class GitlabCIYAMLDumper(yaml.Dumper):
    """Correctly dumps yaml for gitlab ci formatting

    Arguments:
        yaml {[type]} -- [description]
    """

    def increase_indent(self, flow=False, indentless=False):
        return super(GitlabCIYAMLDumper, self).increase_indent(flow, False)
