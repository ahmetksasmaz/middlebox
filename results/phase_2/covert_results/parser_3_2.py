import os
import sys


file = open('exp3_2_working.txt', 'r')

lines = file.readlines()
file.close()

sum_tx = []
sum_rx = []

sum_tx.append(0)
sum_rx.append(0)

for line in lines:
    if line == '\n':
        sum_tx.append(0)
        sum_rx.append(0)
        continue
    else:
        left = line.split(",")[0]
        right = line.split(",")[1]

        left = int(left)
        right = int(right)
        sum_tx[-1] += left
        sum_rx[-1] += right

sumsum_tx = sum(sum_tx)
sumsum_rx = sum(sum_rx)

mean_tx = sum(sum_tx) / len(sum_tx)
mean_rx = sum(sum_rx) / len(sum_rx)

std_tx = 0
std_rx = 0

for i in range(len(sum_tx)):
    std_tx += (sum_tx[i] - mean_tx) ** 2
    std_rx += (sum_rx[i] - mean_rx) ** 2
std_tx = (std_tx / len(sum_tx)) ** 0.5
std_rx = (std_rx / len(sum_rx)) ** 0.5

conf_tx = 1.96 * (std_tx / (len(sum_tx) ** 0.5))
conf_rx = 1.96 * (std_rx / (len(sum_rx) ** 0.5))

print("Total tx: ", sumsum_tx)
print("Total rx: ", sumsum_rx)
print("Mean tx: ", mean_tx)
print("Mean rx: ", mean_rx)
print("Std tx: ", std_tx)
print("Std rx: ", std_rx)
print("Conf tx: ", conf_tx)
print("Conf rx: ", conf_rx)
print("Mean - conf tx: ", mean_tx - conf_tx)
print("Mean + conf tx: ", mean_tx + conf_tx)