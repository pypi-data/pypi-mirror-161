import glob
import os
import shutil
import tempfile
import zipfile


class Archive:
    def __init__(self, filename: str, root_dir: str = None,
                 compression=zipfile.ZIP_DEFLATED) -> None:
        self.filename = filename
        self.root_dir = root_dir
        self.compression = compression
        self.ensure_dirs()

    def ensure_dirs(self):
        self.use_tempfile = self.root_dir is None
        if self.use_tempfile:
            self.root_dir = tempfile.mkdtemp()

        self.org_dir = os.path.join(self.root_dir, 'original')
        self.mod_dir = os.path.join(self.root_dir, 'modified')
        os.makedirs(self.org_dir, exist_ok=True)
        os.makedirs(self.mod_dir, exist_ok=True)

    def cleanup(self, temp_only=False):
        if self.use_tempfile:
            shutil.rmtree(self.root_dir)
            self.root_dir = None
        elif not temp_only:
            shutil.rmtree(self.org_dir)
            shutil.rmtree(self.mod_dir)

    def __del__(self):
        self.cleanup(temp_only=True)

    def unpack(self, force=False):
        if force or (not any(os.scandir(self.org_dir))):
            shutil.unpack_archive(self.filename, self.org_dir)

    def get(self, name: str, mode='o'):
        if mode == 'o':
            return os.path.join(self.org_dir, name)
        elif mode == 'm':
            return os.path.join(self.mod_dir, name)
        elif mode == 'c':
            mod_path = os.path.join(self.mod_dir, name)
            if os.path.exists(mod_path):
                return mod_path
            else:
                return os.path.join(self.org_dir, name)

        raise ValueError("mode must be 'o' (original), 'm' (modified) or 'c' (current)")

    def pack(self):
        with zipfile.ZipFile(self.filename, mode='w', compression=self.compression) as zf:
            # add non-modified element
            for path in glob.iglob(f'{self.org_dir}/**', recursive=True):
                if not os.path.isfile(path):
                    continue

                arcname = os.path.relpath(path, self.org_dir)
                # if is modified
                if os.path.isfile(os.path.join(self.mod_dir, arcname)):
                    continue

                zf.write(path, arcname)

            # add modifed element
            for path in glob.iglob(f'{self.mod_dir}/**', recursive=True):
                if not os.path.isfile(path):
                    continue

                arcname = os.path.relpath(path, self.mod_dir)
                zf.write(path, arcname)
