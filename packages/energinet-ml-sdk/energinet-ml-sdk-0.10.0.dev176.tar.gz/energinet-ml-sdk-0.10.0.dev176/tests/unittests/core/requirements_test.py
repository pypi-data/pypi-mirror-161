import os
import tempfile

import pytest
from packaging.version import Version

from energinetml.core.requirements import RequirementList

REQUIREMENTS = ["some-package==1.0.0", "another-package"]


@pytest.fixture
def requirements_list():
    with tempfile.TemporaryDirectory() as path:
        fp = os.path.join(path, "requirements.txt")

        with open(fp, "w") as f:
            f.write("\n".join(REQUIREMENTS))

        yield RequirementList.from_file(fp)


class TestRequirementList:
    def test__contains(self, requirements_list):
        """
        :param RequirementList requirements_list:
        """
        assert "some-package" in requirements_list
        assert "another-package" in requirements_list
        assert "john-doe" not in requirements_list

    @pytest.mark.parametrize("package", ("some-package", "another-package"))
    def test__get__requirement_exists__should_return_requirement_object(
        self, package, requirements_list
    ):
        """
        :param str package:
        :param RequirementList requirements_list:
        """
        requirement = requirements_list.get(package)

        assert hasattr(requirement, "name")
        assert hasattr(requirement, "specs")

    def test__get__requirement_does_not_exists__should_return_none(
        self, requirements_list
    ):
        """
        :param RequirementList requirements_list:
        """
        assert requirements_list.get("john-doe") is None

    @pytest.mark.parametrize(
        "package, specs", (("some-package", [("==", "1.0.0")]), ("another-package", []))
    )
    def test__get_specs__should_return_correct_specs(
        self, package, specs, requirements_list
    ):
        """
        :param str package:
        :param typing.List[typing.Optional[str]] specs:
        :param RequirementList requirements_list:
        """
        assert requirements_list.get_specs(package) == specs

    @pytest.mark.parametrize(
        "package, version",
        (("some-package", Version("1.0.0")), ("another-package", None)),
    )
    def test__get_version__should_return_correct_version(
        self, package, version, requirements_list
    ):
        """
        :param str package:
        :param typing.Optional[Version] version:
        :param RequirementList requirements_list:
        """
        assert requirements_list.get_version(package) == version
