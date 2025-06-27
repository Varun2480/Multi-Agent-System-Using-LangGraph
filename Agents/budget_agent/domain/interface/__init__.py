from agents.budget_agent.domain.interface.interface_context_repo import IRepoContext
from agents.budget_agent.domain.interface.interface_budget_repo import IBudgetRepo


class AllRepositories:
    def __init__(self, 
                 repo_context: type[IRepoContext],
                 budget_repo: IBudgetRepo
                 ) -> None:
        self.repo_context = repo_context
        self.budget_repo = budget_repo
