from offle_assistant.config import Config


def config_command(args, config_path):
    if args.validate is True:
        config = Config(config_path)
        print(config)
