import dataclasses
import itertools
import logging
import typing
import irisml.core


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SearchSpaceConfig:
    name: str
    candidates: typing.List[typing.Union[int, float, str]]


class Task(irisml.core.TaskBase):
    """Grid search hyperparameters. Tasks are run in sequence.

       In the search loop, new combination of hyperparameters will be set to environment variables.

       After the search loop, the best iteration will be selected and added to the context.
    """
    VERSION = '0.1.0'
    CACHE_ENABLED = False
    RESOLVE_CONFIG_VARIABLES = False

    @dataclasses.dataclass
    class Config:
        search_space: typing.List[SearchSpaceConfig]
        tasks: typing.List[irisml.core.TaskDescription]
        metrics_output_name: str

    @dataclasses.dataclass
    class Outputs:
        best_parameters: typing.Dict[str, typing.Union[int, float, str]] = dataclasses.field(default_factory=dict)

    def execute(self, inputs):
        return self.execute_task(inputs, False)

    def execute_task(self, inputs, dry_run):
        if not self.config.search_space:
            return self.Outputs()

        parameter_names = [x.name for x in self.config.search_space]
        parameter_combinations = list(itertools.product(*[x.candidates for x in self.config.search_space]))

        logger.info(f"Trying {len(parameter_combinations)} combinations...")

        tasks = []
        for task_description in self.config.tasks:
            task = irisml.core.Task(task_description)
            task.load_module()
            tasks.append(task)

        best_results = None  # Metrics, Context object
        metrics_output_task_name, metrics_output_variable_name = self.config.metrics_output_name.split('.')
        for params in parameter_combinations:
            selected_parameters = dict(zip(parameter_names, params))
            logger.info(f"Trying params: {selected_parameters}")
            context = self.context.clone()
            for name, value in selected_parameters.items():
                context.add_environment_variable(name, value)

            for task in tasks:
                task.execute(context) if not dry_run else task.dry_run(context)

            metrics = getattr(context.get_outputs(metrics_output_task_name), metrics_output_variable_name)
            logger.debug(f"Result was {metrics} with {selected_parameters}")
            if not best_results or best_results[0] < metrics:
                best_results = (metrics, selected_parameters, context)

        logger.info(f"Best result is {best_results[0]} with parameters {best_results[1]}")

        # Add the outputs from the best trial to the current context.
        for task in tasks:
            self.context.add_outputs(task.name, best_results[2].get_outputs(task.name))

        return self.Outputs(best_results[1])

    def dry_run(self, inputs):
        return self.execute_task(inputs, True)
