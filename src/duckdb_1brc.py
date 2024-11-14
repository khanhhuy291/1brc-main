import duckdb
import time

# Bắt đầu đo thời gian
start_time = time.time()

# Kết nối và thực hiện truy vấn DuckDB
with duckdb.connect() as conn:
    data = conn.sql(
        """
        SELECT
            station_name,
            MIN(measurement) AS min_measurement,
            CAST(AVG(measurement) AS DECIMAL(8,1)) AS mean_measurement,
            MAX(measurement) AS max_measurement
        FROM READ_CSV(
            'data/measurements.txt',
            header=false,
            columns={'station_name':'VARCHAR','measurement':'DECIMAL(8,1)'},
            delim=';',
            parallel=true
        )
        GROUP BY station_name
        """
    )

    # Tạo nội dung kết quả
    result = "\nduckdb__  ".join(f"{row[0]}={row[1]}/{row[2]}/{row[3]}" for row in sorted(data.fetchall())) 

    # Ghi kết quả vào file answer.txt
    with open("answer.txt", "w") as f:
        f.write(result)

# Kết thúc đo thời gian
end_time = time.time()
elapsed_time = end_time - start_time  # Tính thời gian chạy

# In ra thời gian chạy
print(f"Thời gian chạy duckdb___: {elapsed_time:.4f} giây")
