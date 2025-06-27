from agents.budget_agent.domain.interface import AllRepositories
from agents.budget_agent.infrastructure.db.postgres.db_context import SQLAlchemyConnection
from agents.budget_agent.infrastructure.db.postgres.budget_repo import BudgetRepo
from agents.budget_agent.application.budget_usecase import BudgetAgentUsecase

all_repositories = AllRepositories(
    repo_context=SQLAlchemyConnection,
    budget_repo=BudgetRepo()
)

BUDGET_USECASE = BudgetAgentUsecase(all_repositories)