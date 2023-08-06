import math
from functools import cached_property
from typing import Sequence, Union, Type
from pydantic.dataclasses import dataclass


class Page:
    """Paginator\'s single Page.

    Arguments:
        ** object_list **: current page data.
        ** page_number **: current page number.
        ** paginator **: paginator in which page is used.
    """

    def __init__(self, object_list: Sequence, page_number: int, paginator):
        self.object_list = object_list
        self.page_number = page_number
        self.paginator = paginator

    def has_next(self) -> bool:
        """Check if paginator has next page."""
        return self.page_number < self.paginator.total_pages

    def has_previous(self) -> bool:
        """Check if paginator has previous page."""
        return self.page_number > 0

    @property
    def count(self):
        """Return a number of page objects."""
        return len(self.object_list)


@dataclass
class Paginator:
    """
    Objects paginator. Should be initialised using paginate function.

    Arguments:
        ** object_list **: list of sequential objects that will be split across pages.
        ** page_limit **: number of objects per page.
        ** start_page **: number of page from which paginator will start.
    """
    object_list: Union[list, tuple, dict, set]
    page_limit: int = 10
    start_page: int = 0

    def __post_init_post_parse__(self):
        """Executed after initial validation. Set initial page."""
        self.page: Page = self._page(
            object_list=self.get_objects(self.start_page),
            page_number=self.start_page,
            paginator=self,
        )

    def __iter__(self):
        """Iterate over paginator pages. Every iteration updates paginator page object."""
        for _ in self.page_range:
            yield self.page
            self.get_next()

    def get_objects(self, page_number: int) -> Sequence:
        """Retrieve page list of data."""
        if not isinstance(page_number, int):
            raise TypeError(f'{page_number} expected to be int.')
        n = self.page_limit * page_number
        return self.object_list[n:n + self.page_limit]

    @property
    def response(self):
        """Retrieve response result property."""
        data = {
            'data': self.page.object_list,
            'page_number': self.page.page_number,
            'has_next': self.has_next,
            'has_previous': self.has_previous,
        }
        return self._create_response(**data)

    @property
    def has_next(self) -> bool:
        """Page's "has next" method."""
        return self.page.has_next()

    @property
    def has_previous(self) -> bool:
        """Page's "has previous" method."""
        return self.page.has_previous()

    def get_next(self) -> None:
        """Get next page. Overrides paginator\'s page attribute"""
        if self.has_next:
            self.page.page_number += 1
            next_page = self._page(
                object_list=self.get_objects(self.page.page_number),
                page_number=self.page.page_number,
                paginator=self,
            )
            self.page = next_page  # noqa

    def get_previous(self) -> None:
        """Get previous page. Overrides paginator\'s page attribute."""
        if self.has_previous:
            self.page.page_number -= 1
            previous_page = self._page(
                object_list=self.get_objects(self.page.page_number),
                page_number=self.page.page_number,
                paginator=self,
            )
            self.page = previous_page  # noqa

    @staticmethod
    def _page(*args, **kwargs) -> Page:
        """Returns Page object."""
        return Page(*args, **kwargs)

    def get_page_response(self, page_number: int = 0):
        """
        Get response of requested page number.
        number=0 equals first page.
        """
        if not isinstance(page_number, int):
            raise TypeError(f'{page_number} expected to be int.')
        page = self._page(
            object_list=self.get_objects(page_number),
            page_number=page_number,
            paginator=self,
        )
        data = {
            'data': page.object_list,
            'page_number': page_number,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
        }
        return self._create_response(**data)

    @cached_property
    def total(self):
        """Return the total number of objects, across all pages."""
        return len(self.object_list)

    @property
    def total_pages(self):
        """Number of total pages. Lack of additional pages means total is 0."""
        if self.total == 0:
            return 0
        return math.ceil(self.total / self.page_limit) - 1

    @property
    def page_range(self):
        """Return a range of pages."""
        return range(0, self.total_pages + 1 - self.start_page)

    def _create_response(self, **kwargs):
        """Creates json response object."""
        return {
            'total_pages': self.total_pages,
            'data': kwargs['data'],
            'page_number': kwargs['page_number'],
            'has_next': kwargs['has_next'],
            'has_previous': kwargs['has_previous'],
        }


class PaginatorDictProxy(Paginator):

    def __init__(self, object_list: dict, page_limit: int = 10, start_page: int = 0):
        self.object_list = object_list
        super().__init__(
            object_list=self._convert_dict_to_list(),
            page_limit=page_limit,
            start_page=start_page,
        )

    def _convert_dict_to_list(self) -> list[dict]:
        """Transform dict to list of dicts."""
        if not isinstance(self.object_list, dict):
            raise TypeError(f'Expected dict object, not {type(self.object_list)}')
        new_list = list()
        for k, v in self.object_list.items():
            new_list.append({k: v})
        return new_list


class PaginatorSetProxy(Paginator):

    def __init__(self, object_list: set, page_limit: int = 10, start_page: int = 0):
        self.object_list = object_list
        super().__init__(
            object_list=self._convert_set_to_list(),
            page_limit=page_limit,
            start_page=start_page,
        )

    def _convert_set_to_list(self) -> list[set]:
        """Transform set to list of sets."""
        if not isinstance(self.object_list, set):
            raise TypeError(f'Expected set object, not {type(self.object_list)}')
        new_list = list()
        for v in self.object_list:
            new_list.append(v)
        return new_list


@dataclass
class PaginatorFactory:
    """Factory for Paginator."""

    objects_type: str

    def get_paginator(self) -> Type[Paginator]:
        """Returns paginator class/subclass."""
        if self.objects_type in ['list', 'tuple']:
            return Paginator
        elif self.objects_type == 'dict':
            return PaginatorDictProxy
        elif self.objects_type == 'set':
            return PaginatorSetProxy
        else:
            raise TypeError(f'Unsupported type {self.objects_type} for object_list param.')


def paginate(
        object_list: Union[list, tuple, dict, set],
        page_limit: int = 10,
        start_page: int = 0,
):
    """Paginator initial function. Should be used to initialize paginator object."""
    factory = PaginatorFactory(type(object_list).__name__)
    paginator: Type[Paginator] = factory.get_paginator()
    return paginator(
        object_list=object_list,
        page_limit=page_limit,
        start_page=start_page,
    )
