import numpy as np
import sympy as sym
from abc import ABC
import typing
from . import _parsers
import matplotlib.pyplot as plt
from warnings import warn


class AbstractOptimizer(ABC):
    def __init__(self, x0: np.array, function: typing.Union[sym.Expr, str], *args, eps: float = 1e-7,
                 max_steps: int = 1000, **kwargs) -> None:

        if not isinstance(function, sym.Expr):
            raise ValueError("Function must be a valid sympy expression!")

        if x0.size < len(function.free_symbols):
            raise ValueError(f"Function has more dimensions: {len(function.free_symbols)} "
                             f"than specified for x0: {x0.size}")

        self._get_free_symbols = lambda x: sorted(x.free_symbols, key=lambda s: s.name)
        self.x0 = x0
        self._x = x0
        self._iterations = None
        self.function = function
        self.vars = self._get_free_symbols(function)
        self.max_steps = max_steps
        self.eps = eps
        self._done = False
        self._path = None
        self._gradient = []
        self._num_grad = None
        self._steps = []
        self._values = []
        self._lr_type = None
        self._lr_params = None

        for var in self.vars:
            self._gradient.append(-function.diff(var))

        return

    def substitute(self, function: typing.Union[sym.Expr, sym.MatrixExpr], x: np.array) -> np.array:

        return function.subs(
            dict(
                zip(
                    self.vars, x
                )
            )
        )

    def stop_criterion(self, iteration: int, x: np.array, f_x: float) -> bool:

        # stop if gradients are zero
        if np.linalg.norm(self._num_grad) <= self.eps:
            return True

        # stop if max_steps exceeded
        if iteration > self.max_steps:
            return True

        # stop if argument step is too small
        if np.linalg.norm(x - self._steps[-1]) < self.eps:
            return True
        # stop if function step is too small
        if np.abs(f_x - float(self._values[-1])) < self.eps**(3/2):
            return True
        return False

    def plot(self, vmin: typing.Optional[float] = None, vmax: typing.Optional[float] = None):
        if len(self.vars) > 2:
            raise Exception(f"Multidimensional visualizations are not implemented yet! "
                            f"Got {len(self.vars)} input dimensions.")

        if not self._done:
            raise Exception("Optimisation must be run first!")

        def to_string(array: np.array) -> str:
            return np.array2string(array, formatter={'float_kind': lambda value: "%.2e" % float(value)})

        area = 1.2*max(abs(self.x0 - self._steps[-1]))

        x = np.linspace(self._steps[-1][0]+area, self._steps[-1][0]-area, 1000)

        y = np.linspace(self._steps[-1][1]+area, self._steps[-1][1]-area, 1000)

        X, Y = np.meshgrid(x, y)

        fun = sym.lambdify(self.vars, self.function)

        Z = fun(X, Y)

        x, y = zip(*self._steps)

        plt.ion()
        plt.figure()
        plt.scatter(*self.x0)
        plt.annotate("x0: " + to_string(self.x0)+"\nf(x): {:.2e}".format(float(self._values[0])),
                     (self.x0[0], self.x0[1]),
                     (self.x0[0]+0.025*area, self.x0[1]+0.01*area), fontsize=8)
        plt.plot(x, y, "--o", color="black")
        plt.scatter(*self._steps[-1],  color="blue", s=100)
        plt.annotate("X*: " + to_string(self._steps[-1]) + "\nf(x): {:.2e}".format(float(self._values[-1])),
                     (self._steps[-1][0], self._steps[-1][1]),
                     (self._steps[-1][0] + 0.025 * area, self._steps[-1][1] - 0.1 * area), fontsize=8)
        CS = plt.contour(X, Y, Z, vmin=vmin, vmax=vmax)
        plt.clabel(CS, CS.levels, inline=True, fontsize=10)
        plt.colorbar()
        plt.show(block=True)
        return

    @property
    def minimum(self):
        if not self._done:
            return None
        return self._path[-1][1]

    @property
    def iterations(self) -> str:
        return f"Computed in {self._iterations} iterations."

    @property
    def path(self) -> typing.Optional[typing.List]:
        if self._done:
            return self._path
        return None

    def lr(self, x, *args, **kwargs):
        return self._lr_type(x, *args, **kwargs)

    def step(self, x: np.array, **kwargs) -> np.array:
        return x + np.dot(self.lr(x, **self._lr_params), self._num_grad)

    def minimize(self, **kwargs) -> None:

        if self._done:
            return None

        self._iterations = 0

        self._steps.append(self._x)
        self._values.append(np.array([self.substitute(self.function, self._x)]).item())

        while True:

            x = self.step(self._x, **kwargs)

            f_x = np.array([self.substitute(self.function, x)], dtype=np.float32).item()
            self._iterations += 1

            # stop if values increased on iteration
            if (f_x - self._values[-1]) > 0:
                break

            if self.stop_criterion(self._iterations, x, f_x):
                self._steps.append(x)
                self._values.append(f_x)
                break

            self._x = x
            self._steps.append(x)
            self._values.append(f_x)

            if self._done:
                break

        self._done = True
        self._path = list(zip(self._steps, self._values))
        return

    def __call__(self, *args, **kwargs) -> None:
        self.minimize()
        return None


