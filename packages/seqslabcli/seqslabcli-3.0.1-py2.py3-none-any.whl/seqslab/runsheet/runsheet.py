from pathlib import Path
from sample_sheet import SampleSheet, Sample
from typing import (
    List,
    Optional,
    Union,
)


RECOMMENDED_RUN_KEYS: List[str] = ['Run_Name', 'Workflow_URL', 'Runtimes']


class Run:
    """A single run from a run sheet.

    This class is built with the keys and values in the ``"[Data]"`` section of
    the run sheet. The required keys are:

        - ``"Run_Name"``
        - ``"Workflow_URL"``
        - ``"Runtimes"``

    A run may include multiple samples.  For samples in a Run Sheet, samples with the same Run_Name will be clustered
    as a single run.
    """

    def __init__(self, samples: List[Sample], run_name: str, workflow_url: str, runtimes: str) -> None:
        self.sample_sheet: Optional[SampleSheet] = None
        self.run_name = run_name
        self.workflow_url = workflow_url
        self.runtimes = runtimes
        self.samples = []
        for s in samples:
            if set(RECOMMENDED_RUN_KEYS).issubset([key for key in s.keys()]):
                if s.get('Run_Name') == self.run_name and s.get('Workflow_URL') == self.workflow_url and s.get(
                        'Runtimes') == self.runtimes:
                    self.samples.append(s)

    def to_json(self) -> dict:
        """Return the properties of this :class:`Run` as JSON serializable.

        """
        return {
            'run_name': self.run_name,
            'workflow_url': self.workflow_url,
            'runtimes': self.runtimes,
            'samples': [{str(x): str(y) for x, y in s.items()} for s in self.samples]
        }

    def __eq__(self, other: object) -> bool:
        """Runs are equal if the following attributes are equal:
            - ``"Run_Name"``
            For Run having a same Run_Name, Workflow_URL and runtime should also be the same
        """
        if not isinstance(other, Sample):
            raise NotImplementedError
        is_equal: bool = (
            self.run_name == other.Run_Name
            and self.workflow_url == other.workflow_url
            and self.runtimes == other.runtimes
            and set(self.samples) == set(other.samples)
        )
        return is_equal

    def __str__(self) -> str:
        """Cast this object to string."""
        return str(self.to_json)


class RunSheet(SampleSheet):
    def __init__(self, path: Optional[Union[Path, str]] = None) -> None:
        super().__init__(path=path)
        self._runs = []
        self._parse_run()

    def _parse_run(self) -> None:
        run_name_set = set()
        runs = {}
        for sample in self.samples:
            rsig = (sample.get('Run_Name'), sample.get('Workflow_URL'), sample.get('Runtimes'))
            rn = sample.get('Run_Name')
            if rsig in runs and rn in run_name_set:
                runs[rsig].append(sample)
            elif rsig not in runs and rn not in run_name_set:
                runs[rsig] = [sample]
                run_name_set.add(rn)
            else:
                raise RuntimeError(f'Inconsistent run_name set {run_name_set} and run sig {runs.keys()}')
        for k, v in runs.items():
            self._runs.append(Run(v, k[0], k[1], k[2]))

    @property
    def runs(self) -> List:
        """Return the samples present in this :class:`SampleSheet`."""
        return self._runs
