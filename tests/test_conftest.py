import pytest


def test_basic_compile_test(basic_compile_test):
    compile_result = basic_compile_test('.rst', '''\
        .. raw:: html
        
            <iframe src="foo" height="bar">spam</iframe>
    ''')

    compile_result.assert_contains('iframe', attributes={'src': 'foo'}, text='spam')

    with pytest.raises(Exception, match=r'<eggs> not in'):
        compile_result.assert_contains('eggs')
