"""Abstraction layer to construct a workflow as an airflow DAG."""
import json
import logging
from os import environ
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

from airflow import DAG

from dkist_processing_core._node import Node
from dkist_processing_core._node import task_type_hint
from dkist_processing_core._node import upstreams_type_hint

__all__ = ["Workflow"]


class Workflow:
    """
    Abstraction to create a workflow in the implemented engine api (airflow).

    - Defines the api for task and workflow definition
    - abstracts workflow engine syntax from definition
    - implements workflow and tasks in engine specific syntax
    - engine = airflow
    - contains nodes and the relationships between them

    >>> category = "instrument"
    >>> name = "calibration_name"
    >>> version = "V6-12342"
    >>> task = Task()
    >>> workflow_instance = Workflow(
    >>>    process_category=category, process_name=name, workflow_package=__package__, workflow_version=version,
    >>>)
    >>> workflow_instance.add_node(task=task, upstreams=None)
    """

    def __init__(
        self,
        process_category: str,
        process_name: str,
        workflow_package: str,
        tags: Optional[List[str]] = None,
        workflow_version: Optional[str] = None,
    ):
        """
        Create a workflow instance.

        Parameters
        ----------
        process_category: Category for the process the workflow executes e.g. instrument name
        process_name: Name for the process the workflow executes e.g. algorithm name
        workflow_package: The string representing the dot notation location of the
          workflow definition. e.g. __package__
        tags: tags to be used in airflow's UI when searching for dags
        workflow_version: Version of the workflow being deployed.  Typically populated by the CI/CD
          build process.

        """
        self.workflow_package = workflow_package
        self.process_category = process_category
        self.process_name = process_name
        self.workflow_name = f"{self.process_category}_{self.process_name}"
        self.workflow_version = workflow_version or environ.get("BUILD_VERSION", "dev")
        self.tags = tags or []
        self._dag_name = f"{self.workflow_name}_{self.workflow_version}"
        self._dag = self._initialize_local_dag()
        self.nodes = []

    @property
    def _dag_tags(self) -> str:
        """
        Return the list of dag tags to be used in Airflow's UI.

        Equal to the list of supplied tags plus the workflow version.
        """
        if isinstance(self.tags, str):
            self.tags = [self.tags]
        tags = self.tags + [self.workflow_version]
        # Make sure there are no duplicate tags
        tags = list(set(tags))
        return json.dumps(tags)

    @property
    def _dag_definition(self) -> str:
        return f"DAG(dag_id='{self._dag_name}', start_date=days_ago(2), schedule_interval=None, catchup=False, tags={self._dag_tags})"

    def _initialize_local_dag(self) -> DAG:
        from airflow.utils.dates import days_ago

        return eval(self._dag_definition)

    def add_node(
        self,
        task: task_type_hint,
        upstreams: upstreams_type_hint = None,
    ) -> None:
        """Add a node and edges from that node to the workflow."""
        node = Node(
            workflow_name=self.workflow_name,
            workflow_version=self.workflow_version,
            workflow_package=self.workflow_package,
            task=task,
            upstreams=upstreams,
        )
        self.nodes.append(node)
        # confirm that the node can be properly added to a dag
        self._dag.add_task(node.operator)
        for upstream, downstream in node.dependencies:
            self._dag.set_dependency(upstream, downstream)

    def load(self) -> DAG:
        """Retrieve the native engine (airflow) workflow object."""
        return self._dag

    def export(self, export_path: Optional[Union[str, Path]] = None) -> Path:
        """Write a file representation of the workflow which can be run independently of the task dependencies."""
        export_path = export_path or "export/"
        export_path = Path(export_path)
        export_path.mkdir(exist_ok=True)
        workflow_py = export_path / f"{self._dag_name}.py"

        with workflow_py.open(mode="w") as f:
            f.write(
                f"#  {self.workflow_name} workflow version {self.workflow_version} definition rendered for airflow scheduler\n"
            )
            f.write(self._workflow_imports)
            f.write("# Workflow\n")
            f.write(self._workflow_instantiation)
            f.write("    # Nodes\n")
            for n in self.nodes:
                operator = f"{n.task.__name__.lower()}_operator"
                f.write(f"    {operator} = {n.operator_definition}")
                f.write("\n")
            f.write("    # Edges\n")
            f.write(self._workflow_edges)
            f.write("\n")
        return workflow_py

    @property
    def _workflow_imports(self) -> str:
        imports = [
            "from datetime import timedelta",
            "from functools import partial",
            "",
            "from airflow import DAG",
            "from airflow.operators.bash import BashOperator",
            "from airflow.utils.dates import days_ago",
            "",
            "from dkist_processing_core._failure_callback import chat_ops_notification",
            "",
            "",
        ]
        return "\n".join(imports)

    @property
    def _workflow_instantiation(self) -> str:
        return f"with {self._dag_definition} as d:\n    pass\n"

    @property
    def _workflow_edges(self) -> str:
        edges = []
        for n in self.nodes:
            for upstream, downstream in n.dependencies:
                edges.append(f"    d.set_dependency('{upstream}', '{downstream}')")
        return "\n".join(edges)

    def __repr__(self):
        """Detailed representation of the workflow."""
        return (
            f"Workflow("
            f"process_category={self.process_category}, "
            f"process_name={self.process_name}, "
            f"workflow_package={self.workflow_package}, "
            f"workflow_version={self.workflow_version}, "
            f")"
        )

    def __str__(self):
        """Representation of the workflow as a string."""
        return repr(self)
