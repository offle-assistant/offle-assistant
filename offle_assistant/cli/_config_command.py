from offle_assistant.config import OffleConfig


def config_command(
    args,
    config: OffleConfig
):
    if args.validate is True:
        print(config)
