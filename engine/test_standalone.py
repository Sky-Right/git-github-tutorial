"""Small regression checks for the opt-in HTML bundler and the course assets."""
import base64
import tempfile
import unittest
from pathlib import Path
from build import make_html, make_standalone_html, split_slides


class StandaloneTest(unittest.TestCase):
    def test_bundles_relative_assets_and_escapes_script_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'dist').mkdir()
            (root / 'content').mkdir()
            (root / 'style.css').write_text('body { background: url("icon.svg"); }')
            (root / 'script.js').write_text('const tag = "</script>";')
            icon = b'<svg xmlns="http://www.w3.org/2000/svg"/>'
            (root / 'icon.svg').write_bytes(icon)
            template = '<title>@@TITLE@@</title><link rel="stylesheet" href="../style.css"><textarea>@@MARKDOWN@@</textarea><script src="../script.js"></script>'
            out = make_standalone_html('![Icon](../icon.svg)', 'A & B', template,
                                       root / 'content' / 'deck.md', root / 'dist')
            self.assertIn('<title>A &amp; B</title>', out)
            self.assertEqual(out.count(base64.b64encode(icon).decode()), 2)
            self.assertIn(r'<\/script>', out)
            self.assertNotIn('src=', out)
            self.assertNotIn('href=', out)

    def test_missing_or_remote_assets_fail_before_output(self):
        for name, error in [('missing.svg', FileNotFoundError), ('https://example.com/x.svg', ValueError)]:
            with self.assertRaises(error):
                make_standalone_html(f'![x]({name})', 'x', '@@MARKDOWN@@', Path('/tmp/x.md'), Path('/tmp'))

    def test_existing_html_path_is_unchanged(self):
        self.assertEqual(make_html('# Hi', 'A & B', '@@TITLE@@:@@MARKDOWN@@'), 'A &amp; B:# Hi')

    def test_textarea_preserves_literal_html_entities(self):
        rendered = make_html('<pre>&lt;h1&gt; &amp;</pre>', 'x', '<textarea>@@MARKDOWN@@</textarea>')
        self.assertIn('&lt;pre&gt;&amp;lt;h1&amp;gt; &amp;amp;&lt;/pre&gt;', rendered)

    def test_course_has_notes_and_existing_local_images(self):
        import re
        root = Path(__file__).resolve().parents[1]
        markdown = (root / 'content/git-en.md').read_text()
        for slide in split_slides(markdown):
            self.assertIn('???', slide)
        for src in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', markdown):
            self.assertTrue((root / 'content' / src).is_file(), src)


if __name__ == '__main__':
    unittest.main()
