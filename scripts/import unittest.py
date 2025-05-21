import unittest
from pathlib import Path

class TestDocumentationAndFiles(unittest.TestCase):
    def test_readme_contains_updates(self):
        # Check that the master document (e.g., README.md or CHANGELOG.md) contains new symbols.
        readme_path = Path('README.md')
        self.assertTrue(readme_path.exists(), "README.md does not exist")
        content = readme_path.read_text(encoding='utf-8')
        self.assertIn("Console", content, "README.md should reference 'Console'")
        self.assertIn("Progress", content, "README.md should reference 'Progress'")

    def test_markup_py_updated(self):
        # Check that markup.py has changes reflecting the master document updates.
        markup_path = Path('markup.py')
        self.assertTrue(markup_path.exists(), "markup.py does not exist")
        content = markup_path.read_text(encoding='utf-8')
        # Adjust the expected marker/comment below to match an update note present in your file.
        self.assertIn("# Updated by master document", content, 
                      "markup.py should contain an update comment from master document")

    def test_main_py_updated(self):
        # Check that __main__.py has changes reflecting the master document updates.
        main_path = Path('__main__.py')
        self.assertTrue(main_path.exists(), "__main__.py does not exist")
        content = main_path.read_text(encoding='utf-8')
        # Adjust the expected marker/comment below to match an update note present in your file.
        self.assertIn("# Updated by master document", content, 
                      "__main__.py should contain an update comment from master document")

if __name__ == '__main__':
    unittest.main()