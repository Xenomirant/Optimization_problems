#### **Решим следующую задачу:**

**<center> $-x1 + 3*x2 + 5*x3 + x4  \rightarrow  min$ </center>**

**с  ограничениями:**

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

| Базис         | x<sub>1</sub> | x<sub>2</sub> | x<sub>3</sub> | x<sub>4</sub> | a<sub>1</sub> | a<sub>2</sub> | RHS |
|---------------|---------------|---------------|---------------|---------------|---------------|---------------|-----|
| a<sub>1</sub> | 1             | 4             | 4             | 1             | 1             | 0             |  5  |
| a<sub>2</sub> | 1             | 7             | 8             | 2             | 0             | 1             |  9  |
| P             | -1            | 3             | 5             | 1             | 0             | 0             |  0  |

Однако в связи с тем, что нам дана начальная точка, будем ориентироваться на неё. 
Внесем в базис сначала точку x<sub>3</sub>.


| Базис         | x<sub>1</sub> | x<sub>2</sub> | x<sub>3</sub> | x<sub>4</sub> | a<sub>1</sub> | a<sub>2</sub> | RHS  |
|---------------|---------------|---------------|---------------|---------------|---------------|---------------|------|
| a<sub>1</sub> | 1/2           | 1/2           | 0             | 0             | 1             | 1/2           | 1/2  |
| x<sub>3</sub> | 1/8           | 7/8           | 1             | 1/4           | 0             | 1/8           | 9/8  |
| P             | 13/8          | 11/8          | 0             | 1/4           | 0             | 5/8           | 45/8 |

И точку x<sub>1</sub>, получая значения коэфициентов в точке x = (1, 0, 1, 0)

| Базис         | x<sub>1</sub> | x<sub>2</sub> | x<sub>3</sub> | x<sub>4</sub> | a<sub>1</sub> | a<sub>2</sub> | RHS |
|---------------|---------------|---------------|---------------|---------------|---------------|---------------|-----|
| x<sub>1</sub> | 1             | 1             | 0             | 0             | 2             | 1             | 1   |
| x<sub>3</sub> | 0             | 3/4           | 1             | 1/4           | -1/4          | 0             | 1   |
| P             | 0             | -1/4          | 0             | 1/4           | -13/4         | -1            | 4   |

Сделаем шаг симплекс-метода из заданной точки, внося x<sub>4</sub> в базис и убирая оттуда x<sub>3</sub>:


| Базис         | x<sub>1</sub> | x<sub>2</sub> | x<sub>3</sub> | x<sub>4</sub> | a<sub>1</sub> | a<sub>2</sub> | RHS |
|---------------|---------------|---------------|---------------|---------------|---------------|---------------|-----|
| x<sub>1</sub> | 1             | 1             | 0             | 0             | 2             | 1             | 1   |
| x<sub>4</sub> | 0             | 3             | 4             | 1             | -1            | 0             | 4   |
| P             | 0             | -1            | -1            | 0             | -7/2          | -1            | 3   |

Все коэфициенты отрицательны, следовательно план не улучшаем. 

_Минимум найден._
