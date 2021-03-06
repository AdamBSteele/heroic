#!/usr/bin/env python

import pytest
import requests
from requests.adapters import HTTPAdapter
import urllib.parse
from urllib3.util.retry import Retry
import time

pytest_plugins = ['docker_compose']


class HeroicSession(requests.Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super(HeroicSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs):
        url = urllib.parse.urljoin(self.prefix_url, url)
        return super(HeroicSession, self).request(method, url, *args, **kwargs)


@pytest.fixture(scope='session')
def api_session(session_scoped_container_getter):
    """Wait for the Heroic container to become available and return a requests session."""

    container = session_scoped_container_getter.get('heroic')
    assert container.is_running

    # Wait for Heroic to startup within 2 minutes
    timeout = 120
    max_time = time.time() + 120
    while time.time() < max_time:
        if 'Startup finished, hello' in container.logs().decode():
            break
        else:
            time.sleep(2)
    else:
        raise TimeoutError('Heroic did not start within {} seconds'.format(timeout))

    api_url = 'http://127.0.0.1:{}/'.format(container.network_info[0].host_port)
    request_session = HeroicSession(api_url)
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    request_session.mount('http://', HTTPAdapter(max_retries=retries))
    return request_session


def test_loading(api_session):
    resp = api_session.get('/status', timeout=10)
    assert resp.ok
    status = resp.json()

    assert status['ok']
    assert status['consumers']['ok']
    assert status['backends']['ok']
    assert status['metadataBackend']['ok']
    assert status['cluster']['ok']