class Optimizer:

    def __init__(self, optimizer: typing.Union[typing.Type[AbstractOptimizer], str],
                 parser: _parsers.SympyParser = _parsers.SympyParser()) -> None:

        self.parser = parser

        if not (isinstance(optimizer, type) or isinstance(optimizer, str)):
            raise ValueError("Can't use optimizer. It's set wrong or not implemented")

        self.optimizer_cls = self.__set_optimizer(optimizer)
        self.optimizer = None

    @staticmethod
    def __set_optimizer(optimizer: str) -> typing.Type[AbstractOptimizer]:

        match optimizer:
            case "GradientDescent" | "GD":
                optimizer = GD
            case "Neuton" | "N":
                optimizer = Neuton
            case "ConjugateGradient" | "CG":
                optimizer = ConjugateGradient
            case "ConditionalGradient" | "ConG":
                optimizer = ConditionalGradient
            case "QuadPenalty" | "QP":
                optimizer = QuadPenalty
            case _:
                raise ValueError("Optimizer is not yet implemented")

        return optimizer

    def set_parser(self, parser: _parsers.Parser) -> None:
        self.parser = parser

    def optimize(self, x0: np.array, function: typing.Any, *args, eps: float = 1e-7, max_iter: int = 1000,
                 show: bool = True, **kwargs) -> typing.Optional[typing.List]:

        expression = self.parser(function)

        if "constraints" in kwargs:
            constraints = [self.parser(expr) for expr in kwargs.get("constraints")]
            del kwargs["constraints"]
        else:
            constraints = []

        self.optimizer = self.optimizer_cls(x0=x0, function=expression, *args, eps=eps, max_iter=max_iter,
                                            constraints=constraints, **kwargs)

        self.optimizer()

        if show:
            return self.optimizer.path
        return None

    def show(self) -> None:

        self.optimizer.plot()

        return None


class GD(AbstractOptimizer):
    """
    Computes minimum of the specified function using Stochastic Gradient descent method
    :param x0: np.array,
    :param function: sympy.Expr
    :param method: str = ["armijo"]
    :param kwargs:
    """

    def __init__(self, x0: np.array, function: sym.Expr, *args, eps: float = 1e-7, max_steps: int = 1000,
                 method: str = "armijo", **kwargs) -> None:

        super().__init__(x0=x0, function=function, eps=eps, max_steps=max_steps, **kwargs)

        match method:
            case "armijo":
                self._lr_type = self._armijo_lr
                self._lr_params = kwargs.get("armijo_params", {"alpha": 1,
                                                               "epsilon": .5,
                                                               "theta": .5})
            case _:
                raise NotImplementedError("Method does not exist or is not implemented")

        return

    def _armijo_lr(self, x, *args, **kwargs):
        """
        Computes lr using armijo's rule.
        :param x: np.array - current point in R^n
        :param alpha (>0);
        :param epsilon (from 0 to 1)
        :param theta (from 0 to 1)
        :return: lr: float
        """

        alpha = kwargs.get("alpha", 1)
        epsilon = kwargs.get("epsilon", .5)
        theta = kwargs.get("theta", .5)

        def armijo_inequality() -> bool:

            self._num_grad = np.array([self.substitute(diff, x) for diff in self._gradient], dtype=np.float32)

            left = np.array(self.substitute(self.function, x + alpha*self._num_grad), dtype=np.float32)

            right = np.array(self.substitute(self.function, x) + epsilon*alpha*(-self._num_grad.T)@self._num_grad,
                             dtype=np.float32)
            return left <= right

        while not armijo_inequality():
            alpha = theta*alpha

        return alpha


