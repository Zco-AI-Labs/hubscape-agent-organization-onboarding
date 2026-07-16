import os
import sys
from unittest.mock import MagicMock

# 1. Mock default GCP credentials and project settings globally
os.environ["GOOGLE_CLOUD_PROJECT"] = "dummy-project"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

import google.auth
mock_creds = MagicMock()
mock_creds.token = "dummy_token"
mock_creds.valid = True
mock_creds.service_account_email = "dummy@google.com"
mock_creds.requires_scopes = False
google.auth.default = MagicMock(return_value=(mock_creds, "dummy-project"))

# 2. Run pytest
import pytest
sys.exit(pytest.main(sys.argv[1:]))
