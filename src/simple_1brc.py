import time
from datetime import timedelta


def print_stats(stats):
    formatted = ", ".join(
        [
            f"{k}={v['min']}/{v['sum']/v['count']:.1f}/{v['max']}"
            for k, v in sorted(stats.items(), key=lambda x: x[0])
        ]
    )
    print("{" + formatted + "}")


def calculate_stats(filepath: str):
    stats = {}

    with open(filepath, "rt") as f:
        for row in f:
            city, temp_str = row.strip().split(";")
            temp = float(temp_str)
            if city in stats:
                city_stats = stats[city]
                city_stats["min"] = min(city_stats["min"], temp)
                city_stats["max"] = max(city_stats["max"], temp)
                city_stats["sum"] += temp
                city_stats["count"] += 1
            else:
                stats[city] = {
                    "min": temp,
                    "max": temp,
                    "sum": temp,
                    "count": 1,
                }

    return stats


if __name__ == "__main__":
    start_time = time.monotonic()

    measurements_path = "/path/to/1br/file.txt"
    print_stats(calculate_stats(measurements_path))

    time_elapsed = round(time.monotonic() - start_time, 2)
    print(f"Total application time: {timedelta(seconds=time_elapsed)}")