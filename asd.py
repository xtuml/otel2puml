from tqdm import tqdm
import time

# Example 1: Progress bar for a simple loop
print("Progress Bar for a Simple Loop")
for i in tqdm(range(100)):
    # Simulate some work being done
    time.sleep(0.1)

# Example 2: Progress bar with additional description
print("\nProgress Bar with Description")
for i in tqdm(range(100), desc="Processing"):
    # Simulate some work being done
    time.sleep(0.1)

# Example 3: Progress bar with a defined total
print("\nProgress Bar with a Defined Total")
total_work = 50
with tqdm(total=total_work) as pbar:
    for _ in range(5):
        time.sleep(1)
        pbar.update(10)

# Example 4: Progress bar over an iterable
print("\nProgress Bar over an Iterable")
items = ["task1", "task2", "task3", "task4", "task5"]
for item in tqdm(items, desc="Tasks"):
    time.sleep(1)  # Simulate task processing

# Example 5: Nested Progress Bars
print("\nNested Progress Bars")
for i in tqdm(range(3), desc="Outer Loop"):
    for j in tqdm(range(5), desc="Inner Loop", leave=False):
        time.sleep(0.2)  # Simulate some work being done
