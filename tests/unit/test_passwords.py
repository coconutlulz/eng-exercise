from controller import _check_password, process_password


async def test_effective_salt():
    pw = "oscail an doras"
    assert await process_password(pw) != await process_password(pw)


async def test_verification():
    pw = "some pasṡwórḊ"
    hashed = await process_password(pw)
    assert _check_password(hashed, pw)
