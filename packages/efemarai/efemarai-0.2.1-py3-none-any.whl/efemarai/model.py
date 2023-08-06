import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZipFile

import git
import pathspec

from efemarai.console import console
from efemarai.definition_checker import DefinitionChecker


class ModelRepository:
    def __init__(self, url=None, branch=None, hash=None, access_token=None):
        self.url = url if url is not None else "."
        self.branch = branch
        self.hash = hash
        self.access_token = access_token

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n      url={self.url}"
        res += f"\n      branch={self.branch}"
        res += "\n    )"
        return res

    @property
    def is_remote(self):
        return DefinitionChecker.is_path_remote(self.url)

    @contextmanager
    def archive(self, name):
        ignore_files = [
            ignore_file
            for ignore_file in [".gitignore", ".efemaraiignore"]
            if Path.joinpath(Path(self.url), ignore_file).exists()
        ]

        # Do not upload .git folder
        ignore_lines = [".git"]

        # Filter out files based on *ignore specification
        for ignore_file in ignore_files:
            ignore_lines.extend(Path(ignore_file).read_text().splitlines())

        ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_lines)

        files = [
            file
            for file in list(Path(self.url).glob("**/*"))
            if not ignore_spec.match_file(str(file))
        ]

        with tempfile.TemporaryDirectory() as dirpath:
            zip_name = os.path.join(dirpath, name)

            with ZipFile(zip_name, "w") as zip:
                for file in files:
                    zip.write(file)

            yield zip_name


class ModelFile:
    def __init__(self, name, url, upload=True, credentials=None):
        self.name = name
        self.url = url
        self.upload = upload
        self.credentials = credentials

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n      name={self.name}"
        res += f"\n      url={self.url}"
        res += f"\n      upload={self.upload}"
        res += f"\n    )"
        return res


class Model:
    """
    Provides model related functionality.

    It should be created through the :class:`efemarai.project.Project.create_model` method.

    Example:

    .. code-block:: python
        :emphasize-lines: 2

        import efemarai as ef
        ef.Session().project("Name").create_model(...)
    """

    @staticmethod
    def create(project, name, description, version, repository, files):
        """
        Creates a model.

        You should use :func:`project.create_model` instead.
        """
        if name is None:
            raise ValueError("Missing model name")

        if repository is None:
            repository = {}

        if files is None:
            files = []

        if not isinstance(repository, ModelRepository):
            repository = ModelRepository(**repository)

        files = [ModelFile(**f) if not isinstance(f, ModelFile) else f for f in files]

        response = project._put(
            f"api/model/undefined/{project.id}",
            json={
                "name": name,
                "description": description,
                "version": version,
                "repository": {
                    "url": repository.url,
                    "branch": repository.branch,
                    "hash": repository.hash,
                    "access_token": repository.access_token,
                },
                "files": [
                    {
                        "name": f.name,
                        "url": f.url,
                        "upload": f.upload,
                        "credentials": f.credentials,
                    }
                    for f in files
                ],
            },
        )
        model_id = response["id"]

        if not repository.is_remote:
            base_name = "model_code.zip"
            endpoint = f"api/modelCode/{model_id}/upload"
            with repository.archive(name=base_name) as archive_name:
                project._upload(archive_name, endpoint)

            project._post(endpoint, json={"archive": base_name})

        for f in files:
            if f.upload:
                project._upload(f.url, f"api/model/{model_id}/upload")

        return Model(project, model_id, name, description, version, repository, files)

    def __init__(self, project, id, name, description, version, repository, files):
        self.project = project
        self.id = id
        self.name = name
        self.description = description
        self.version = version
        self.repository = repository
        self.files = files

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n  id={self.id}"
        res += f"\n  name={self.name}"
        res += f"\n  description={self.description}"
        res += f"\n  version={self.version}"
        res += f"\n  repository={self.repository}"
        res += f"\n  files={self.files}"
        res += f"\n)"
        return res

    def delete(self, delete_dependants=False):
        """
        Deletes the model.

        You cannot delete an object that is used in a stress test or a baseline
        (delete those first). Deletion cannot be undone.
        """
        self.project._delete(
            f"api/model/{self.id}/{self.project.id}/{delete_dependants}",
        )
