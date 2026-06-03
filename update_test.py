with open("tests/features/test_memories.py") as f:
    content = f.read()

content = content.replace(
    """    response = await client.post(
        "/api/v1/memories/upload",
        headers={"Authorization": "Bearer valid-token"},
        files=files,
        data=data
    )

    # FastAPI returns 500 when RuntimeError is raised
    assert response.status_code == 500""",
    """    import pytest
    with pytest.raises(RuntimeError, match="Failed to create memory in database"):
        await client.post(
            "/api/v1/memories/upload",
            headers={"Authorization": "Bearer valid-token"},
            files=files,
            data=data
        )""",
)

with open("tests/features/test_memories.py", "w") as f:
    f.write(content)
