import pathlib
import tempfile
import unittest
from irisml.azureml import Job


class TestAzureML(unittest.TestCase):
    def test_job(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_filepath = pathlib.Path(temp_dir) / 'fake_config.json'
            job_filepath.write_text('{"tasks": []}')
            job = Job(job_filepath, {'env': 'value'})
            self.assertEqual(job.name, 'fake_config.json')
            self.assertTrue('fake_config.json' in job.command)
