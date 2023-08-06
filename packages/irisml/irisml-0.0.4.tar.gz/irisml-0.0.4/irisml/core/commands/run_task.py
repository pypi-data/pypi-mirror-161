import argparse
import json
import pathlib
import pickle
from irisml.core import Context, Task, TaskDescription
from irisml.core.commands.common import configure_logger


class KeyValuePairAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        assert len(values) == 1
        k, v = values[0].split('=', 2)
        dest = getattr(args, self.dest, None)
        if not dest:
            dest = {}
            setattr(args, self.dest, dest)

        dest[k] = v


def main():
    """TODO This method is WIP."""
    configure_logger()
    parser = argparse.ArgumentParser(description="Run a single task")
    parser.add_argument('task_name')
    parser.add_argument('--inputs', help="JSON-encoded inputs.")
    parser.add_argument('--inputs_pickle', nargs=1, action=KeyValuePairAction, metavar='KEY=VALUE', help="Add a serialized object to the inputs.")
    parser.add_argument('--inputs_bytes', nargs=1, action=KeyValuePairAction, metavar='KEY=VALUE', help="Add a bytes oject to the inputs.")
    parser.add_argument('--config', help="JSON-encoded task configs.")

    args = parser.parse_args()

    task_dict = {'task': args.task_name, 'inputs': {}}

    if args.inputs:
        task_dict['inputs'] = json.loads(args.inputs)

    if args.inputs_pickle:
        for key, value in args.inputs_pickle.items():
            data = pickle.loads(pathlib.Path(value).read_bytes())
            task_dict['inputs'][key] = data

    if args.inputs_bytes:
        for key, value in args.inputs_bytes.items():
            data = pathlib.Path(value).read_bytes()
            task_dict['inputs'][key] = data

    if args.config:
        task_dict['config'] = json.loads(args.config)

    task_description = TaskDescription.from_dict(task_dict)
    context = Context()
    task = Task(task_description)
    task.load_module()
    outputs = task.execute(context)
    print(outputs)
