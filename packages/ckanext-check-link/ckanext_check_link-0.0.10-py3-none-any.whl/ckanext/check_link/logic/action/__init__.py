from . import check, report


def get_actions():
    return {
        **check.get_actions(),
        **report.get_actions(),
    }
