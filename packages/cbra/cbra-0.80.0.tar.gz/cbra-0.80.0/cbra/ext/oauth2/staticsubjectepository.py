"""Declares :class:`StaticSubjectRepository`."""
from .settingssubjectrepository import SettingsSubjectRepository
from .types import ISubject


class StaticSubjectRepository(SettingsSubjectRepository):
    """A :class:`cbra.ext.oauth2.types.ISubjectRepository` implemenation
    that is configured with a static set of subjects.
    """
    __module__: str = 'cbra.ext.oauth2'
    subjects: dict[int | str, ISubject] = {}

    def __init__(self) -> None:
        self.subjects = type(self).subjects