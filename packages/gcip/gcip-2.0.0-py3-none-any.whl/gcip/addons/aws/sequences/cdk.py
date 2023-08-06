from typing import Dict, List, Optional
from dataclasses import dataclass

from gcip.core.sequence import Sequence
from gcip.addons.aws.jobs.cdk import Diff, Deploy


@dataclass(kw_only=True)
class DiffDeployOpts:
    stacks: List[str]
    context: Optional[Dict[str, str]] = None


class DiffDeploy(Sequence):
    def __init__(
        self,
        *,
        stacks: List[str],
        context: Optional[Dict[str, str]] = None,
    ) -> None:

        super().__init__()

        #
        # cdk diff
        #
        self.diff_job = Diff(stacks=stacks, context=context)

        #
        # cdk deploy
        #
        self.deploy_job = Deploy(stacks=stacks, context=context)
        self.deploy_job.add_needs(self.diff_job)

        self.add_children(
            self.diff_job,
            self.deploy_job,
        )
