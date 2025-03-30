import multiprocessing as mp
import os

def read_matrix_from_file(filename):
    """
    Считывает матрицу из текстового файла.
    Предполагается, что строки файла содержат числа, разделенные пробелами.
    """
    matrix = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():  # игнорируем пустые строки
                row = list(map(float, line.strip().split()))
                matrix.append(row)
    return matrix

def write_matrix_to_file(matrix, filename):
    """
    Записывает матрицу в текстовый файл.
    """
    with open(filename, 'w') as f:
        for row in matrix:
            line = ' '.join(map(str, row))
            f.write(line + '\n')

def compute_element(args):
    """
    Функция вычисления поэлементного произведения.
    Принимает в качестве аргументов:
      i, j          - индексы элемента, который надо вычислить,
      a_val, b_val  - соответствующие значения из матриц,
      filename      - имя промежуточного файла (для добавления результата).
    Функция сразу дописывает вычисленное значение в промежуточный файл в формате:
      i j value
    (Такая запись позволит при последующем чтении понять, куда поместить значение.)
    """
    i, j, a_val, b_val, inter_filename, lock = args
    product = a_val * b_val
    # Запись результата в промежуточный файл сразу после вычисления
    # Используем блокировку (lock) для избежания одновременной записи из разных процессов.
    with lock:
        with open(inter_filename, 'a') as f:
            # формат записи: индекс строки, индекс столбца, значение
            f.write(f"{i} {j} {product}\n")
    return (i, j, product)

def initialize_intermediate_file(filename):
    """
    Инициализирует (очищает) промежуточный файл.
    """
    with open(filename, 'w') as f:
        pass  # просто очищаем файл

def main():
    # Задаем имена файлов исходных матриц и результирующего файла
    matrix_file1 = 'matrix1.txt'
    matrix_file2 = 'matrix2.txt'
    intermediate_file = 'intermediate.txt'
    result_file = 'result.txt'
    
    # Считываем матрицы
    mat1 = read_matrix_from_file(matrix_file1)
    mat2 = read_matrix_from_file(matrix_file2)
    
    # Проверяем размеры матриц (допустим одинаковые размеры)
    if len(mat1) != len(mat2) or any(len(r1) != len(r2) for r1, r2 in zip(mat1, mat2)):
        raise ValueError("Матрицы должны быть одинакового размера для поэлементного умножения!")
    
    rows = len(mat1)
    cols = len(mat1[0])
    
    # Инициализируем промежуточный файл
    initialize_intermediate_file(intermediate_file)
    
    # Количество процессов в пуле (например, фиксированное число)
    pool_size = 4  # выберите нужное количество процессов
    
    # Создаем менеджер для синхронизации и создания блокировки
    manager = mp.Manager()
    lock = manager.Lock()
    
    # Формируем список аргументов для вычислений: каждый элемент имеет вид (i, j, a_val, b_val, inter_filename, lock)
    tasks = []
    for i in range(rows):
        for j in range(cols):
            tasks.append((i, j, mat1[i][j], mat2[i][j], intermediate_file, lock))
    
    # Создаем пул процессов
    with mp.Pool(processes=pool_size) as pool:
        # Запускаем вычисления. Метод imap_unordered позволяет получить результаты по мере их завершения.
        results = pool.map(compute_element, tasks)
    
    # Инициализируем результирующую матрицу нулями
    result_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # Заполняем результирующую матрицу значениями, полученными из пула
    for i, j, product in results:
        result_matrix[i][j] = product
    
    # Записываем результирующую матрицу в файл
    write_matrix_to_file(result_matrix, result_file)
    
    print("Вычисления завершены.")
    print(f"Промежуточные результаты записаны в файл: {intermediate_file}")
    print(f"Результирующая матрица записана в файл: {result_file}")

if __name__ == '__main__':
    main()
