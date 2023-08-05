from datetime import date, datetime
from typing import List, NamedTuple, Optional, Tuple

from django.utils import timezone


class Overlap(NamedTuple):
    exists: bool
    index1: Optional[int]
    index2: Optional[int]


def get_date_overlap(dates: List[Tuple[date, date]]) -> Overlap:
    result = Overlap(exists=False, index1=None, index2=None)
    if len(dates) <= 1:
        return result

    def has_overlap(start1, end1, start2, end2):
        return (start1 <= start2 <= end1) or (start2 <= start1 <= end2)

    for index1 in range(len(dates)):
        for index2 in range(index1 + 1, len(dates)):
            first = dates[index1]
            second = dates[index2]

            if has_overlap(first[0], first[1], second[0], second[1]):
                return Overlap(exists=True, index1=index1, index2=index2)

    return result


def get_age(birth_date, at_date: Optional[date] = None):
    if at_date is None:
        at_date = timezone.now()

    if isinstance(at_date, datetime) and timezone.is_aware(at_date):
        at_date = timezone.localdate(at_date)

    if isinstance(birth_date, datetime) and timezone.is_aware(birth_date):
        birth_date = timezone.localdate(birth_date)

    return (
        at_date.year
        - birth_date.year
        - ((at_date.month, at_date.day) < (birth_date.month, birth_date.day))
    )
