"""Declares :class:`SettingsSubjectRepository`."""
import types
from typing import Any

from cbra.conf import settings # type: ignore
from cbra.utils import docstring
from .types import BaseSubject
from .types import ISubject
from .types import ISubjectRepository


class SettingsSubjectRepository(ISubjectRepository):
    """A :class:`~cbra.ext.oauth2.types.ISubjectRepository` implementation
    that uses the :mod:`cbra` settings module as the source of the OAuth
    subjects.
    
    The settings module must declare the ``OAUTH_SUBJECTS`` attribute holding
    a dictionary that maps subject identifiers (i.e. its keys) to dictionaries
    specifying the additional properties of a subject.

    The subject model must be defined using the :attr:`model` attribute. The
    model defines which keys need to be declared for each subject.
    """
    __module__: str = 'cbra.ext.oauth2'
    settings: types.ModuleType = settings
    subjects: dict[int | str, Any]
    model: type[ISubject] = BaseSubject

    def __init__(self) -> None:
        self.subjects = {
            k: {**v, 'sub': k}
            for k, v in dict.items(getattr(self.settings, 'OAUTH_SUBJECTS', {})) # type: ignore
        }

    @docstring(ISubjectRepository)
    async def get(
        self,
        subject_id: int | str,
        client_id: str | None = None
    ) -> ISubject:
        return self.model.parse_obj({
            **self.subjects[subject_id],
            'client_id': client_id
        })