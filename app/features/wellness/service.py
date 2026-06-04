from collections import Counter
from datetime import UTC, datetime, timedelta

from fastapi import Depends

from app.features.wellness.repository import WellnessRepository, get_wellness_repository
from app.features.wellness.schemas import MoodEntry, TopicEntry, WellnessResponse


class WellnessService:
    def __init__(self, repository: WellnessRepository):
        self.repository = repository

        self.mood_levels = {
            "Alegría": 0.8,
            "Felicidad": 0.9,
            "Entusiasmo": 0.9,
            "Paz": 0.7,
            "Tranquilidad": 0.7,
            "Tranquilo": 0.6,
            "Normal": 0.5,
            "Cansancio": 0.5,
            "Nostalgia": 0.4,
            "Ansiedad": 0.3,
            "Estrés": 0.3,
            "Miedo": 0.2,
            "Tristeza": 0.2,
            "Enojo": 0.2,
            "Frustración": 0.2,
        }
        self.default_mood_level = 0.5
        self.day_initials = ["L", "M", "M", "J", "V", "S", "D"]
        self.months_es = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]

    def _get_current_week_range(self) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        start_of_week = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_of_week = (start_of_week + timedelta(days=6)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        return start_of_week, end_of_week

    def _format_week_string(self, start_date: datetime, end_date: datetime) -> str:
        if start_date.month == end_date.month:
            month_name = self.months_es[start_date.month - 1]
            return f"Del {start_date.day} al {end_date.day} de {month_name}"
        else:
            month_start = self.months_es[start_date.month - 1]
            month_end = self.months_es[end_date.month - 1]
            return f"Del {start_date.day} de {month_start} al {end_date.day} de {month_end}"

    def _parse_created_at(self, date_str: str) -> datetime:
        if date_str.endswith("Z"):
            date_str = date_str[:-1] + "+00:00"
        return datetime.fromisoformat(date_str)

    async def get_current_week_wellness(self, user_id: str) -> WellnessResponse:
        start_of_week, end_of_week = self._get_current_week_range()
        week_str = self._format_week_string(start_of_week, end_of_week)

        memories = await self.repository.get_memories_for_date_range(
            user_id=user_id, start_date=start_of_week, end_date=end_of_week
        )

        highest_levels: dict[int, tuple[float, str]] = {}
        topics_list: list[str] = []

        for mem in memories:
            created_at = self._parse_created_at(mem["created_at"])
            day_index = created_at.weekday()

            mood_str = mem.get("mood")
            if mood_str:
                mood_str = mood_str.strip().capitalize()
                level = self.mood_levels.get(mood_str, self.default_mood_level)

                current_highest = highest_levels.get(day_index, (-1.0, ""))
                if level > current_highest[0]:
                    highest_levels[day_index] = (level, mood_str)

            topic_str = mem.get("topic")
            if topic_str:
                topics_list.append(topic_str.strip().capitalize())

        moods = [
            MoodEntry(day=self.day_initials[i], level=0.0, label="Sin registro") for i in range(7)
        ]

        for day_index, (level, label) in highest_levels.items():
            moods[day_index] = MoodEntry(day=self.day_initials[day_index], level=level, label=label)

        topic_counts = Counter(topics_list)
        total_topics = sum(topic_counts.values())
        topics_entries = []

        if total_topics > 0:
            top_topics = topic_counts.most_common(4)
            for name, count in top_topics:
                percentage = int(round((count / total_topics) * 100))
                topics_entries.append(TopicEntry(name=name, percentage=percentage))

        return WellnessResponse(week=week_str, moods=moods, topics=topics_entries)


def get_wellness_service(
    repository: WellnessRepository = Depends(get_wellness_repository),
) -> WellnessService:
    return WellnessService(repository)
