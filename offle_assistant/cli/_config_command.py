from offle_assistant.config import Config


def config_command(
    args,
    config: Config
):
    if args.validate is True:
        print(config)
