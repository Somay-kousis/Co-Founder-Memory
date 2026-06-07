from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ==========================================
# 1. PREFERENCES & CORE PRINCIPLES
# ==========================================
class UserPreferences(BaseModel):
    tech_stack: List[str] = Field(default_factory=list, description="Preferred technologies, frameworks, and tools (e.g., LangGraph, local-only, React).")
    coding_style: List[str] = Field(default_factory=list, description="Rules or patterns the user likes to follow when writing code.")
    workflows: List[str] = Field(default_factory=list, description="How the user prefers to work (e.g., offline-first, test-driven, step-by-step).")

class CorePrinciples(BaseModel):
    ideologies: List[str] = Field(default_factory=list, description="Core beliefs, personal philosophies, or business values.")
    anti_goals: List[str] = Field(default_factory=list, description="Things the user explicitly wants to avoid or promises NEVER to do.")
    lessons_learned: List[str] = Field(default_factory=list, description="Hard-earned lessons from failed experiments or past projects that should survive for years.")


# ==========================================
# 2. PROJECTS & EVOLUTION
# ==========================================
class ProjectUpdate(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="ISO timestamp of when this update occurred.")
    summary: str = Field(..., description="What changed, was accomplished, or got blocked in this update.")

class Project(BaseModel):
    name: str = Field(..., description="The unique name of the project (e.g., 'Co-Founder-Memory').")
    status: str = Field(..., description="Current state of the project (e.g., 'active', 'backlog', 'completed', 'abandoned').")
    vision_goal: str = Field(..., description="The ultimate objective or core idea behind this project.")
    updates: List[ProjectUpdate] = Field(default_factory=list, description="A chronological timeline of updates or milestones for this specific project.")


# ==========================================
# 3. STRATEGIC PLANNING & DECISIONS
# ==========================================
class Decision(BaseModel):
    id: str = Field(..., description="A short slug or unique identifier for the decision (e.g., 'local-embeddings-v3').")
    title: str = Field(..., description="What decision was made.")
    context_why: str = Field(..., description="The hidden context: why it happened, what constraints forced it, and what alternatives were rejected.")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    project_name: Optional[str] = Field(None, description="The project this decision belongs to, if applicable.")

class PlanningItem(BaseModel):
    horizon: str = Field(..., description="The time horizon (e.g., 'upcoming_plans', 'future_planning', 'long_term_roadmap').")
    goal: str = Field(..., description="What the user intends to design, research, or execute.")
    context: Optional[str] = Field(None, description="Background details or triggers behind this plan.")


# ==========================================
# 4. THE COMPREHENSIVE PERMANENT MEMORY SCHEMA
# ==========================================
class PermanentMemoryProfile(BaseModel):
    """
    The master blueprint of your Digital Co-Founder's knowledge about YOU and YOUR JOURNEY.
    This structure is saved, fetched, and evolved continuously inside the LangGraph Store.
    """
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    principles: CorePrinciples = Field(default_factory=CorePrinciples)
    projects: List[Project] = Field(default_factory=list, description="Tracked projects and their developmental timelines.")
    decisions: List[Decision] = Field(default_factory=list, description="A historic log of strategic micro and macro decisions made over time.")
    planning: List[PlanningItem] = Field(default_factory=list, description="Current roadmaps, future intentions, and upcoming tasks.")