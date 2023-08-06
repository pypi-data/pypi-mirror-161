import pytest

from energinetml.core.submitting import SubmitContext


@pytest.fixture
def submit_context():
    yield SubmitContext()


class TestSubmitContext:
    def test__submit_model(self, submit_context):
        """
        :param SubmitContext submit_context:
        """
        with pytest.raises(NotImplementedError):
            submit_context.submit_model()

    def test__wait_for_completion(self, submit_context):
        """
        :param SubmitContext submit_context:
        """
        with pytest.raises(NotImplementedError):
            submit_context.wait_for_completion()

    def test__download_files(self, submit_context):
        """
        :param SubmitContext submit_context:
        """
        with pytest.raises(NotImplementedError):
            submit_context.download_files()
