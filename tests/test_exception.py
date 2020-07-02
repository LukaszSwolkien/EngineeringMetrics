import ia.common.exception as iae


def test_iaexception():
    e = iae.IAException()
    assert str(e) == 'IAException'

    e = iae.IAException(status_code=404)
    assert str(e) == 'IAException - status code: 404'

    e = iae.IAException(status_code=404, text="page no found")
    assert str(e) == 'IAException - status code: 404\ntext: page no found'

    e = iae.IAException(status_code=404, text="page no found", url='ut.test.url')
    assert str(e) == 'IAException - status code: 404 url: ut.test.url\ntext: page no found'

