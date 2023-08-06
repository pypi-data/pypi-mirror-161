import ast
from abc import ABC, abstractmethod
from asyncio import subprocess
import pathlib
from dataclasses import dataclass, field
from typing import Any, Union, Dict, List, Tuple
from enum import Enum
from subprocess import run, PIPE, check_output, Popen
from contextlib import contextmanager

import yaml


__all__ = ["WorkflowType", "Workflow"]


class WorkflowType(Enum):
    """Different types workflows supported."""

    ExecutionMetaflow = "green"
    # DeploymentGenerator = 'magenta'
    DeploymentYaml = "bright_magenta"


MANDATORY_KEYS = {
    None: ("type",),
    WorkflowType.ExecutionMetaflow: ("py", "className"),
    WorkflowType.DeploymentYaml: ("yaml",),
}


@dataclass
class Workflow:
    """The Workflow object representing a workflow.
    Usually instances of this class are not created manually but are created from a
    class:`ai_core_sdk.content.content_package.ContentPackage` instance.
    :param name: Name of the workflow
    :type name: str
    :param path: Path to the workflow file. Type of the file depends on the worklfow type.
    :type path: pathlib.Path
    :param type: Type of the workflow
    :type type: class:`ai_core_sdk.content.workflow.WorkflowType`
    :param content_package_version: Version of the content package
    :type content_package_version: Union[str, None], optional
    :param class_name: Name of the content package's class_name
    :type class_name: Union[str, None], optional
    :param description: Description text
    :type description: str, optional
    :param additional_options: Version str
    :type additional_options: Dict[str, Any], optional
    """

    name: str
    path: pathlib.Path
    type: WorkflowType
    content_package_version: Union[str, None] = None
    class_name: Union[str, None] = None
    dockerfiles: Dict[str, pathlib.Path] = None
    description: str = field(default_factory=str)
    additional_options: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_entry(
        cls,
        name: str,
        entry: Dict[str, Any],
        content_package_version: Union[None, str] = None,
    ) -> "Workflow":
        """Create a worfklow from dictionary.
        Usually instances of this class are not created manually but are created from a
        class:`ai_core_sdk.content.content_package.ContentPackage` instance.
        :param name: Name of the workflow
        :type name: str
        :param entry: Path to the workflow file. Type of the file depends on the worklfow type.
        :type entry: Dict[str, Any]
        :param content_package_version: Version of the content package
        :type content_package_version: Union[str, None], optional
        :raises: class:`KeyError`
        :return: Workflow
        :rtype: class:`ai_core_sdk.content.workflow.Workflow`
        """
        if any([k not in entry.keys() for k in MANDATORY_KEYS[None]]):
            raise KeyError(
                "All workflow definitions require the key(s): "
                + ", ".join(MANDATORY_KEYS[None])
            )
        try:
            template_type = WorkflowType[entry["type"]]
        except KeyError:
            raise KeyError(f"Unkown workflow type '{entry['type']}'")
        if any([k not in entry.keys() for k in MANDATORY_KEYS[template_type]]):
            raise KeyError(
                f"Worfklow definitions of '{template_type.name}' require the key(s): "
                + ", ".join(MANDATORY_KEYS[template_type])
            )
        if template_type == WorkflowType.DeploymentYaml:
            path = entry["yaml"]
            class_name = None
        if template_type == WorkflowType.ExecutionMetaflow:
            path = entry["py"]
            class_name = entry["className"]
        dockerfiles = entry.get("dockerfile", None)
        if isinstance(dockerfiles, str) or isinstance(dockerfiles, pathlib.Path):
            dockerfiles = {"default": pathlib.Path(dockerfiles)}
        if isinstance(dockerfiles, dict):
            dockerfiles = {n: pathlib.Path(p) for n, p in dockerfiles.items()}
        else:
            dockerfiles = {}
        return cls(
            name=name,
            path=path,
            content_package_version=content_package_version,
            type=template_type,
            class_name=class_name,
            dockerfiles=dockerfiles,
            description=entry.get("description", ""),
            additional_options=entry.get("additionalOptions", {}),
        )

    def validate(self) -> None:
        """Run validationfor the content package definition and its workflows.
        :raises: class:`ValueError`
        """
        msg = f"Validation of worflow '{self.name}' failed: "
        failed = False
        if not pathlib.Path(self.path).exists():
            failed = True
            msg += f"\n- Workflow path {self.path} does not exist"
        else:
            if self.type is WorkflowType.ExecutionMetaflow:
                try:
                    self._get_py_class_from_template_file()
                except ValueError:
                    failed = True
                    msg += f"\n- Class '{self.class_name}' not defined in {self.path}"
        for tag, dockerfile in self.dockerfiles.items():
            if not dockerfile.exists():
                failed = True
                msg += f"\n- Dockerfile ({tag}) path {dockerfile} does not exist"
        if failed:
            raise ValueError(msg)

    def raw_metaflow_cli(
        self, *args: str, return_cmd: bool = False
    ) -> Union[str, None]:
        """Execute metaflow CLI command.
        This functions is to execute metaflow CLI commands on a workflow
        python file. The basic structure of the CLI commands is:
        `cd <base folder of the workflow> && python -m<flow.py> *args`.
        :param `*args`: CLI arguments as strings
        :type `*args`: str
        :param return_cmd: Return the command instead of executing it
        :type return_cmd: bool, optional
        :raises: class:`CalledProcessError`
        :return: Command as list of str or None
        :rtype: Union[List[str], None]
        """
        if self.type is not WorkflowType.ExecutionMetaflow:
            raise TypeError("Workflow is ")
        workflow_file = pathlib.Path(self.path)
        cwd = workflow_file.parent
        flow = workflow_file.stem
        cmd = ["python", f"-m{flow}"] + [*args]
        if return_cmd:
            return cmd
        else:
            check_output(cmd, cwd=cwd)

    def raw_build_docker(
        self,
        *args: str,
        docker_type:
        Union[None, str] = None,
        return_cmd: bool = False,
        silent: bool=False
    ) -> Union[List[str], None]:
        """Execute docker build CLI command.
        This functions is to execute docker build CLI commands on dockerfile
        of workflow. The basic structure of the CLI commands is:
        `docker build -f <workflow.dockerfile[dockertype]> --build-arg pkg_version===<content_pkg_version> <base folder of the workflow>`.
        :param `*args`: CLI arguments as strings
        :type `*args`: str
        :param dockertype: Specific docker type, if not set the first in the dockerfiles definition is being used.
        :type dockertype: str, optional
        :param return_cmd: Return the command instead of executing it
        :type return_cmd: str, optional
        :raises: class:`CalledProcessError`
        :return: Command as list of str or None
        :rtype: Union[List[str], None]
        """
        if len(self.dockerfiles) == 0:
            raise KeyError(f"No Dockerfile available!")
        if docker_type is None:
            docker_type = [*self.dockerfiles.keys()][0]
        try:
            dockerfile = pathlib.Path(self.dockerfiles[docker_type])
        except KeyError:
            raise KeyError(f"Unknown docker_type '{docker_type}'")
        pkg_version = self.content_package_version
        if pkg_version is not None:
            pkg_version = ["--build-arg", f"pkg_version==={pkg_version}"]
        else:
            pkg_version = ["--build-arg", f"pkg_version="]
        cmd = [
            "docker",
            "build",
            *args,
            *pkg_version,
            f"-f{dockerfile}",
            f"{dockerfile.parent}",
        ]
        if return_cmd:
            return cmd
        else:
            if silent:
                stderr = PIPE
            else:
                stderr = None
            check_output(cmd, stderr=stderr)

    def create_image(
        self,
        workflow_config: Union[str, pathlib.Path, Dict],
        docker_type: Union[None, str] = None,
        return_cmd: bool = False,
        silent: bool = False
    ):
        """Create docker image based on workflow_config.
        The image is created using the tag workflow_config['image'].
        :param workflow_config: Path to the workflow config or dictionary from a loaded workflow config
        :type workflow_config: Union[str, pathlib.Path, Dict]
        :param dockertype: Specific docker type, if not set the first in the dockerfiles definition is being used.
        :type dockertype: str, optional
        :param return_cmd: Return the command instead of executing it
        :type return_cmd: str, optional
        :raises: class:`CalledProcessError`, class:`AttributeError`
        :return: Command as list of str or None
        :rtype: Union[List[str], None]
        """
        if isinstance(workflow_config, str) or isinstance(
            workflow_config, pathlib.Path
        ):
            with pathlib.Path(workflow_config).open() as stream:
                workflow_config = yaml.safe_load(stream)
        if not isinstance(workflow_config, dict):
            raise AttributeError("workflow_config is mandatory!")
        return self.raw_build_docker(
            f'--tag={workflow_config["image"]}',
            docker_type=docker_type,
            return_cmd=return_cmd,
            silent=silent
        )

    def _get_py_class_from_template_file(self):
        if self.class_name is None:
            raise ValueError("Attribute class_name is None.")
        with self.absolute_path.open() as fd:
            file_contents = fd.read()
        module = ast.parse(file_contents)
        class_definitions = [
            node for node in module.body if isinstance(node, ast.ClassDef)
        ]
        return class_definitions[
            [c.name for c in class_definitions].index(self.class_name)
        ]

    def _create_template_deployment_yaml(self, target_file, return_cmd):
        workflow_file = pathlib.Path(self.path)
        target_file = pathlib.Path(target_file).resolve() if target_file else None
        if return_cmd:
            if target_file:
                return ["cp", str(workflow_file), str(target_file)]
            else:
                return ["cat", str(workflow_file)]
        else:
            with workflow_file.open() as stream:
                if target_file:
                    with open(target_file, "w") as f:
                        f.write(stream.read())
                else:
                    return stream.read()

    def _create_template_execution_metaflow(
        self, workflow_config, target_file, return_cmd, silent
    ):
        workflow_file = pathlib.Path(self.path)
        target_file = pathlib.Path(target_file).resolve() if target_file else None
        if isinstance(workflow_config, str) or isinstance(
            workflow_config, pathlib.Path
        ):
            with pathlib.Path(workflow_config).open() as stream:
                workflow_config = yaml.safe_load(stream)
        if not isinstance(workflow_config, dict):
            raise AttributeError(
                "For templates of type ExecutionMetaflow a workflow_config is mandatory!"
            )
        workflow_config = {**{".workflow-yaml-template-kwargs": self.additional_options}, **workflow_config}
        metaflow_args, argo_args, argo_create_args = generate_metaflow_args_from_workflow_config(workflow_config)
        cwd = workflow_file.parent
        flow = workflow_file.stem
        cmd = ["python", "-Wignore", f"-m{flow}"]
        cmd += [*metaflow_args]
        cmd += ["argo"] + argo_args + ["create"]
        cmd += [*argo_create_args]
        cmd += ["--only-json"]
        if return_cmd:
            return cmd
        else:
            if silent:
                stderr = PIPE
            else:
                stderr = None
            output = check_output(cmd, stderr=stderr, cwd=cwd)
            if target_file:
                with pathlib.Path(target_file).open("w") as stream:
                    stream.write(output.decode("utf-8"))
            else:
                return output.decode("utf-8")


    def create_template(
        self,
        workflow_config: Union[str, pathlib.Path, Dict, None] = None,
        target_file: Union[str, pathlib.Path, None] = None,
        return_cmd: bool = False,
        silent: bool = False
    ) -> Union[List[str], None]:
        """Create docker image based on workflow_config.
        The image is created using the tag workflow_config['image'].
        :param workflow_config: Path to the workflow config or dictionary from a loaded workflow
        config. Can also be None for DeploymentYaml workflows.
        :type workflow_config: Union[str, pathlib.Path, Dict, NOne]
        :param target_file: Output path for the template. If None the template will be printed.
        :type target_file: Union[str, pathlib.Path, None], optional
        :param return_cmd: Return the command instead of executing it
        :type return_cmd: str, optional
        :raises: class:`CalledProcessError`, class:`AttributeError`
        :return: Command as list of str or None
        :rtype: Union[List[str], None]
        """
        if self.type == WorkflowType.DeploymentYaml:
            return self._create_template_deployment_yaml(target_file, return_cmd)
        elif self.type == WorkflowType.ExecutionMetaflow:
            return self._create_template_execution_metaflow(
                workflow_config, target_file, return_cmd, silent
            )
        else:
            raise ValueError(
                f"{self.type} can not be used to create an AICore template."
            )

    @property
    def absolute_path(self) -> pathlib.Path:
        """Return absolute path of the workflow file (py/yaml).
        :return: Path
        :rtype: class:`pathlib.Path`
        """
        if not self.path.is_absolute():
            raise ValueError("Path of the workflow is not absolute path!")
        return self.path

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Workflow(name='{self.name}', type={self.type.name})"


