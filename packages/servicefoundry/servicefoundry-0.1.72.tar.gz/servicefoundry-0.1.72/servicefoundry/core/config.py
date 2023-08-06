from servicefoundry.lib import context


def use_server(url: str):
    context.use_server(url=url)