class Neuton(AbstractOptimizer):

    def __init__(self, x0: np.array, function: sym.Expr, *args, eps: float = 1e-7, max_steps: int = 1000,
                 method: str = "default", **kwargs) -> None:

        super().__init__(x0=x0, function=function, eps=eps, max_steps=max_steps, **kwargs)

        self._num_hessian = None

        match method:
            case "default":
                self._lr_type = self._neuton_lr
                self._lr_params = {}
                self._hessian = sym.hessian(self.function, self.vars)
            case _:
                raise NotImplementedError("Method does not exist or is not implemented")

        return

    def _neuton_lr(self, x: np.array, *args, **kwargs):

        self._num_hessian = np.array(self.substitute(self._hessian, x), dtype=np.float32)
        self._num_hessian = np.linalg.inv(self._num_hessian)
        self._num_grad = np.array([self.substitute(diff, x) for diff in self._gradient], dtype=np.float32)

        return self._num_hessian


class ConjugateGradient(AbstractOptimizer):

    def __init__(self, x0: np.array, function: sym.Expr, *args, eps: float = 1e-7, max_steps: int = 1000,
                 method: str = "quadratic", **kwargs) -> None:

        super().__init__(x0=x0, function=function, eps=eps, max_steps=max_steps, **kwargs)

        warn("If the function is not a quadratic form, current realization is not suggested!")
        self._beta = None

        match method:
            case "quadratic":
                self._lr_type = self._quadratic_lr
                self._lr_params = {}
                self._quadratic_form = np.array(sym.hessian(self.function, self.vars), dtype=np.float32)/2
                self._bias = np.array(self.substitute(self.function, np.array([0 for var in self.vars])),
                                      dtype=np.float32).item()
            case _:
                raise NotImplementedError("Method does not exist or is not implemented")

        return

    def _quadratic_lr(self, x: np.array, *args, **kwargs):

        if self._iterations == 0:
            self._num_grad = np.array([0 for var in self.vars])
            self._beta = 0

        if self._iterations >= 1:

            first_term = np.dot(self._quadratic_form, self._num_grad)
            self._beta = (np.dot(first_term,
                                 np.array(
                                     [-self.substitute(diff, x) for diff in self._gradient], dtype=np.float32))) / \
                         (np.dot(first_term, self._num_grad))

        self._num_grad = np.array([self.substitute(diff, x) for diff in self._gradient], dtype=np.float32) + \
            self._beta*self._num_grad

        lr = -(np.dot(np.dot(2*self._quadratic_form, x) + self._bias, self._num_grad)) / \
              (2*np.dot(np.dot(self._quadratic_form, self._num_grad), self._num_grad))

        if self._iterations >= len(self.vars) - 1:
            self._done = True

        return lr