class WorkflowConfigOps(ABC):
    """Abstract class to define expected entries in a workflow config
    and the CLI args they result in.
    """

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    def __call__(self, key: str, value: Any) -> None:
        """Register an entry.
        :param key: Key of the entry.
        :type key: str
        :param value: Value
        :type value: Any
        """
        ...

    @abstractmethod
    def collect(self) -> Tuple[Union[str, List], Union[str, List], Union[str, List]]:
        """Return CLI arguments from the collected entries.
        Calling this function should also set the class to its initial state.
        """
        ...


class CopyPasteOps(WorkflowConfigOps):
    """Workflow config entry to be used directly as CLI argument.
    :param n_args: Number of different cli argument types
    :type n_args: int
    :param pos: Position of the CLI arguments in the return of CopyPasteOps.collect()
    :param pos: int
    """

    def __init__(self, n_args: int, pos: int):
        self.n_args = n_args
        self.pos = pos
        self.values = []

    def __call__(self, _: str, value: Union[List[str], str]) -> None:
        """Register an entry.
        :param _: Key of the workflow config entry (not processed)
        :type _: str
        :param v: Entry as a single str or a list of str
        :type v: Union[List[str], str]
        """
        self.values.extend([value] if isinstance(value, str) else value)

    def collect(self) -> Tuple[List[str]]:
        """Returns n_args Lists of cli arguments.
        :return: Tuple of cli arguments lists.
        :rtype: Tuple[List[str]]
        """
        args = [list() for _ in range(self.n_args)]
        if len(self.values) > 0:
            args[self.pos].extend(self.values)
        self.values = []
        return args


