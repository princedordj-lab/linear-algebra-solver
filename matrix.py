import numpy as np


def get_matrix_input():
    """
    Guide users to input A and B for Gaussian elimination.

    Input format:
      - First enter the number of equations (n).
      - Then enter matrix A row by row, space-separated.
      - Then enter vector B, space-separated.

    Example for a 3x3 system:
      n = 3
      Row 1 of A: 2 -1  1
      Row 2 of A: 3  3  9
      Row 3 of A: 3  3  5
      B: 2 -1 4
    """
    print("=" * 50)
    print("Gaussian Elimination with Partial Pivoting")
    print("=" * 50)
    print()

    while True:
        try:
            n = int(input("Enter the number of equations (n): ").strip())
            if n > 0:
                break
            print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    print("\nEnter the coefficient matrix A row by row.")
    print("For each row, enter the coefficients separated by spaces.")
    print(f"Example: 2 -1 1  (for a 3x3 system)\n")

    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        while True:
            try:
                row = list(map(float, input(f"Row {i + 1} of A: ").strip().split()))
                if len(row) != n:
                    print(f"Expected {n} values, got {len(row)}. Try again.")
                    continue
                A[i, :] = row
                break
            except ValueError:
                print("Invalid numbers. Please enter numeric values separated by spaces.")

    print(f"\nEnter the right-hand side vector B ({n} values).")
    print("Enter the values separated by spaces.")
    print(f"Example: 2 -1 4  (for a 3x3 system)\n")

    b = np.zeros(n, dtype=float)
    while True:
        try:
            values = list(map(float, input("B: ").strip().split()))
            if len(values) != n:
                print(f"Expected {n} values, got {len(values)}. Try again.")
                continue
            b[:] = values
            break
        except ValueError:
            print("Invalid numbers. Please enter numeric values separated by spaces.")

    print("\n" + "-" * 50)
    print("Input summary:")
    print("-" * 50)
    print("A =")
    print(A)
    print()
    print("B =")
    print(b)
    print("-" * 50)

    return A, b, n


def gaussian_elimination_partial_pivoting(A=None, b=None):
    if A is None or b is None:
        A, b, n = get_matrix_input()
    else:
        n = len(b)
        A = A.astype(float)
        b = b.astype(float)

    Aug = np.hstack([A, b.reshape(-1, 1)]).astype(float)

    print("\nInitial Augmented Matrix:")
    print(Aug)
    print()

    for k in range(n - 1):
        p = np.argmax(np.abs(Aug[k:n, k])) + k

        if p != k:
            Aug[[k, p], :] = Aug[[p, k], :]
            print(f"Rows {k + 1} and {p + 1} swapped.\n")

        print(Aug)
        print()

        if Aug[k, k] == 0:
            raise ValueError("Matrix is singular. No unique solution exists.")

        for i in range(k + 1, n):
            factor = Aug[i, k] / Aug[k, k]
            Aug[i, :] = Aug[i, :] - factor * Aug[k, :]

        print(f"After Elimination Step {k + 1}:")
        print(Aug)
        print()

    x = np.zeros(n)
    x[n - 1] = Aug[n - 1, n] / Aug[n - 1, n - 1]

    for i in range(n - 2, -1, -1):
        x[i] = (Aug[i, n] - np.dot(Aug[i, i + 1:n], x[i + 1:n])) / Aug[i, i]

    print("Upper Triangular Matrix:")
    print(Aug[:, :n])
    print()

    print("Solution Vector:")
    print(x)
    print()

    print("NumPy Built-in Solution (verification):")
    print(np.linalg.solve(A, b))


if __name__ == "__main__":
    gaussian_elimination_partial_pivoting()