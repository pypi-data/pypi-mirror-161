import os
import re
import sys
import tempfile
import urllib

import git
import yaml
from furl import furl

from efemarai.base_checker import BaseChecker
from efemarai.console import console
from efemarai.dataset import DatasetFormat, DatasetStage
from efemarai.problem_type import ProblemType
from efemarai.runtime_checker import RuntimeChecker


class DefinitionChecker(BaseChecker):
    @staticmethod
    def is_path_remote(path):
        return urllib.parse.urlparse(path).scheme in ("http", "https")

    def load_definition(self, filename):
        if not os.path.isfile(filename):
            self._error(f"File '{filename}' does not exist")

        with open(filename) as f:
            contents = f.read()
        contents = os.path.expandvars(contents)

        unknown_environment_variables = list(
            re.findall("\$\{([a-zA-Z]\w*)\}", contents)
        )
        if unknown_environment_variables:
            for match in unknown_environment_variables:
                self._error(f"Unknown environment variable '{match}' in '{filename}'")

        return yaml.safe_load(contents)

    def check(
        self,
        definition,
        check_all=False,
        check_project=False,
        check_datasets=False,
        check_models=False,
        check_domains=False,
    ):
        try:
            if "project" in definition or check_project or check_all:
                self.check_project(definition)

            if "datasets" in definition or check_datasets or check_all:
                self.check_datasets(definition)

            if "models" in definition or check_models or check_all:
                self.check_models(definition)

            if "domains" in definition or check_domains or check_all:
                self.check_domains(definition)
        except AssertionError:
            return False

        return True

    def check_from_file(
        self,
        definition_file,
        check_all=False,
        check_project=False,
        check_datasets=False,
        check_models=False,
        check_domains=False,
    ):
        try:
            definition = self.load_definition(definition_file)
        except AssertionError:
            return False

        return self.check(
            definition,
            check_all=check_all,
            check_project=check_project,
            check_datasets=check_datasets,
            check_models=check_models,
            check_domains=check_domains,
        )

    def check_project(self, definition):
        project = self._get_required_item(definition, "project")

        name = self._get_required_item(project, "name", "project")

        problem_type = self._get_required_item(project, "problem_type", "project")

        if not ProblemType.has(problem_type):
            self._error(f"Unsupported problem type '{problem_type}' (in 'project')")

    def check_datasets(self, definition):
        datasets = self._get_required_item(definition, "datasets")

        if not isinstance(datasets, list):
            self._error(f"'datasets' must be an array")

        known_datasets = set()

        for i, dataset in enumerate(datasets):
            parent = f"datasets[{i}]"

            name = self._get_required_item(dataset, "name", parent)

            if name in known_datasets:
                self._error(f"Multiple datasets named '{name}' exist (in 'datasets')")

            known_datasets.add(name)

            format = self._get_required_item(dataset, "format", parent)
            if not DatasetFormat.has(format):
                self._error(f"Unsupported dataset format '{format}' (in '{parent}')")

            stage = self._get_required_item(dataset, "stage", parent)
            if not DatasetStage.has(stage):
                self._error(f"Unsupported dataset stage '{stage}' (in '{parent}')")

            upload = dataset.get("upload", True)

            if upload:
                annotations_url = dataset.get("annotations_url")
                if annotations_url is not None and not os.path.exists(annotations_url):
                    self._error(
                        f"File path '{anotations_url}' does not exist (in '{parent}')"
                    )

                data_url = dataset.get("data_url")
                if data_url is not None and not os.path.exists(data_url):
                    self._error(
                        f"File path '{data_url}' does not exist (in '{parent}')"
                    )

    def check_models(self, definition):
        models = self._get_required_item(definition, "models")

        if not isinstance(models, list):
            self._error(f"'models' must be an array")

        known_models = set()

        for i, model in enumerate(models):
            parent = f"models[{i}]"
            name = self._get_required_item(model, "name", parent)

            if name in known_models:
                self._error(f"Multiple models named '{name}' exist (in 'models')")

            known_models.add(name)

        models = self._resolve_runtime(models)

        if not models:
            self._warning(
                "Runtime checks are skipped - just a default model runtime is provided"
            )

        for i, model in enumerate(models):
            parent = f"models[{i}]"
            self._check_repository(model, parent)
            self._check_files(model, parent)

            runtime_checker = RuntimeChecker(
                model,
                parent,
                datasets=definition.get("datasets"),
                project=definition.get("project"),
            )
            runtime_checker.check()

    def check_domains(self, definition):
        domains = self._get_required_item(definition, "domains")

        if not isinstance(domains, list):
            self._error(f"'domains' must be an array")

        known_domains = set()

        for i, domain in enumerate(domains):
            parent = f"domain[{i}]"
            name = self._get_required_item(domain, "name", parent)

            if name in known_domains:
                self._error(f"Multiple models named '{name}' exist (in 'domains')")

            known_domains.add(name)

            _ = self._get_required_item(domain, "transformations", parent)
            _ = self._get_required_item(domain, "graph", parent)

    def _resolve_runtime(self, models):
        if any("runtime" not in model for model in models):
            try:
                default_runtime = self._get_default_runtime(models)
            except AssertionError:
                self._error("Unable to load default runtime (in 'models')")

        resolved_models = []
        for i, model in enumerate(models):
            if model["name"] in {"${model.name}", "$model.name"}:
                continue

            if "runtime" not in model:
                model["runtime"] = default_runtime

            resolved_models.append(model)

        return resolved_models

    def _get_default_runtime(self, models):
        for i, model in enumerate(models):
            if model["name"] in {"${model.name}", "$model.name"}:
                runtime = model.get("runtime")
                if runtime is None:
                    raise AssertionError()
                return runtime

        if not os.path.exists("efemarai.yaml"):
            raise AssertionError()

        definition = self.load_definition("efemarai.yaml")

        models = definition.get("models")

        if not models:
            raise AssertionError()

        for i, model in enumerate(models):
            if model["name"] in {"${model.name}", "$model.name"}:
                runtime = model.get("runtime")
                if runtime is None:
                    raise AssertionError()
                return runtime

        raise AssertionError()

    def _check_repository(self, model, parent):
        repository = model.get("repository", {"url": "."})

        repo_parent = parent + ".repository"

        url = self._get_required_item(repository, "url", repo_parent)

        if DefinitionChecker.is_path_remote(url):
            branch = repository.get("branch")
            hash = repository.get("hash")
            access_token = repository.get("access_token")

            if branch is None and hash is None:
                self._error(f"'branch' or 'hash' must be provided (in '{repo_parent}')")

            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    clone_url = furl(url)
                    clone_url.username = access_token
                    clone_url.password = "x-oauth-basic"

                    repo = git.Repo.clone_from(
                        clone_url.tostr(),
                        temp_dir,
                        branch=branch,
                        depth=1,
                        single_branch=True,
                    )
                except Exception:
                    self._error(
                        f"Unable to clone repository at '{url}' (in '{repo_parent}')"
                    )

                if hash is not None:
                    try:
                        repo.commit(hash)
                    except git.exc.GitError as e:
                        self._error(
                            f"Commit '{hash}' does not exist (in '{repo_parent}')"
                        )
        else:
            if not os.path.isdir(url):
                self._error(
                    f"Repository path '{url}' (in '{repo_parent}') must be a folder."
                )

    def _check_files(self, model, parent):
        files = model.get("files", [])
        known_files = set()
        for i, file in enumerate(files):
            file_parent = parent + f".files[{i}]"
            name = self._get_required_item(file, "name", file_parent)

            if name in known_files:
                self._error(f"Multiple files named '{name}' exist (in '{parent}')")

            known_files.add(name)

            url = self._get_required_item(file, "url", parent + f".files[{i}]")

            if file.get("upload", False) and not os.path.exists(url):
                self._error(f"File path '{url}' does not exist (in '{file_parent}')")
