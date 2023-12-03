#### **Решим следующую задачу:**

**<center> $-x1 + 3*x2 + 5*x3 + x4  \rightarrow  min$ </center>**

**со  ограничениями:**

$$ x1, x2, x3, x4 \in \mathbb{R^4_+} $$

**<center> $ x_1 + 4*x_2 + 4*x_3 + x_4 = 5 $ </center>**

**<center> $ x_1 + 7*x_2 + 8*x_3 + 2*x_4 = 9 $ </center>**

**<center> $ x_0 = (1, 0, 1, 0) $ </center>**

---

Перепишем заданную систему:

$$ \begin{cases}
-x_1 + 3*x_2 + 5*x_3 + x_4 + P = 0\\
x_1 + 4*x_2 + 4*x_3 + x_4 + a_1 = 5\\
x_1 + 7*x_2 + 8*x_3 + 2*x_4 + a_2 = 9
\end{cases} $$ 

Или в форме следующей матрицы:

| Базис | x1 | x2 | x3 | x4 | a1 | a2 | RHS |
|-------|----|----|----|----|----|----|-----|
|  a_1  |  1 |  4 |  4 |  1 |  1 |  0 |  5  |
|  a_2  |  1 |  7 |  8 |  2 |  0 |  1 |  9  |
|  P    | -1 |  3 |  5 |  1 |  0 |  0 |  0  |
