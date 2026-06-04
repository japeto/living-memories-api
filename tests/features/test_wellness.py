from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.features.wellness.repository import WellnessRepository
from app.features.wellness.service import WellnessService

VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"


@pytest.mark.asyncio
async def test_get_current_week_wellness_success(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    # Arrange
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    # The service calls _get_current_week_range to compute the dates.
    # To have predictable weekday indexes, we can mock datetime or we can just mock
    # the repository to return records with dates relative to "now".
    # Instead, let's just mock the _get_current_week_range to be deterministic,
    # or just use dates based on fixed days of the week.
    fixed_now = datetime(2026, 6, 4, 12, 0, 0, tzinfo=UTC)  # A Thursday
    mock_datetime = mocker.patch("app.features.wellness.service.datetime")
    mock_datetime.now.return_value = fixed_now
    mock_datetime.fromisoformat = datetime.fromisoformat
    mock_datetime.UTC = UTC

    supabase_mock.table.return_value.execute.return_value.data = [
        # Monday (index 0)
        {"created_at": "2026-06-01T10:00:00Z", "mood": "Alegría", "topic": "Familia"},
        # Tuesday (index 1)
        {"created_at": "2026-06-02T10:00:00Z", "mood": "Tristeza", "topic": "Salud"},
        # Tuesday again, higher level mood (Entusiasmo > Tristeza)
        {"created_at": "2026-06-02T18:00:00Z", "mood": "Entusiasmo", "topic": "Salud"},
        # Wednesday (index 2) - unknown mood defaults to 0.5
        {"created_at": "2026-06-03T10:00:00Z", "mood": "Desconocido", "topic": "Trabajo"},
        # Thursday (index 3)
        {"created_at": "2026-06-04T10:00:00Z", "mood": "Paz", "topic": "Familia"},
    ]

    # Act
    response = await client.get(
        "/api/v1/wellness/current-week",
        headers={"Authorization": "Bearer valid-token"},
    )

    # Assert
    assert response.status_code == 200
    resp_data = response.json()

    assert "week" in resp_data
    assert resp_data["week"] == "Del 1 al 7 de Junio"

    moods = resp_data["moods"]
    assert len(moods) == 7
    # Monday
    assert moods[0]["day"] == "L"
    assert moods[0]["level"] == 0.8
    assert moods[0]["label"] == "Alegría"

    # Tuesday (takes highest: Entusiasmo = 0.9)
    assert moods[1]["day"] == "M"
    assert moods[1]["level"] == 0.9
    assert moods[1]["label"] == "Entusiasmo"

    # Wednesday (unknown mood fallback to 0.5)
    assert moods[2]["day"] == "M"
    assert moods[2]["level"] == 0.5
    assert moods[2]["label"] == "Desconocido"

    # Thursday
    assert moods[3]["day"] == "J"
    assert moods[3]["level"] == 0.7
    assert moods[3]["label"] == "Paz"

    # Friday (no data)
    assert moods[4]["day"] == "V"
    assert moods[4]["level"] == 0.0
    assert moods[4]["label"] == "Sin registro"

    topics = resp_data["topics"]
    # Total topics: Familia (2), Salud (2), Trabajo (1)
    # Total = 5
    # Familia = 40%, Salud = 40%, Trabajo = 20%
    assert len(topics) == 3
    # Order might depend on Counter.most_common, which preserves order of occurrence for ties.
    topic_dict = {t["name"]: t["percentage"] for t in topics}
    assert topic_dict["Familia"] == 40
    assert topic_dict["Salud"] == 40
    assert topic_dict["Trabajo"] == 20


@pytest.mark.asyncio
async def test_get_current_week_wellness_empty(
    client: AsyncClient, supabase_mock: MagicMock, mocker: MockerFixture
) -> None:
    # Arrange
    mocker.patch("app.core.auth.decode_token", return_value={"sub": VALID_UUID})

    fixed_now = datetime(2026, 6, 4, 12, 0, 0, tzinfo=UTC)
    mock_datetime = mocker.patch("app.features.wellness.service.datetime")
    mock_datetime.now.return_value = fixed_now
    mock_datetime.fromisoformat = datetime.fromisoformat
    mock_datetime.UTC = UTC

    supabase_mock.table.return_value.execute.return_value.data = []

    # Act
    response = await client.get(
        "/api/v1/wellness/current-week",
        headers={"Authorization": "Bearer valid-token"},
    )

    # Assert
    assert response.status_code == 200
    resp_data = response.json()
    assert len(resp_data["topics"]) == 0
    assert len(resp_data["moods"]) == 7
    for mood in resp_data["moods"]:
        assert mood["level"] == 0.0
        assert mood["label"] == "Sin registro"


@pytest.mark.asyncio
async def test_get_current_week_wellness_unauthorized(client: AsyncClient) -> None:
    # Act
    response = await client.get("/api/v1/wellness/current-week")

    # Assert
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_service_format_week_string_different_months() -> None:
    # Arrange
    mock_repo = MagicMock(spec=WellnessRepository)
    service = WellnessService(repository=mock_repo)

    start_date = datetime(2026, 5, 25, tzinfo=UTC)
    end_date = datetime(2026, 5, 31, tzinfo=UTC)
    week_str = service._format_week_string(start_date, end_date)
    assert week_str == "Del 25 al 31 de Mayo"

    start_date_diff = datetime(2026, 5, 30, tzinfo=UTC)
    end_date_diff = datetime(2026, 6, 5, tzinfo=UTC)
    week_str_diff = service._format_week_string(start_date_diff, end_date_diff)
    assert week_str_diff == "Del 30 de Mayo al 5 de Junio"


@pytest.mark.asyncio
async def test_service_topic_aggregation_limits_to_top_4() -> None:
    # Arrange
    mock_repo = MagicMock(spec=WellnessRepository)
    # 1 of T1, 2 of T2, 3 of T3, 4 of T4, 5 of T5. Top 4 should be T5, T4, T3, T2.
    mock_repo.get_memories_for_date_range = AsyncMock(
        return_value=[
            {"created_at": "2026-06-01T10:00:00Z", "topic": "T1", "mood": None},
            *[{"created_at": "2026-06-01T10:00:00Z", "topic": "T2", "mood": None}] * 2,
            *[{"created_at": "2026-06-01T10:00:00Z", "topic": "T3", "mood": None}] * 3,
            *[{"created_at": "2026-06-01T10:00:00Z", "topic": "T4", "mood": None}] * 4,
            *[{"created_at": "2026-06-01T10:00:00Z", "topic": "T5", "mood": None}] * 5,
        ]
    )
    service = WellnessService(repository=mock_repo)

    # Act
    response = await service.get_current_week_wellness(user_id=VALID_UUID)

    # Assert
    assert len(response.topics) == 4
    topic_names = [t.name for t in response.topics]
    assert topic_names == ["T5", "T4", "T3", "T2"]
    # Total topics = 1 + 2 + 3 + 4 + 5 = 15
    # T5 = 5 / 15 = 33.33% -> 33
    # T4 = 4 / 15 = 26.66% -> 27
    # T3 = 3 / 15 = 20% -> 20
    # T2 = 2 / 15 = 13.33% -> 13
    percentages = [t.percentage for t in response.topics]
    assert percentages == [33, 27, 20, 13]
