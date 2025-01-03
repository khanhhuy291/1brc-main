import mmap
import multiprocessing
import os

import time

# Bắt đầu đo thời gian
start_time = time.time()

CPU_COUNT = os.cpu_count()
MMAP_PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")

def process_line(line, result):
    idx = line.find(b";")
    decoded_line = line.decode("utf-8") 
    city = decoded_line[:idx]
    temp_float = float(decoded_line[idx+1])

    if city in result:
        item = result[city]
        item[0] += 1
        item[1] += temp_float
        if temp_float > item[2]:
            item[2] = temp_float
        if temp_float < item[3]:
            item[3] = temp_float
    else:
        result[city] = [1, temp_float, temp_float, temp_float]


# Will get OS errors if mmap offset is not aligned to page size
def align_offset(offset, page_size):
    return (offset // page_size) * page_size


def process_chunk(file_path, start_byte, end_byte):
    offset = align_offset(start_byte, MMAP_PAGE_SIZE)
    result = {}

    with open(file_path, "rb") as file:
        length = end_byte - offset

        with mmap.mmap(
            file.fileno(), length, access=mmap.ACCESS_READ, offset=offset
        ) as mmapped_file:
            mmapped_file.seek(start_byte - offset)
            for line in iter(mmapped_file.readline, b"\n"):
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
        with mmap.mmap(
            file.fileno(), length=0, access=mmap.ACCESS_READ
        ) as mmapped_file:
            start_byte = 0
            for _ in range(CPU_COUNT):
                end_byte = min(start_byte + base_chunk_size, file_size_bytes)
                while (
                    end_byte < file_size_bytes
                    and mmapped_file[end_byte : end_byte + 1] != b"\n"
                ):
                    end_byte +=1
                if end_byte < file_size_bytes:
                    end_byte+=1

    with multiprocessing.Pool(processes=CPU_COUNT) as p:
        results = p.starmap(process_chunk, chunks)

    final = reduce(results)
    
    with open("answer.txt","W") as f:
        f.write(
        "\nbootyV3___ ".join(
            f"{loc.decode()}={0.1*val[2]:.1f}/{(0.1*val[1] / val[0]):.1f}/{0.1*val[3]:.1f}"
            for loc, val in sorted(final.items())))


if __name__ == "__main__":
    read_file_in_chunks("data/measurements.txt")
    # Kết thúc đo thời gian
    end_time = time.time()
    elapsed_time = end_time - start_time  # Tính thời gian chạy
  
    # In ra thời gian chạy
    print(f"Thời gian chạy doug_bootyV1___ : {elapsed_time:.4f} giây")