"""Shared fixtures for property-based tests."""
import pytest
from hypothesis import settings, Verbosity

# Configure Hypothesis for CI/local development
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose)

# Load profile from environment or default to 'dev'
import os
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
