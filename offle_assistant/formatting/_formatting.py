class Formatting:
    def __init__(self, formatting_config=None):
        default_color = "red"

        if formatting_config is not None:
            self.user_color = formatting_config.get(
                "user_color",
                default_color
            )
            self.persona_color = formatting_config.get(
                "persona_color",
                default_color
            )
        else:
            self.user_color = default_color
            self.persona_color = default_color
