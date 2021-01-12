"""
Test that we can use the `client` fixture in our tests
"""


def test_client_fixture(testdir):
    testdata = """
               def test_client(client):
                   assert True
               """

    testconftest = """
                   pytest_plugins = ['tests.sklik_client_tester_plugin']
                   """

    testdir.makeconftest(testconftest)
    testdir.makepyfile(testdata)
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)