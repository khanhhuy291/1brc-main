import mmap
import os
import time
from concurrent.futures import ProcessPoolExecutor

# Bắt đầu đo thời gian
start_time = time.time()

CPU_COUNT = os.cpu_count()
MMAP_PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")


def to_int(x: bytes) -> int:
    if x[0] == 45:  # ASCII for "-"
        sign = -1
        idx = 1
    else:
        sign = 1
        idx = 0

    if x[idx + 1] == 46:  # ASCII for "."
        return sign * ((x[idx] * 10 + x[idx + 2]) - 528)
    else:
        return sign * ((x[idx] * 100 + x[idx + 1] * 10 + x[idx + 3]) - 5328)


def process_line(line, result):
    idx = line.find(b";")
    city = line[:idx]
    temp_float = to_int(line[idx + 1 : -1])

    if city in result:
        item = result[city]
        item[0] += 1
        item[1] += temp_float
        item[2] = min(item[2], temp_float)
        item[3] = max(item[3], temp_float)
    else:
        result[city] = [1, temp_float, temp_float, temp_float]


def align_offset(offset, page_size):
    return (offset // page_size) * page_size


def process_chunk(file_path, start_byte, end_byte):
    offset = align_offset(start_byte, MMAP_PAGE_SIZE)
    result = {}

    with open(file_path, "rb") as file:
        length = end_byte - offset
        with mmap.mmap(file.fileno(), length, access=mmap.ACCESS_READ, offset=offset) as mmapped_file:
            mmapped_file.seek(start_byte - offset)
            for line in iter(mmapped_file.readline, b""):
                process_line(line, result)
    return result


def reduce(results):
    final = {}
    for result in results:
        for city, item in result.items():
            if city in final:
                city_result = final[city]
                city_result[0] += item[0]
                city_result[1] += item[1]
                city_result[2] = min(city_result[2], item[2])
                city_result[3] = max(city_result[3], item[3])
            else:
                final[city] = item
    return final


def read_file_in_chunks(file_path):
    file_size_bytes = os.path.getsize(file_path)
    base_chunk_size = file_size_bytes // CPU_COUNT
    chunks = []

    with open(file_path, "r+b") as file:
        with mmap.mmap(file.fileno(), length=0, access=mmap.ACCESS_READ) as mmapped_file:
            start_byte = 0
            for _ in range(CPU_COUNT):
                end_byte = min(start_byte + base_chunk_size, file_size_bytes)
                end_byte = mmapped_file.find(b"\n", end_byte)
                end_byte = end_byte + 1 if end_byte != -1 else file_size_bytes
                chunks.append((file_path, start_byte, end_byte))
                start_byte = end_byte

    # Sử dụng ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=CPU_COUNT) as executor:
        futures = [executor.submit(process_chunk, *chunk) for chunk in chunks]
        results = [future.result() for future in futures]

    final = reduce(results)
    with open("answer.txt", "w") as f:
        f.write(
            "\nbootyv4___ ".join(
                f"{loc.decode()}={0.1*val[2]:.1f}/{(0.1*val[1] / val[0]):.1f}/{0.1*val[3]:.1f}"
                for loc, val in sorted(final.items())
            )
        )


if __name__ == "__main__":
    read_file_in_chunks("data/measurements.txt")
    # Kết thúc đo thời gian
    end_time = time.time()
    elapsed_time = end_time - start_time  # Tính thời gian chạy
    print(f"Thời gian chạy doug_booty3___ : {elapsed_time:.4f} giây")