class NamedOps(WorkflowConfigOps):
    """Workflow config entry to be a named options --<name>=<entry>.
    :param n_args: Number of different cli argument types
    :type n_args: int
    :param pos: Position of the CLI arguments in the return of CopyPasteOps.collect()
    :param pos: int
    """

    def __init__(self, key, n_args, pos):
        self.key = key
        self.n_args = n_args
        self.pos = pos
        self.values = []

    def __call__(self, _: str, value: str) -> None:
        """Register an entry.
        :param _: Key of the workflow config entry (not processed)
        :type _: str
        :param value: Entry as a single str or a list of str
        :type value: Union[List[str], str]
        """
        self.values.append(value)

    def collect(self):
        args = [list() for _ in range(self.n_args)]
        if len(self.values) > 0:
            args[self.pos].extend([f"--{self.key}={v}" for v in self.values])
        self.values = []
        return args


class DictOps(WorkflowConfigOps):
    def __init__(self, key, n_args, pos):
        self.key = key
        self.n_args = n_args
        self.pos = pos
        self.entry = {}

    def __call__(self, _, entry):
        self.entry = {**self.entry, **entry}

    def collect(self):
        args = [list() for _ in range(self.n_args)]
        args[self.pos].extend(
            [f'--{self.key}="{k}:{v}"' for k, v in self.entry.items()]
        )
        self.entry = {}
        return args


