from pathlib import Path

import yaml

from tdmctl.core import Context


class ContextNotFoundError(Exception):
    pass


class ContextEarlyError(Exception):
    pass


class ContextManager:
    context_file: str
    context_path: str
    current: Context
    context_list: list[Context]

    def __init__(self):
        self.context_file = "config.yaml"
        self.context_path = f"{Path.home()}/.tdmctl/"
        self.current = None
        self.context_list = []

        if not Path(self.context_path).exists():
            Path(self.context_path).mkdir(parents=True)

        if not Path(self.context_path + self.context_file).exists():
            self.save()
        else:
            self.load()

    def save(self):
        data = {"context": [], "current_context": None}

        for context in self.context_list:
            data["context"].append(context.to_dict())

        if self.current:
            data["current_context"] = self.current.name

        with open("{}{}".format(self.context_path, self.context_file), "w") as f:
            yaml.dump(data, f)

    def load(self):
        with open(self.context_path + self.context_file, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.context_list = []
        for context in data["context"]:
            self.context_list.append(Context(**context))

        self.current = None
        if data.get("current_context"):
            self.current = self.get_context(data["current_context"])

    def get_context(self, name: str) -> Context:
        for context in self.context_list:
            if context.name == name:
                return context
        raise ContextNotFoundError("Context {} not found".format(name))

    def set_context(self, name: str):
        self.current = self.get_context(name)
        self.save()

    def add_context(self, name: str, host: str, user: str, passwd: str, set_current=False):
        for context in self.context_list:
            if context.name == name:
                raise ContextEarlyError("Context {} already exists".format(name))
        self.context_list.append(Context(name, host, user, passwd))
        self.save()
        if set_current:
            self.set_context(name)

    def del_context(self, context: Context):
        self.context_list.remove(context)
        if self.current == context:
            self.current = None
        self.save()
