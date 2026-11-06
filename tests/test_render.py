"""Both renderers behind essays.render_markdown. A Roc test needs bin/render_note
and fails without it, so a green run has tested both."""
import pathlib
import stat
import subprocess
import tempfile
import unittest
from unittest import mock

import config
import essays

DOT_NOTE = '```dot\ndigraph { a -> b }\n```\n'


def choosing(renderer):
    return mock.patch.object(config, 'MARKDOWN_RENDERER', renderer)


class EachRenderer:
    renderer = None

    def setUp(self):
        chosen = choosing(self.renderer)
        chosen.start()
        self.addCleanup(chosen.stop)

    def test_front_matter_is_stripped(self):
        html = essays.render_markdown('---\nkey: value\n---\n# Title\n')
        self.assertIn('Title</h1>', html)
        self.assertNotIn('value', html)

    def test_a_dot_fence_gets_the_scripts(self):
        body = essays.view_body('notes', 'n.md', DOT_NOTE)
        self.assertIn('class="language-dot"', body)
        self.assertIn(essays.DOT_SCRIPTS, body)

    def test_a_note_without_dot_goes_without_the_scripts(self):
        body = essays.view_body('notes', 'n.md', '```python\nx = 1\n```\n')
        self.assertNotIn('class="language-dot"', body)
        self.assertNotIn(essays.DOT_SCRIPTS, body)

    def test_an_image_is_shown(self):
        self.assertIn('<img', essays.render_markdown('![alt](x.png)\n'))


class PythonRenderer(EachRenderer, unittest.TestCase):
    renderer = 'python'

    def test_a_raw_fence_stays_code(self):
        html = essays.render_markdown('```raw\n<b>x</b>\n```\n')
        self.assertIn('&lt;b&gt;x&lt;/b&gt;', html)

    def test_the_roc_program_is_not_needed(self):
        missing = pathlib.Path('/nonexistent/render_note')
        with mock.patch.object(config, 'ROC_RENDERER_BIN', missing):
            self.assertIn('<h1', essays.render_markdown('# Title\n'))


class RocRenderer(EachRenderer, unittest.TestCase):
    renderer = 'roc'

    def test_a_raw_fence_comes_through_unescaped(self):
        html = essays.render_markdown('```raw\n<div class="x">&amp;</div>\n```\n')
        self.assertIn('<div class="x">&amp;</div>', html)
        self.assertNotIn('<pre>', html)

    def test_html_outside_a_raw_fence_stays_escaped(self):
        html = essays.render_markdown('<b>x</b>\n')
        self.assertIn('&lt;b&gt;x&lt;/b&gt;', html)

    def test_an_other_fence_stays_code(self):
        html = essays.render_markdown('```python\n<b>\n```\n')
        self.assertIn('class="language-python"', html)
        self.assertIn('&lt;b&gt;', html)

    def test_an_empty_note_renders_nothing(self):
        self.assertEqual(essays.render_markdown('').strip(), '')

    def test_a_note_at_each_side_of_a_part_boundary(self):
        for length in (essays.ROC_PART_CHARS - 1, essays.ROC_PART_CHARS,
                       essays.ROC_PART_CHARS + 1):
            html = essays.render_markdown('a' * length)
            self.assertEqual(html.count('a'), length)

    def test_a_note_of_the_widest_characters_fits_each_part(self):
        emoji = '\N{GRINNING FACE}'
        count = essays.ROC_PART_CHARS * 3 + 7
        self.assertEqual(essays.render_markdown(emoji * count).count(emoji), count)


class RocFailures(unittest.TestCase):
    def setUp(self):
        chosen = choosing('roc')
        chosen.start()
        self.addCleanup(chosen.stop)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = pathlib.Path(folder.name)

    def using(self, program):
        chosen = mock.patch.object(config, 'ROC_RENDERER_BIN', program)
        chosen.start()
        self.addCleanup(chosen.stop)

    def stand_in(self, script):
        program = self.folder / 'render_note'
        program.write_text('#!/bin/sh\n' + script)
        program.chmod(program.stat().st_mode | stat.S_IXUSR)
        self.using(program)

    def test_a_missing_program_stops_the_page(self):
        self.using(self.folder / 'render_note')
        with self.assertRaisesRegex(RuntimeError, 'build_renderer.sh'):
            essays.render_markdown('# Title\n')

    def test_a_failing_program_stops_the_page(self):
        self.stand_in('echo partial\necho broken >&2\nexit 3\n')
        with self.assertRaisesRegex(RuntimeError, 'exited 3: broken'):
            essays.render_markdown('# Title\n')

    def test_a_hung_program_stops_the_page(self):
        self.stand_in('exec sleep 5\n')
        with mock.patch.object(config, 'ROC_RENDER_TIMEOUT', 0.1):
            with self.assertRaises(subprocess.TimeoutExpired):
                essays.render_markdown('# Title\n')

    def test_a_program_that_works_gives_the_page_its_output(self):
        self.stand_in('echo "<p>from the stand-in</p>"\n')
        self.assertIn('from the stand-in', essays.render_markdown('# Title\n'))


class UnknownRenderer(unittest.TestCase):
    def test_an_unknown_name_stops_the_page(self):
        with choosing('rock'):
            with self.assertRaises(KeyError):
                essays.render_markdown('# Title\n')
