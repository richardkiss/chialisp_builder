from pathlib import Path

import shutil
import tempfile

from chialisp_builder import ChialispBuild


def test_chialisp_build():
    here = Path(__file__).parent
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # copy files to temporary directory
        shutil.copytree(here, tmpdir, dirs_exist_ok=True)

        # create builder
        mod_file = tmpdir / "mod.clsp"
        artifact_f = ChialispBuild(include_paths=[tmpdir])
        target_path = tmpdir / "mod.hex"

        artifact_f(target_path)
        output = target_path.read_text()
        assert output == "ff10ff02ffff0182012c80\n"

        # change `b.clib`
        blib = tmpdir / "b.clib"
        blib.write_text("((defconstant CONST_B 400))")

        artifact_f(target_path)
        output = target_path.read_text()
        assert output == "ff10ff02ffff018201f480\n"

        # change `b.clib` but rewrite target file so we trick `ChialispBuild` into not rebuilding
        blib.write_text("((defconstant CONST_B 500))")
        target_path.write_text(output)

        artifact_f(target_path)
        output = target_path.read_text()
        assert output == "ff10ff02ffff018201f480\n"

        # touch `b.clib` and try again
        blib.write_text("((defconstant CONST_B 500))")

        artifact_f(target_path)
        output = target_path.read_text()
        assert output == "ff10ff02ffff0182025880\n"
