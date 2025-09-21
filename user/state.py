from typing import TypedDict, List, Dict, Any, Optional
import json
from copy import deepcopy


class Contact(TypedDict, total=False):
    email: str
    phone: str

class Education(TypedDict, total=False):
    institution: str
    degree: str
    year_start: Optional[int]
    year_end: Optional[int]

class Experience(TypedDict, total=False):
    company: str
    position: str
    period: str
    responsibilities: List[str]

class Project(TypedDict, total=False):
    name: str
    description: str

class Certification(TypedDict, total=False):
    name: str
    provider: str
    year: Optional[int]

class Candidate(TypedDict, total=False):
    id: str
    name: str
    target_role: str

# --- финальное состояние ---
class State(TypedDict, total=False):
    candidate: Candidate
    contact: Contact
    education: List[Education]
    experience: List[Experience]
    skills: List[str]
    projects: List[Project]
    certifications: List[Certification]


def json_to_state(raw: str | Dict[str, Any]) -> State:
    if isinstance(raw, str):
        obj = json.loads(raw)
    else:
        obj = deepcopy(raw)

    if "candidates" in obj:
        cand = obj["candidates"][0]
    elif "candidate" in obj:
        cand = obj["candidate"]
    else:
        cand = obj

    candidate = {k: v for k, v in cand.items() if k not in ("profile",)}
    profile = cand.get("profile", {})

    state: State = {
        "candidate": {
            "id": candidate.get("id", ""),
            "name": candidate.get("name", ""),
            "target_role": candidate.get("target_role", "")
        },
        "contact": profile.get("contact", {}),
        "education": profile.get("education", []),
        "experience": profile.get("experience", []),
        "skills": profile.get("skills", []),
        "projects": profile.get("projects", []),
        "certifications": profile.get("certifications", []),
    }
    return state


def state_to_json(state: State, indent: int = 2) -> str:
    cand_with_profile = {
        **state["candidate"],
        "profile": {
            "contact": state.get("contact", {}),
            "education": state.get("education", []),
            "experience": state.get("experience", []),
            "skills": state.get("skills", []),
            "projects": state.get("projects", []),
            "certifications": state.get("certifications", []),
        }
    }
    return json.dumps({"candidate": cand_with_profile}, ensure_ascii=False, indent=indent)