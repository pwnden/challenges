"""Check that missing toolbox images are built from their recipe and others are pulled."""

from pathlib import Path
import os
import tomllib
import unittest
from unittest.mock import MagicMock, patch

import images
from runtime import Docker

REPOSITORY = Path(__file__).resolve().parents[1]


class ImageTests(unittest.TestCase):
    def test_every_declared_toolbox_tag_has_a_recipe(self):
        used = set()
        for manifest in (REPOSITORY / 'challenges').glob('*/challenge.toml'):
            data = tomllib.loads(manifest.read_text(encoding='utf-8'))
            for image in (data['solve']['image'], data.get('patched', {}).get('image', '')):
                if image.startswith('pwnden-cli:'):
                    used.add(image)
        self.assertTrue(used)
        for tag in used:
            self.assertIsNotNone(images.build_args(tag), tag)
        self.assertEqual(set(images.declared()), used)

    def test_build_arguments_follow_the_recipe(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('PWNDEN_IMAGE_PLATFORM', None)
            basic = images.build_args('pwnden-cli:basic-20261003')
            extended = images.build_args('pwnden-cli:extended-20261003')
        self.assertEqual(basic[:6], ['build', '--progress=quiet', '--platform', 'linux/amd64', '--target', 'basic'])
        self.assertIn('pwnden-cli:basic-20261003', basic)
        self.assertEqual(basic[-1], str(REPOSITORY / 'images/cli'))
        self.assertIn(str(REPOSITORY / 'images/cli/Dockerfile.toolbox'), extended)
        with patch.dict(os.environ, {'PWNDEN_IMAGE_PLATFORM': 'linux/arm64'}):
            self.assertIn('linux/arm64', images.build_args('pwnden-cli:basic-20261003'))
        self.assertIsNone(images.build_args('python:3.13-slim'))

    def docker(self, present):
        docker = Docker.__new__(Docker)
        docker.prepare_timeout = 300
        docker.calls = []

        def call(*args, **kwargs):
            docker.calls.append(args)
            result = MagicMock(code=0 if present else 1, stdout='{}')
            if args[:2] == ('image', 'inspect') and '--format' not in args:
                return result
            return MagicMock(code=0, stdout='null')
        docker.call = call
        return docker

    def test_missing_known_tag_is_built_not_pulled(self):
        docker = self.docker(present=False)
        docker.prepare_image('pwnden-cli:basic-20261003')
        verbs = [call[0] for call in docker.calls]
        self.assertIn('build', verbs)
        self.assertNotIn('pull', verbs)

    def test_missing_public_image_is_pulled(self):
        docker = self.docker(present=False)
        docker.prepare_image('python:3.13-slim')
        verbs = [call[0] for call in docker.calls]
        self.assertIn('pull', verbs)
        self.assertNotIn('build', verbs)

    def test_present_image_is_left_alone(self):
        docker = self.docker(present=True)
        docker.prepare_image('pwnden-cli:basic-20261003')
        verbs = [call[0] for call in docker.calls]
        self.assertNotIn('build', verbs)
        self.assertNotIn('pull', verbs)


if __name__ == '__main__':
    unittest.main()
