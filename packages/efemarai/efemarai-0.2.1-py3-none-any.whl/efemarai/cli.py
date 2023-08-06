import os
import time
from pathlib import Path

import click
import click_completion
from appdirs import user_config_dir
from click_aliases import ClickAliasedGroup
from rich.prompt import Confirm
from rich.table import Table

import efemarai as ef
from efemarai.console import console
from efemarai.definition_checker import DefinitionChecker

click_completion.init()
checker = DefinitionChecker()

default_yaml = "efemarai.yaml"


@click.group()
@click.version_option(ef.__version__)
def main():
    """Efemarai CLI."""
    pass


@main.command()
@click.option("-c", "--config", help="Optional configuration file.")
@click.option(
    "--noinput", is_flag=True, default=False, help="Avoid user input prompts."
)
@click.option("--username", help="Efemarai username.")
@click.option("--url", help="Efemarai URL.")
def init(config, noinput, username, url):
    """Initialize Efemarai."""
    if noinput:
        ef.Session._setup(url, username, password=os.environ.get("EFEMARAI_PASSWORD"))
    else:
        ef.Session._user_setup(config_file=config)


@main.command()
@click.option(
    "-c",
    "--config",
    default=None,
    help=f"Efemarai config filename (Default: '{os.path.join(user_config_dir(appname='efemarai'), 'config.yaml')}')",
)
def status(config):
    """Check the status of the Efemarai system."""
    try:
        config = ef.Session()._read_config(config)
        console.print(
            f"Checking [bold]{config['username']}[/bold] @ {config['url']}",
        )
        # Check status by getting a list of projects
        _ = ef.Session().projects
        console.print(":heavy_check_mark: Status: [bold]Success[/bold]", style="green")
    except Exception as e:
        console.print(":poop: Status: [bold]Fail[/bold]", style="red")
        exit(1)


@main.command()
@click.argument("definition-file", required=True)
@click.option(
    "-a",
    "--all",
    "check_all",
    default=False,
    is_flag=True,
    help="Perform all checks on a complete project definition including models, datasets and domains.",
)
def check(definition_file, check_all):
    """Check if the YAML definition of a project, dataset, model or domain is correct.

    DEFINITION_FILE is the YAML definition file to be checked.
    """
    if definition_file == ".":
        definition_file = default_yaml

    with console.status(f"Checking..."):
        if not checker.check_from_file(definition_file, check_all):
            exit(1)

    console.print(":heavy_check_mark: [bold]No issues detected[/bold]", style="green")


@main.group(cls=ClickAliasedGroup)
def project():
    """Manage projects."""
    pass


@project.command("create")
@click.argument("definition-file", required=True)
@click.option(
    "--exists-ok/--exists-not-ok",
    default=False,
    help="Skip project and its models, datasets, domains if they already exists.",
)
@click.option(
    "-w",
    "--wait",
    default=False,
    is_flag=True,
    help="Wait for any created datasets to be loaded.",
)
@click.option("-v", "--verbose", count=True, help="Print resulting model.")
@click.option(
    "-p",
    "--project-only",
    default=False,
    is_flag=True,
    help="Create just the project specified in the defintion file.",
)
@click.option(
    "--check/--no-check",
    default=True,
    help="Check YAML definition before creating project.",
)
def project_create(definition_file, exists_ok, wait, verbose, project_only, check):
    """Create a project following the specified configuration file.

    definition_file (str): YAML file containing project definition."""
    if definition_file == ".":
        definition_file = default_yaml

    if check:
        with console.status(f"Checking project..."):
            if not checker.check_from_file(definition_file, check_project=True):
                exit(1)

    result = ef.Session().load(
        definition_file, exists_ok=exists_ok, project_only=project_only
    )

    if verbose:
        console.print(result)

    if wait:
        with console.status(
            "Waiting for datasets to be loaded...", spinner_style="green"
        ):
            for dataset in result["datasets"]:
                while dataset.reload().loading:
                    time.sleep(0.1)

                if dataset.loading_failed:
                    exit(1)


@project.command("list", aliases=["ls"])
def project_list():
    """Lists the projects associated with the current user."""
    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name", "Problem Type"]]
    for m in ef.Session().projects:
        table.add_row(m.id, m.name, str(m.problem_type))
    console.print(table)


@project.command("delete")
@click.argument("project", required=True)
@click.option("-y", "--yes", default=False, is_flag=True, help="Confirm deletion.")
def project_delete(project, yes):
    """Delete the specified project."""
    if project == ".":
        project = default_yaml

    if project.endswith((".yaml", ".yml")):
        project = _get_project(efemarai_file=project, must_exist=False)
    else:
        project = ef.Session().project(project)

    if project is None:
        return

    if yes or Confirm.ask(
        f"Do you want to delete project [bold]{project.name}[/bold] including all stress tests, models, datasets and domains?",
        default=False,
    ):
        project.delete(delete_dependants=True)


