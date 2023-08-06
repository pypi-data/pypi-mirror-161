"""Declares :class:`NullSubjectRepository`."""
from .types import ISubject
from .types import ISubjectRepository


class NullSubjectRepository(ISubjectRepository):
    __module__: str = 'cbra.ext.oauth2'

    async def get(
        self,
        subject_id: int | str,
        client_id: str | None = None
    ) -> ISubject:
        raise self.SubjectDoesNotExist