#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

from typing import List, Optional

import requirements
from packaging import version

from energinetml.settings import DEFAULT_ENCODING


class RequirementList(List):
    """[summary]"""

    @classmethod
    def from_file(cls, filepath: str) -> "RequirementList":
        """[summary]

        Args:
            filepath (str): [description]

        Returns:
            RequirementList: [description]
        """
        with open(filepath, encoding=DEFAULT_ENCODING) as f:
            return cls(requirements.parse(f.read()))

    def __contains__(self, package_name: str) -> bool:
        """[summary]

        Args:
            package_name (str): [description]

        Returns:
            bool: [description]
        """
        return self.get(package_name) is not None

    def get(self, package_name: str):
        """[summary]

        Args:
            package_name (str): [description]

        Returns:
            TODO: Requirement or RequirementList: [description]
        """
        for requirement in self:
            if requirement.name == package_name:
                return requirement

    def get_specs(self, package_name: str) -> List[Optional[str]]:
        """[summary]

        Args:
            package_name (str): [description]

        Returns:
            List[Optional[str]]: [description]
        """
        requirement = self.get(package_name)
        if requirement is not None:
            return requirement.specs

    def get_version(self, package_name: str) -> Optional[version.Version]:
        """[summary]

        Args:
            package_name (str): [description]

        Returns:
            Optional[version.Version]: [description]
        """
        specs = self.get_specs(package_name)
        if specs:
            return version.parse(specs[0][1])