@main.group(cls=ClickAliasedGroup)
def model():
    """Manage models."""
    pass


@model.command("list", aliases=["ls"])
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
def model_list(file):
    """Lists the models in the current project."""
    project = _get_project(efemarai_file=file)

    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name"]]
    for m in project.models:
        table.add_row(m.id, m.name)
    console.print(table)


@model.command("create")
@click.argument("definition-file", required=True)
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
@click.option("-v", "--verbose", count=True, help="Print created models.")
@click.option(
    "--exists-ok/--exists-not-ok",
    default=False,
    help="Skip model if it already exists.",
)
@click.option(
    "--check/--no-check",
    default=True,
    help="Check YAML definition before creating model.",
)
def model_create(definition_file, file, verbose, exists_ok, check):
    """Create a model in the current project."""

    definition = checker.load_definition(definition_file)

    if check:
        with console.status(f"Checking model..."):
            if not checker.check(definition, check_models=True):
                exit(1)

    project = _get_project(definition=definition, efemarai_file=file)

    for model_definition in definition["models"]:
        if model_definition["name"] == "${model.name}":
            continue

        try:
            model = project.create_model(**model_definition, exists_ok=exists_ok)

            if verbose:
                console.print(model)

            console.print(model.id)

        except Exception as e:
            console.print(e, style="red")
            exit(1)


@model.command("delete")
@click.argument("model", required=True)
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
@click.option(
    "-d",
    "--delete-dependants",
    is_flag=True,
    show_default=True,
    default=False,
    help="Delete all entities that depend on the model",
)
def model_delete(model, file, delete_dependants):
    """Delete a model from the current project.

    MODEL - the name or ID of the model."""
    project = _get_project(efemarai_file=file)

    if _check_for_multiple_entities(project.models, model):
        console.print("There are multiple models with the given:\n")
        models = [t for t in project.models if t.name == test]
        _print_table(models)
        console.print(
            f"\nRun the command with a specific model id: [bold green]$ efemarai model delete {models[0].id}",
        )
        exit(1)

    model_name = model
    model = project.model(model)
    if not model:
        console.print(
            f":poop: Project '{project.name}' does not have model '{model_name}'",
            style="red",
        )
        exit(1)

    model.delete(delete_dependants)


@main.group(cls=ClickAliasedGroup)
def domain():
    """Manage domains."""
    pass


@domain.command("list", aliases=["ls"])
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
def domain_list(file):
    """Lists the domains in the current project."""
    project = _get_project(efemarai_file=file)

    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name"]]
    for d in project.domains:
        table.add_row(d.id, d.name)
    console.print(table)


@domain.command("create")
@click.argument("definition-file", required=True)
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
@click.option("-v", "--verbose", count=True, help="Print created domains.")
@click.option(
    "--exists-ok/--exists-not-ok",
    default=False,
    help="Skip domain if it already exists.",
)
@click.option(
    "--check/--no-check",
    default=True,
    help="Check YAML definition before creating domain.",
)
def domain_create(definition_file, file, verbose, exists_ok, check):
    """Create a domain in the current project.

    definition_file (str): YAML file containing domain definition."""

    definition = checker.load_definition(definition_file)

    if check:
        with console.status(f"Checking domain..."):
            if not checker.check(definition, check_domains=True):
                exit(1)

    project = _get_project(definition=definition, efemarai_file=file)

    for domain_definition in definition["domains"]:
        try:
            domain = project.create_domain(**domain_definition, exists_ok=exists_ok)

            if verbose:
                console.print(domain)

            console.print(domain.id)

        except Exception as e:
            console.print(e, style="red")
            exit(1)


@domain.command("delete")
@click.argument("domain", required=True)
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
@click.option(
    "-d",
    "--delete-dependants",
    is_flag=True,
    show_default=True,
    default=False,
    help="Delete all entities that depend on the domain",
)
def domain_delete(domain, file, delete_dependants):
    """Delete a domain from the current project.

    DOMAIN - the name or ID of the domain."""
    project = _get_project(efemarai_file=file)

    if _check_for_multiple_entities(project.domains, domain):
        console.print("There are multiple domains with the given name:\n")
        domains = [t for t in project.domains if t.name == test]
        _print_table(domains)
        console.print(
            f"\nRun the command with a specific domain id: [bold green]$ efemarai domain delete {domains[0].id}",
        )
        exit(1)

    domain_name = domain
    domain = project.domain(domain)
    if not domain:
        console.print(f":poop: Domain '{domain_name}' does not exist.", style="red")
        exit(1)
    domain.delete(delete_dependants)


