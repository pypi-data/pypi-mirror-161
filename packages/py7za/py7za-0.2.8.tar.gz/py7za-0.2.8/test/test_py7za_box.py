import unittest
from pathlib import Path
from shutil import rmtree
from py7za.py7za_box import box, CLI_DEFAULTS
from conffu import Config
from zipfile import ZipFile
from os import chdir, getcwd

CLI_DEFAULTS['output'] = 'q'


class TestPy7zaBox(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        # ensure working dir is directory of test script
        chdir(Path(__file__).parent)
        test = Path('.')
        rmtree(test / 'data')
        (test / 'data/source/sub/subsub').mkdir(parents=True, exist_ok=True)
        (test / 'data/source/sub2/').mkdir(parents=True, exist_ok=True)
        (test / 'data/source/sub3/').mkdir(parents=True, exist_ok=True)
        (test / 'data/target').mkdir(parents=True, exist_ok=True)
        (test / 'data/extra').mkdir(parents=True, exist_ok=True)
        with open('data/.gitignore', 'w') as f:
            f.write('*\n!.gitignore')
        with open('data/source/x.csv', 'w') as f:
            f.write('A,B,C\n1,2,3\n')
        with open('data/source/sub/test.txt', 'w') as f:
            f.write('Testing, 1, 2, 3')
        with open('data/source/sub/y.csv', 'w') as f:
            f.write('X,Y,Z\n0,0,0\n')
        with open('data/source/sub2/y2.csv', 'w') as f:
            f.write('X,Y,Z\n0,0,0\n')
        with open('data/source/sub3/y3.csv', 'w') as f:
            f.write('X,Y,Z\n0,0,0\n')
        # file easily mistaken for a directory
        with open('data/source/sub4', 'w') as f:
            f.write('X,Y,Z\n0,0,0\n')
        with open('data/source/sub/subsub/z.csv', 'w') as f:
            f.write('0,0,0\n')
        with open('data/source/sub/hello.txt', 'w') as f:
            f.write('Hello\nWorld\n')

    def tearDown(self) -> None:
        test = Path('.')
        rmtree(test / 'data')
        (test / 'data').mkdir(parents=True, exist_ok=True)
        with open('data/.gitignore', 'w') as f:
            f.write('*\n!.gitignore')

    async def test_box_inplace(self):
        with open('data/source/x.csv', 'rb') as f:
            original_content = f.read()
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv', '7za': '-tzip'}))
        with ZipFile('data/source/x.csv.zip') as zf:
            with zf.open('x.csv') as f:
                self.assertEqual(original_content, f.read(), 'zipped content is identical')
        self.assertFalse(Path('data/source/x.csv').is_file(), 'original was removed')

    async def test_box_inplace_wd(self):
        wd = getcwd()
        chdir('data/source')
        with open('x.csv', 'rb') as f:
            original_content = f.read()
        await box(Config(CLI_DEFAULTS | {'glob': '*.csv', '7za': '-tzip'}))
        with ZipFile('x.csv.zip') as zf:
            with zf.open('x.csv') as f:
                self.assertEqual(original_content, f.read(), 'zipped content is identical')
        self.assertFalse(Path('x.csv').is_file(), 'original was removed')
        chdir(wd)

    async def test_box_no_delete(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv', 'delete': False}))
        self.assertTrue(Path('data/source/x.csv').is_file(), 'original was not removed')

    async def test_box_create_dirs(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'target': 'data/target', 'glob': '**/*.csv',
                                         'delete': False, '7za': '-tzip'}))
        with ZipFile('data/target/x.csv.zip') as zf:
            with zf.open('x.csv') as fz:
                with open('data/source/x.csv', 'rb') as f:
                    self.assertEqual(f.read(), fz.read(), 'zipped content in root is identical')
        self.assertTrue(Path('data/target/sub/y.csv.zip').is_file(), 'file in dir zipped to subdir')
        with ZipFile('data/target/sub/y.csv.zip') as zf:
            with zf.open('y.csv') as fz:
                with open('data/source/sub/y.csv', 'rb') as f:
                    self.assertEqual(f.read(), fz.read(), 'zipped content in subdir is identical')

    async def test_box_zip_structure(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'target': 'data/target', 'glob': '**/*.csv',
                                         'delete': False, 'create_dirs': False, 'zip_structure': True,
                                         '7za': '-tzip'}))
        with ZipFile('data/target/x.csv.zip') as zf:
            with zf.open('x.csv') as fz:
                with open('data/source/x.csv', 'rb') as f:
                    self.assertEqual(f.read(), fz.read(), 'zipped content in root is identical')
        self.assertTrue(Path('data/target/y.csv.zip').is_file(), 'file in dir zipped to root')
        with ZipFile('data/target/y.csv.zip') as zf:
            with zf.open('sub/y.csv') as fz:
                with open('data/source/sub/y.csv', 'rb') as f:
                    self.assertEqual(f.read(), fz.read(), 'zipped content in subdir is identical')

    async def test_box_round_trip_zip(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv', '7za': '-tzip'}))
        self.assertFalse(Path('data/source/x.csv').is_file(), 'original is gone after box')
        self.assertTrue(Path('data/source/x.csv.zip').is_file(), 'archive exists after box')
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv.zip', 'unbox': True}))
        self.assertTrue(Path('data/source/x.csv').is_file(), 'original is back after unbox')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive removed after unbox')

    async def test_box_round_trip_7z(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv'}))
        self.assertFalse(Path('data/source/x.csv').is_file(), 'original is gone after box')
        self.assertTrue(Path('data/source/x.csv.7z').is_file(), 'archive exists after box')
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv.7z', 'unbox': True}))
        self.assertTrue(Path('data/source/x.csv').is_file(), 'original is back after unbox')
        self.assertFalse(Path('data/source/x.csv.7z').is_file(), 'archive removed after unbox')

    async def test_box_overwrite_zip(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': 'x.csv', 'delete': False, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/x.csv.zip').is_file(), 'archive exists after first box')
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': 'x.csv'}))
        self.assertFalse(Path('data/source/x.csv').is_file(), 'original is gone after box')
        with ZipFile('data/source/x.csv.zip') as zf:
            self.assertEqual(1, len(zf.filelist), 'Only one file in resulting archive')

    async def _do_test_overwrite(self, mode=None, suffix='zip'):
        with open('data/source/x.csv') as f:
            content = f.read()
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': 'x.csv', 'delete': False,
                                         '7za': f'-t{suffix}'}))
        with open('data/source/x.csv', 'a') as f:
            f.write('extra')
            new_content = content + 'extra'
        if mode is None:
            await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': f'x.csv.{suffix}', 'unbox': True}))
        else:
            await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': f'x.csv.{suffix}', 'unbox': True,
                                             'overwrite': mode}))
        return content, new_content

    async def test_box_overwrite_source_skip_default(self):
        content, new_content = await self._do_test_overwrite(suffix='zip')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(new_content, f.read(), 'Content of original file untouched, no overwrite')

    async def test_box_overwrite_source_all(self):
        content, new_content = await self._do_test_overwrite('a', suffix='zip')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(content, f.read(), 'Content of original file back to original, overwritten')

    async def test_box_overwrite_source_rename_new_zip(self):
        content, new_content = await self._do_test_overwrite('u', suffix='zip')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(new_content, f.read(), 'Content of original file untouched, no overwrite')
        self.assertTrue(Path('data/source/x_1.csv').is_file(), 'extracted file was renamed')
        with open('data/source/x_1.csv') as f:
            self.assertEqual(content, f.read(), 'Extracted file contains original content')

    async def test_box_overwrite_source_rename_new_7z(self):
        content, new_content = await self._do_test_overwrite('u', suffix='7z')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(new_content, f.read(), 'Content of original file untouched, no overwrite')
        self.assertTrue(Path('data/source/x_1.csv').is_file(), 'extracted file was renamed')
        with open('data/source/x_1.csv') as f:
            self.assertEqual(content, f.read(), 'Extracted file contains original content')

    async def test_box_overwrite_source_rename_existing_zip(self):
        content, new_content = await self._do_test_overwrite('t', suffix='zip')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(content, f.read(), 'extracted file to original name, original content')
        self.assertTrue(Path('data/source/x_1.csv').is_file(), 'existing file was renamed')
        with open('data/source/x_1.csv') as f:
            self.assertEqual(new_content, f.read(), 'Existing files still contains new content')

    async def test_box_overwrite_source_rename_existing_7z(self):
        content, new_content = await self._do_test_overwrite('t', suffix='7z')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(content, f.read(), 'extracted file to original name, original content')
        self.assertTrue(Path('data/source/x_1.csv').is_file(), 'existing file was renamed')
        with open('data/source/x_1.csv') as f:
            self.assertEqual(new_content, f.read(), 'Existing files still contains new content')

    async def test_box_dir_default(self):
        await box(Config(CLI_DEFAULTS | {'glob': '**/*.csv', '7za': '-tzip'}))
        self.assertTrue(Path('data/source/x.csv.zip').is_file(), 'archive in-place default')
        self.assertTrue(Path('data/source/sub/y.csv.zip').is_file(), 'archive subs in-place default')

    async def test_box_dir_root(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source/sub', 'glob': '**/*.csv', '7za': '-tzip'}))
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'no archive in root parent')
        self.assertTrue(Path('data/source/sub/y.csv.zip').is_file(), 'archive subs in-place from root')

    async def test_box_dir_target(self):
        await box(Config(CLI_DEFAULTS | {'glob': '**/*.csv', 'target': 'data/target', '7za': '-tzip'}))
        self.assertTrue(Path('data/target/data/source/x.csv.zip').is_file(),
                        'archive in target, relative to working')
        self.assertTrue(Path('data/target/data/source/sub/y.csv.zip').is_file(),
                        'archive subs in target, relative to working')
        self.assertTrue(Path('data/target/data/source/sub/subsub/z.csv.zip').is_file(),
                        'archive sub-subs in target, relative to working')

    async def test_box_dir_target_root(self):
        await box(Config(CLI_DEFAULTS | {'glob': '**/*.csv', 'target': 'data/target', 'root': 'data/source',
                                         '7za': '-tzip'}))
        self.assertTrue(Path('data/target/x.csv.zip').is_file(),
                        'archive in target, relative to root')
        self.assertTrue(Path('data/target/sub/y.csv.zip').is_file(),
                        'archive subs in target, relative to root')
        self.assertTrue(Path('data/target/sub/subsub/z.csv.zip').is_file(),
                        'archive sub-subs in target, relative to root')

    async def test_box_dirs_no_match(self):
        await box(Config(CLI_DEFAULTS | {'glob': 'sub?', 'root': 'data/source', '7za': '-tzip'}))
        self.assertFalse(Path('data/source/sub2.zip').is_file(),
                        'no zipped subdirectory without --match_dir')

    async def test_box_dirs_match(self):
        await box(Config(CLI_DEFAULTS | {'glob': 'sub?', 'root': 'data/source', 'match_dir': True, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/sub2.zip').is_file(),
                        'zipped subdirectory in-place')
        self.assertFalse(Path('data/source/sub2').is_dir(),
                         'zipped subdirectory original removed')
        self.assertTrue(Path('data/source/sub3.zip').is_file(),
                        '2nd zipped subdirectory in-place')
        await box(Config(CLI_DEFAULTS | {'glob': 'sub?.zip', 'root': 'data/source', 'unbox': True,
                                         'unbox_multi': True}))
        self.assertTrue(Path('data/source/sub2').is_dir(),
                       'zipped subdirectory restored')
        self.assertTrue(Path('data/source/sub2/y2.csv').is_file(),
                       'zipped subdirectory contents restored')
        self.assertFalse(Path('data/source/sub2.zip').is_file(),
                         'restored sub directory archive removed')
        self.assertTrue(Path('data/source/sub3').is_dir(),
                       'zipped subdirectory restored')

    async def test_box_dirs_subdirs(self):
        with open('data/source/sub/subsub/z.csv', 'rb') as f:
            content = f.read()
        await box(Config(CLI_DEFAULTS | {'glob': 'sub', 'root': 'data/source', 'match_dir': True, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/sub.zip').is_file(),
                        'archive exists')
        with ZipFile('data/source/sub.zip') as zf:
            with zf.open('sub/subsub/z.csv', 'r') as f:
                self.assertEqual(content, f.read(), 'zipped content contains files in subdirs')

    async def test_box_dirs_match_files(self):
        await box(Config(CLI_DEFAULTS | {'glob': '**/sub?', 'match_dir': True, 'match_file': True, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/sub3.zip').is_file(),
                        'zipped subdirectories in-place')
        self.assertTrue(Path('data/source/sub4.zip').is_file(),
                        'zipped files in-place')
        await box(Config(CLI_DEFAULTS | {'glob': 'sub?.zip', 'root': 'data/source', 'unbox': True,
                                         'unbox_multi': True, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/sub3').is_dir(),
                       'zipped subdirectory restored')
        self.assertTrue(Path('data/source/sub3/y3.csv').is_file(),
                       'zipped subdirectory contents restored')
        self.assertTrue(Path('data/source/sub4').is_file(),
                       'zipped files restored')
        self.setUp()
        await box(Config(CLI_DEFAULTS | {'glob': '**/sub?', 'match_dir': True, 'match_file': False, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/sub3.zip').is_file(),
                        'zipped subdirectories in-place')
        self.assertFalse(Path('data/source/sub4.zip').is_file(),
                         'no files matched and zipped')

    async def test_box_multi_glob(self):
        await box(Config(CLI_DEFAULTS) | {'glob': ['**/*.csv', '**/*.txt'], 'root': 'data', '7za': '-tzip'})
        self.assertTrue(Path('data/source/sub/test.txt.zip').is_file(),
                       'txt files matched in multi-glob')
        self.assertTrue(Path('data/source/sub/y.csv.zip').is_file(),
                       'csv files matched in multi-glob')

    async def test_zip_archives(self):
        await box(Config(CLI_DEFAULTS) | {'glob': '**/*', 'root': 'data', '7za': '-tzip'})
        self.assertTrue(Path('data/source/sub/test.txt.zip').is_file(),
                       'txt files matched in catch all')
        self.assertTrue(Path('data/source/sub/y.csv.zip').is_file(),
                       'csv files matched in catch all')
        with open('data/source/new.txt', 'w') as f:
            f.write('test')
        await box(Config(CLI_DEFAULTS) | {'glob': '**/*', 'root': 'data', '7za': '-tzip'})
        self.assertTrue(Path('data/source/new.txt.zip').is_file(),
                       'new txt files matched in catch all')
        await box(Config(CLI_DEFAULTS) | {'glob': '**/*.zip', 'unbox': True, 'root': 'data', '7za': '-tzip'})
        self.assertFalse(Path('data/source/sub/test.txt.zip').is_file(),
                         'zip files were not rezipped and')
        self.assertTrue(Path('data/source/sub/test.txt').is_file(),
                       'original content from previously created archive extracted')

    async def test_unbox_multi(self):
        await box(Config(CLI_DEFAULTS | {'glob': '**/sub', 'match_dir': True, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/sub.zip').is_file(),
                        'zipped files in sub in single archive')
        await box(Config(CLI_DEFAULTS | {'glob': '**/*.zip', 'unbox': True, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/sub.zip').is_file(),
                        'default unbox_multi False, archive not extracted')
        await box(Config(CLI_DEFAULTS | {'glob': '**/*.zip', 'unbox': True, 'unbox_multi': True, '7za': '-tzip'}))
        self.assertTrue(Path('data/source/sub/y.csv').is_file() and Path('data/source/sub/test.txt').is_file(),
                        'unbox_multi True, files extracted')
        self.assertFalse(Path('data/source/sub.zip').is_file(),
                         'unbox_multi True, archive removed')