class ConditionalGradient(AbstractOptimizer):

    def __init__(self, x0: np.array, function: sym.Expr, *args, eps: float = 1e-7, max_steps: int = 1000,
                 method: str = "linearize", **kwargs) -> None:

        super().__init__(x0=x0, function=function, eps=eps, max_steps=max_steps, **kwargs)

        self.constraints = kwargs.get("constraints")

        self._constr_indices = [self.vars.index(symbol) for const in self.constraints for symbol in const.free_symbols]

        self._constraints_lam = [sym.lambdify(self.vars[index], self.constraints[n], "numpy")
                                 for n, index in enumerate(self._constr_indices)]

        match method:
            case "linearize":
                self._lr_type = self._fw_lr
                self._lr_params = {}
            case _:
                raise NotImplementedError("Method does not exist or is not implemented")

        return

    def check_constraints(self, x: np.array):
        check = [self._constraints_lam[n](x[index]) for n, index in enumerate(self._constr_indices)]
        if all(check):
            return True
        return np.argmin(check)

    def _fw_lr(self, x: np.array, *args, **kwargs):
        return 2/(self._iterations + 2)

    def step(self, x: np.array, **kwargs) -> np.array:
        self._num_grad = np.array([self.substitute(diff, x) for diff in self._gradient], dtype=np.float32)

        if np.linalg.norm(np.dot(self._lr_type(x, **kwargs), self._num_grad)) < self.eps:
            self._done = True
        x_new = x + np.dot(self._lr_type(x, **kwargs), self._num_grad)

        if self.check_constraints(x_new) is True:
            return x_new
        else:
            # identify constraints and make linear projection
            index = self.check_constraints(x_new)
            var, value = self.vars.index(
                self._get_free_symbols(self.constraints[index])[0]
            ), self.constraints[index].rhs

            x_new[var] = value

        return x_new

    def minimize(self, **kwargs) -> None:

        if self._done:
            return None

        self._iterations = 0

        self._steps.append(self._x)
        self._values.append(np.array([self.substitute(self.function, self._x)]).item())

        while True:

            x = self.step(self._x, **kwargs)
            # local condition
            if np.linalg.norm(x - self._x) <= .1:
                break

            f_x = np.array([self.substitute(self.function, x)], dtype=np.float32).item()
            self._iterations += 1

            # stop if values increased on iteration
            if (f_x - self._values[-1]) > 0:
                break

            if self.stop_criterion(self._iterations, x, f_x):
                self._steps.append(x)
                self._values.append(f_x)
                break

            self._x = x
            self._steps.append(x)
            self._values.append(f_x)

            if self._done:
                break

        self._done = True
        self._path = list(zip(self._steps, self._values))
        return


class QuadPenalty(AbstractOptimizer):

    def __init__(self, x0: np.array, function: sym.Expr, *args, eps: float = 1e-7, max_steps: int = 1000,
                 method: str = "exponential", **kwargs) -> None:

        super().__init__(x0=x0, function=function, eps=eps, max_steps=max_steps, **kwargs)

        self.constraints = kwargs.get("constraints")

        # only for testing
        self._iterations = 0

        self._l_iterations = 0

        match method:
            case "exponential":
                self._lr_type = self._exponential_lr
                self._lr_params = {}
            case "polynomial":
                self._lr_type = self._polynomial_lr
                self._lr_params = kwargs.get("lr_params", {"poly_power": 2})
            case _:
                raise NotImplementedError("Method does not exist or is not implemented")

        return

    def _exponential_lr(self, x: np.array, *args, **kwargs):
        return 2**self._iterations/2

    def _polynomial_lr(self, x: np.array, *args, **kwargs):
        return (self._iterations+1)**kwargs["lr_params"]["poly_power"]

    def step(self, x: np.array, **kwargs) -> np.array:

        lagrangian = self.function + self._lr_type(x, lr_params=self._lr_params) * \
                     sum([constraint ** 2 for constraint in self.constraints])

        gradient = []
        for var in self.vars:
            gradient.append(-lagrangian.diff(var))

        self._num_grad = np.array([self.substitute(diff, x) for diff in gradient], dtype=np.float32)

        minimizer = GD(x0=x, function=lagrangian, eps=self.eps/2, max_steps=self.max_steps//10, armijo_params={
            "alpha": 2,
            "delta": 1/4,
            "theta": 1/8
        })

        minimizer.minimize()

        self._iterations += minimizer._iterations - 1

        return minimizer._steps[-1]

    def minimize(self, **kwargs) -> None:

        if self._done:
            return None

        self._iterations = 0

        self._steps.append(self._x)
        self._values.append(np.array([self.substitute(self.function, self._x)]).item())

        while True:

            x = self.step(self._x, **kwargs)

            f_x = np.array([self.substitute(self.function, x)], dtype=np.float32).item()
            self._iterations += 1

            if self.stop_criterion(self._iterations, x, f_x):
                self._steps.append(x)
                self._values.append(f_x)
                break

            self._x = x
            self._steps.append(x)
            self._values.append(f_x)

            if self._done:
                break

        self._done = True
        self._path = list(zip(self._steps, self._values))

        return