@domain.command("download")
@click.argument("domain", required=True)
@click.option("-o", "--output", default=None, help="Optional domain output file.")
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
def domain_download(domain, output, file):
    """Download a domain.

    DOMAIN - the name of the domain."""
    project = _get_project(efemarai_file=file)

    domain = project.domain(domain)
    filename = domain.download(filename=output)
    console.print(
        (f":heavy_check_mark: Downloaded '{domain.name}' reports to: \n  {filename}"),
        style="green",
    )


@main.group(cls=ClickAliasedGroup)
def dataset():
    """Manage datasets."""
    pass


@dataset.command("list", aliases=["ls"])
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
def dataset_list(file):
    """Lists the datasets in the current project."""
    project = _get_project(efemarai_file=file)

    table = Table(box=None)

    for x in ["Id", "Name", "Status"]:
        table.add_column(x)

    for dataset in project.datasets:
        if dataset.loading_finished:
            status = "Loaded"
        elif dataset.loading_failed:
            status = "Failed"
        else:
            status = "Loading"

        table.add_row(dataset.id, dataset.name, status)

    console.print(table)


@dataset.command("create")
@click.argument("definition_file", required=True)
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
@click.option(
    "-w",
    "--wait",
    default=False,
    is_flag=True,
    help="Wait for dataset to be loaded.",
)
@click.option("-v", "--verbose", count=True, help="Print created datasets.")
@click.option(
    "--exists-ok/--exists-not-ok",
    default=False,
    help="Skip dataset if it already exists.",
)
@click.option(
    "--check/--no-check",
    default=True,
    help="Check YAML definition before creating dataset.",
)
def dataset_create(definition_file, file, wait, verbose, exists_ok, check):
    """Create a dataset in the current project.

    definition_file (str): YAML file containing dataset definition."""

    definition = checker.load_definition(definition_file)

    if check:
        with console.status(f"Checking dataset..."):
            if not checker.check(definition, check_datasets=True):
                exit(1)

    project = _get_project(definition=definition, efemarai_file=file)

    datasets = []
    for dataset_definition in definition["datasets"]:
        try:
            dataset = project.create_dataset(**dataset_definition, exists_ok=exists_ok)
            datasets.append(dataset)

            if verbose:
                console.print(dataset)

            console.print(dataset.id)

        except Exception as e:
            console.print(e, style="red")
            exit(1)

    if not wait:
        return

    with console.status("Waiting for datasets to be loaded...", spinner_style="green"):
        for dataset in datasets:
            while dataset.reload().loading:
                time.sleep(0.1)

            if dataset.loading_failed:
                console.print(
                    f":poop: Dataset loading failed: {dataset}",
                    style="red",
                )
                exit(1)


@dataset.command("delete")
@click.argument("dataset", required=True)
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
@click.option(
    "-d",
    "--delete-dependants",
    is_flag=True,
    show_default=True,
    default=False,
    help="Delete all entities that depend on the dataset",
)
def dataset_delete(dataset, file, delete_dependants):
    """Delete a dataset from the current project.

    DATASET - the name or ID of the dataset."""
    project = _get_project(efemarai_file=file)

    if _check_for_multiple_entities(project.datasets, dataset):
        console.print("There are multiple datasets with the given name:\n")
        datasets = [t for t in project.datasets if t.name == test]
        _print_table(datasets)
        console.print(
            f"\nRun the command with a specific dataset id: [bold green]$ efemarai dataset delete {datasets[0].id}",
        )
        exit(1)

    dataset_name = dataset
    dataset = project.dataset(dataset)
    if not dataset:
        console.print(f":poop: Dataset '{dataset_name}' does not exist.", style="red")
        exit(1)

    dataset.delete(delete_dependants)


@main.group(cls=ClickAliasedGroup)
def test():
    """Manage stress tests."""
    pass


@test.command("list", aliases=["ls"])
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
def test_list(file):
    """Lists the stress tests in the current project."""
    project = _get_project(efemarai_file=file)

    _print_table(project.stress_tests)


@test.command("run")
@click.argument("definition-file", required=True)
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
@click.option(
    "-w", "--wait", default=False, is_flag=True, help="Wait for stress test to finish."
)
@click.option("-v", "--verbose", count=True, help="Print created stress tests.")
def test_run(definition_file, file, wait, verbose):
    """Run a stress test.

    definition_file (str): YAML file containing stress test definition."""
    if not os.path.exists(definition_file):
        console.print(f":poop: File {definition_file} does not exist")
        exit(1)

    definition = ef.Session._load_config_file(definition_file)

    project = _get_project(definition=definition, efemarai_file=file)

    try:
        test_definitions = definition["tests"]
    except KeyError:
        console.print(
            f":poop: Key 'tests' not found in definition file: {definition_file}",
            style="red",
        )
        exit(1)

    cfg = ef.Session._read_config()

    tests = []
    for test_definition in test_definitions:
        test = project.create_stress_test(**test_definition)
        tests.append(test)

        if verbose:
            console.print(test)

        console.print(f"{cfg['url']}project/{project.id}/runs/{test.id}")

    if not wait:
        return

    with console.status("Waiting for stress tests to finish...", spinner_style="green"):
        for test in tests:
            while test.reload().running:
                time.sleep(0.1)

            if test.failed:
                console.print(
                    f":poop: Stress test failed: \n {test} {test.state_message}",
                    style="red",
                )
                exit(1)


