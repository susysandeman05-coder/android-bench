# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
from unittest.mock import patch, MagicMock
import subprocess
from pathlib import Path
from utils.task_validator.task_validator import TaskValidator


class TestTaskValidatorSubprocess(unittest.TestCase):
    def setUp(self):
        self.validator = TaskValidator(output_path="test_output.yaml")

    def test_run_command_timeout_real(self):
        """Test that run_command raises subprocess.TimeoutExpired on a real timeout."""
        command = ["sleep", "5"]
        with self.assertRaises(subprocess.TimeoutExpired):
            self.validator.run_command(command, timeout=0.1)

    def test_run_command_failure_real(self):
        """Test that run_command raises subprocess.CalledProcessError on a real failure."""
        command = ["ls", "/non/existent/directory/path/that/should/fail"]
        with self.assertRaises(subprocess.CalledProcessError):
            self.validator.run_command(command)


class TestTaskValidatorFiltering(unittest.TestCase):
    def setUp(self):
        self.validator = TaskValidator(output_path="test_output.yaml")

    @patch("utils.task_validator.task_validator.TASKS_DIR", Path("dataset/tasks"))
    @patch("utils.task_validator.task_validator.ROOT_DIR", Path("."))
    def test_detect_task_changes_excludes_base_images(self):
        # Mock run_command to return specific changed files
        self.validator.run_command = MagicMock()

        # simulated output from git diff-tree
        # dataset/tasks/task1/file.txt -> should be detected
        # dataset/tasks/task2/base_images/image.png -> should be IGNORED
        # dataset/tasks/task3/src/main.py -> should be detected
        changed_files_output = (
            "M\tdataset/tasks/task1/file.txt\n"
            "M\tdataset/tasks/base_images/task2/image.png\n"
            "M\tdataset/tasks/task3/src/main.py"
        )
        self.validator.run_command.return_value = changed_files_output

        changed_tasks = self.validator._detect_task_changes()

        self.assertIn("task1", changed_tasks)
        self.assertNotIn("task2", changed_tasks)
        self.assertIn("task3", changed_tasks)
        self.assertEqual(len(changed_tasks), 2)


if __name__ == "__main__":
    unittest.main()
