from pydantic import BaseModel, Field
from typing import List, Optional

class TaskItem(BaseModel):
    task_id: str = Field(description="Unique identifier for the task, e.g., 'task_01'")
    title: str = Field(description="Clear, concise name of the technical action item.")
    description: str = Field(description="Detailed description of what needs to be done.")
    status: str = Field(default="pending", description="Status of the task: 'pending', 'in_progress', 'completed', or 'blocked'.")
    dependencies: List[str] = Field(default=[], description="List of task_ids that must be finished before this task can start.")

class ProjectPlan(BaseModel):
    project_name: str = Field(description="The name of the feature or startup project being planned.")
    current_milestone: str = Field(description="The immediate high-level objective.")
    tasks: List[TaskItem] = Field(default=[], description="The sequential breakdown of tasks to achieve the milestone.")
    risks_and_blockers: Optional[List[str]] = Field(default=[], description="Potential roadblocks or technical challenges identified.")