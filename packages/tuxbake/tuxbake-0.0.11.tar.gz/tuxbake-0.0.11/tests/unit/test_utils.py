import pytest
from tuxbake.exceptions import TuxbakeRunCmdError
import os


def test_run_cmd(tmp_path):
    from tuxbake.utils import run_cmd

    cmd = "ls nofile".split()
    run_cmd(cmd, src_dir=tmp_path, fail_ok=True)
    with pytest.raises(TuxbakeRunCmdError):
        run_cmd(cmd, src_dir=tmp_path, fail_ok=False)


def test_git_init(oebuild_git_object, tmpdir_factory):

    """
    oebuild_git_object is a gobal fixture defined in conftest file.
    and we are receiving it as a tuple object (oebuild_obj, src_path_1, src_path_2, git_branch_1, git_branch_2, src_dir)
    """
    from tuxbake.utils import git_init

    oebuild_object = oebuild_git_object[0]
    src_dir = oebuild_object.src_dir
    git_init(oebuild_object, src_dir)

    # case when only url is present and not branch
    for git_obj in oebuild_object.git_trees:

        # adding ref also , so as to cover ref if block
        git_obj.ref = f"refs/heads/{git_obj.branch}"
        git_obj.branch = None

    temp_src2 = tmpdir_factory.mktemp("src2")
    git_init(oebuild_object, temp_src2)

    with pytest.raises((TuxbakeRunCmdError, FileNotFoundError)):
        git_init(oebuild_object, "/some/wrong/folder")


def test_repo_init(oebuild_repo_init_object, tmpdir_factory, tmpdir):
    from tuxbake.utils import repo_init

    oebuild = oebuild_repo_init_object
    url, branch = oebuild.repo.url, oebuild.repo.branch
    temp_src = tmpdir_factory.mktemp("test_repo_init")

    # case - checking with all right parameters ( url, branch, manifest)
    repo_init(oebuild, temp_src)

    # case - checking with all right parameters with a tag.
    oebuild.repo.branch = "refs/tags/1.0.0"
    repo_init(oebuild, temp_src)

    # case - checking with wrong branch name
    oebuild.repo.branch = "some-wrong-branch"
    with pytest.raises(TuxbakeRunCmdError):
        repo_init(oebuild, temp_src)
    oebuild.repo.branch = branch

    # case - checking with wrong url
    oebuild.repo.url = "https://gitlab.com/some/wrong/url/=?"
    with pytest.raises(TuxbakeRunCmdError):
        repo_init(oebuild, temp_src)
    oebuild.repo.url = url

    # case - checking with local manifest file
    manifest_path = oebuild.local_manifest
    local_manifest = os.path.abspath(manifest_path)
    repo_init(oebuild, tmpdir, local_manifest)

    # case - checking with wrong manishfest file name
    oebuild.repo.manifest = "some-wrong-name.xml"
    with pytest.raises(TuxbakeRunCmdError):
        repo_init(oebuild, temp_src)


def test_find_bitbake_env():

    from tuxbake.utils import find_bitbake_env

    path = os.path.abspath("tests/unit/bitbake-environment")
    assert find_bitbake_env(path, "DL_DIR")
    with pytest.raises(AssertionError):
        assert find_bitbake_env(path, "DUMMY_VAR")
