from denethor.core.model import Statistics
from denethor.core.repository import StatisticsRepository

class StatisticsService:
    def __init__(self, statistics_repo: StatisticsRepository):
        self.statistics_repo = statistics_repo


    def get_or_create(self, statistics_dict: dict) -> list[Statistics]:
        
        statistics: list[Statistics] = []

        custom_statistics = statistics_dict["custom_statistics"]
        for act in custom_statistics:
            for stat in custom_statistics[act]:
                if stat["fieldName"] == "request_id":
                    continue
                stat_model = Statistics(
                    statistics_name=stat["fieldName"],
                    statistics_description=stat["description"],
                )
                stat_db, created = self.statistics_repo.get_or_create(stat_model)
                print(
                    f'{"Saving" if created else "Retrieving"} Statistics: {stat_db} for Activity: {act}'
                )
                statistics.append(stat_db)

        return statistics