@test.command("delete")
@click.argument("test", required=True)
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
def test_delete(test, file):
    """Delete a stress test from the current project.

    TEST - Name, ID or yaml file of the stress test."""
    project = _get_project(efemarai_file=file)

    if _check_for_multiple_entities(project.stress_tests, test):
        console.print("There are multiple stress tests with the given name:\n")
        tests = [t for t in project.stress_tests if t.name == test]
        _print_table(tests)
        console.print(
            f"\nRun the command with a specific stress test id: [bold green]$ efemarai test delete {tests[0].id}",
        )
        exit(1)

    test_name = test

    if test.endswith((".yaml", ".yml")):
        test_name = _get_test_name(test)

    test = project.stress_test(test_name)

    if test is None:
        console.print(f":poop: Stress test '{test_name}' does not exist.", style="red")
        exit(1)

    test.delete()


@test.command("download")
@click.argument("test", required=True)
@click.option("--min_score", default=0.0, help="Minimum score for the samples.")
@click.option("--include_dataset", default=False, help="Include original test dataset.")
@click.option("--path", default=None, help="Path to the downloaded files.")
@click.option("--unzip", default=True, help="Whether to unzip the resulting file.")
@click.option("--ignore_cache", default=False, help="Ignore local cache.")
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
def test_download(test, min_score, include_dataset, path, unzip, ignore_cache, file):
    """Download the stress test vulnerabilities dataset.

    TEST - Name, ID or yaml file of the stress test to download."""
    test_name = test
    project = _get_project(efemarai_file=file)

    if test.endswith((".yaml", ".yml")):
        test_name = _get_test_name(test)

    test = project.stress_test(test_name)

    if test is None:
        console.print(f":poop: Stress test '{test_name}' does not exist.", style="red")
        exit(1)

    test.vulnerabilities_dataset(
        min_score=min_score,
        include_dataset=include_dataset,
        path=path,
        unzip=unzip,
        ignore_cache=ignore_cache,
    )


@test.command("reports")
@click.argument("test", required=True)
@click.option("-o", "--output", default=None, help="Optional output file.")
@click.option(
    "-f", "--file", help=f"Name of the Efemarai file (Default is '{default_yaml}')"
)
def test_reports(test, output, file):
    """Export the stress test reports.

    TEST - Name, ID or yaml file of the stress test."""
    test_name = test
    project = _get_project(efemarai_file=file)

    if test.endswith((".yaml", ".yml")):
        test_name = _get_test_name(test)

    test = project.stress_test(test_name)

    if test is None:
        console.print(f":poop: Stress test '{test_name}' does not exist.", style="red")
        exit(1)

    filename = test.download_reports(filename=output)
    console.print(
        (f":heavy_check_mark: Downloaded '{test.name}' reports to: \n  {filename}"),
        style="green",
    )


def _print_table(tests):
    table = Table(box=None)
    [table.add_column(x) for x in ["Id", "Name", "Model", "Dataset", "Domain", "State"]]
    for t in tests:
        table.add_row(
            t.id, t.name, t.model.name, t.dataset.name, t.domain.name, str(t.state)
        )
    console.print(table)


def _check_for_multiple_entities(entities, name):
    return len([x for x in entities if x.name == name])


def _get_project(definition=None, efemarai_file=None, must_exist=True):
    # Check if definition needs to be overwritten from file
    if definition is not None:
        if "project" not in definition or "name" not in definition["project"]:
            definition = None

    if definition is None or efemarai_file is not None:

        if efemarai_file is None:
            efemarai_file = default_yaml

        if not os.path.exists(efemarai_file):
            console.print(
                f":poop: '{efemarai_file}' does not exist in '{os.getcwd()}'.",
                style="red",
            )
            exit(1)

        definition = ef.Session()._load_config_file(efemarai_file)

    if "project" not in definition:
        console.print(f":poop: Missing field 'project'", style="red")
        exit(1)

    if "name" not in definition["project"]:
        console.print(f":poop: Missing filed 'name' (in 'project')", style="red")
        exit(1)

    name = definition["project"]["name"]
    project = ef.Session().project(name)
    if project is None and must_exist:
        console.print(f":poop: Project '{name}' does not exist.", style="red")
        exit(1)

    return project


def _get_test_name(file, index=0):
    config = ef.Session()._load_config_file(file)
    return config["tests"][index]["name"]


if __name__ == "__main__":
    main()