class KubernetesOps(WorkflowConfigOps):
    def __init__(self):
        self.image = None
        self.secret = None

    def __call__(self, k, v):
        if k in "objectStoreSecret":
            self.secret = v.strip()
        elif k == "image":
            self.image = v.strip()
        else:
            raise ValueError

    def collect(self):
        if self.image is None and self.secret is None:
            return [], [], []
        arg = "--with=kubernetes:"
        opts = ([f"image={self.image}"] if self.image else []) + (
            [f"secrets={self.secret}"] if self.secret else []
        )
        arg += ",".join(opts)
        self.image = self.secret = None
        return arg, [], []


class Template(WorkflowConfigOps):
    def __init__(self, template, n_args):
        self.template = template
        self.n_args = n_args

    def __call__(self, _, v):
        for key, args in v.items():
            if key in self.template.keys():
                self.template[key](key, args)
        return self

    def collect(self):
        args = [list() for _ in range(self.n_args)]
        for key, entry in self.template.items():
            new_args = entry.collect()
            assert len(new_args) == len(args)
            for i in range(len(args)):
                args[i].extend(
                    [new_args[i]] if isinstance(new_args[i], str) else new_args[i]
                )
        return args


def generate_metaflow_args_from_workflow_config(workflow_config: Dict):
    kubernetes_ops = KubernetesOps()

    metaflow_plain_args = CopyPasteOps(3, 0)
    workflow_plain_args = CopyPasteOps(3, 2)
    label_ops = DictOps("label", 3, 2)
    annotation_ops = DictOps("annotation", 3, 2)
    additional_ops = Template(
        {
            "step": metaflow_plain_args,
            "metaflow": metaflow_plain_args,
            "labels": label_ops,
            "annotations": annotation_ops,
            "pipeline": workflow_plain_args,
            "workflow": workflow_plain_args,
        },
        n_args=3,
    )

    special_keywords = {
        ".workflow-yaml-template-kwargs": additional_ops,
        "objectStoreSecret": kubernetes_ops,
        "image": kubernetes_ops,
        "additionalOptions": additional_ops,
        "name": NamedOps("name", 3, 1),
        "labels": label_ops,
        "annotations": annotation_ops,
        "imagePullSecret": NamedOps("image-pull-secret", 3, 2),
    }
    return Template(special_keywords, n_args=3)(None, workflow_config).collect()
