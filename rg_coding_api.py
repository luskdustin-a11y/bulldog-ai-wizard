"""RG Coding Department entry point: local proposals and staging only."""
from rg_coding_department import propose_repair
from rg_repair_staging import stage_repair, verify_staged

class CodingDepartment:
    def __init__(self, project_root, staging_root, model="llama3.2"):
        self.project_root = project_root
        self.staging_root = staging_root
        self.model = model

    def propose(self, relative_path, problem):
        return propose_repair(self.project_root, relative_path, problem, model=self.model)

    def stage(self, proposal, owner_approval):
        return stage_repair(self.project_root, proposal, owner_approval, self.staging_root)

    def verify(self, relative_path):
        return verify_staged(self.project_root, relative_path, self.staging_root)
