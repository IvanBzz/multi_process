import multiprocessing as mp
import os
import random
import time

process_lock = None

def init_lock(l):
    global process_lock
    process_lock = l

def generate_random_square_matrix(n, min_val=0, max_val=10):
    return [[random.uniform(min_val, max_val) for _ in range(n)] for _ in range(n)]

def compute_element(args):
    i, j, a_val, b_val, inter_filename = args
    product = a_val * b_val
    global process_lock
    with process_lock:
        with open(inter_filename, 'a') as f:
            f.write(f"{i} {j} {product}\n")
    return (i, j, product)

def multiply_matrices_elementwise(mat1, mat2, inter_filename, pool_size, lock):
    if len(mat1) != len(mat2) or any(len(r1) != len(r2) for r1, r2 in zip(mat1, mat2)):
        raise ValueError("Матрицы должны иметь одинаковые размеры!")
    n = len(mat1)
    tasks = []
    for i in range(n):
        for j in range(n):
            tasks.append((i, j, mat1[i][j], mat2[i][j], inter_filename))
    with mp.Pool(processes=pool_size, initializer=init_lock, initargs=(lock,)) as pool:
        results = pool.map(compute_element, tasks)
    result_matrix = [[0 for _ in range(n)] for _ in range(n)]
    for i, j, product in results:
        result_matrix[i][j] = product
    return result_matrix

def consumer(queue, inter_filename, result_queue, pool_size, stop_marker):
    while True:
        item = queue.get()
        if item == stop_marker:
            print("Получен сигнал остановки потребителя.")
            break
        mat1, mat2, matrix_id = item
        with open(inter_filename, 'w') as f:
            pass
        print(f"Начинается перемножение матриц с ID {matrix_id}")
        lock = mp.Lock()
        result_matrix = multiply_matrices_elementwise(mat1, mat2, inter_filename, pool_size, lock)
        print(f"Перемножение матриц с ID {matrix_id} завершено. Результат записан в {inter_filename}")
        result_queue.put((matrix_id, result_matrix))
        time.sleep(0.1)

def producer(queue, n, iterations, delay, stop_marker):
    for i in range(iterations):
        mat1 = generate_random_square_matrix(n)
        mat2 = generate_random_square_matrix(n)
        print(f"Сгенерированы матрицы с ID {i}")
        queue.put((mat1, mat2, i))
        time.sleep(delay)
    queue.put(stop_marker)
    print("Генерация матриц завершена и послан сигнал остановки.")

def main():
    matrix_size = 4
    iterations = 5
    delay = 1
    inter_filename = 'intermediate.txt'
    pool_size = mp.cpu_count()
    print(f"Используем {pool_size} процессов для вычислений.")
    work_queue = mp.Queue()
    result_queue = mp.Queue()
    stop_marker = "STOP"
    consumer_process = mp.Process(target=consumer, args=(work_queue, inter_filename, result_queue, pool_size, stop_marker))
    consumer_process.start()
    producer_process = mp.Process(target=producer, args=(work_queue, matrix_size, iterations, delay, stop_marker))
    producer_process.start()
    producer_process.join()
    consumer_process.join()
    while not result_queue.empty():
        matrix_id, result_matrix = result_queue.get()
        print(f"\nРезультат перемножения матриц с ID {matrix_id}:")
        for row in result_matrix:
            print(row)
    print("Все процессы завершены.")

if __name__ == '__main__':
    main()
