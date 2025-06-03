import numpy as np
import matplotlib.pyplot as plt

BIT_SEQUENCE = [4,8,12,16,20,24,28,32]
CONSISTENT = []

for i in BIT_SEQUENCE:
    file = open(f'mitigator_{i}bit_test.txt', 'r')
    lines = file.readlines()
    file.close()
    line = lines[-1].strip().split(' ')
    CONSISTENT.append(int(line[3][1:]))

plt.plot(BIT_SEQUENCE, CONSISTENT, marker='o')
plt.xlabel('Bit Sequence Length')
plt.ylabel('Consistent Sequence Percentage')
plt.title('Consistent Sequence Percentage vs Bit Sequence Length')
plt.xticks(BIT_SEQUENCE)
plt.grid()
plt.show()
