#################################
## Preamble
# import necessary modules/tools
# import extension as ex
import inspect
import functools
import logging
import math
import numpy as np
import pandas as pd
import scipy as sc
import sympy as sp
import sys
from typing import Optional, Tuple, Union
from types import FunctionType
#   #   #   #   #   #   #   #   #


#################################
## Universal Variables/Methods/Classes
# common functions
def _retrieve_name(var):
	r"""https://stackoverflow.com/questions/18425225/getting-the-name-of-a-variable-as-a-string"""
	callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
	return [var_name for var_name, var_val in callers_local_vars if var_val is var]

def _retrieve_expression(expression):
	expression_str = str(inspect.getsourcelines(expression)[0]).strip("['\\n']").split(" = ")[1]
	return expression_str[expression_str.find(": ")+2:]

def _alias(alias_f):
	# https://stackoverflow.com/questions/68642129/set-multiple-names-for-one-function
	def _(_):
		@functools.wraps(alias_f)
		def _(*args, **kwargs):
			return alias_f(*args, **kwargs)
		return _
	return _

def diagonality(A: tuple) -> bool:
	r"""Determines if matrix, `A` is strictly, diagonally dominant.

	Parameters
	----------
	A : tuple
		Input matrix to be tested.

	Returns
	-------
	is_strictly_diagonal : bool
		Truth value whether matrix is strictly, diagonally dominant.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	Notes
	-----
	Will write to logfile either if strictly, diagonally dominant, or if matrix, `A` is not strictly, diagonally dominant which could lead to poor solution of :math:`\mathbf{A}\vec{x} = \vec{b}`.
	"""
	matrix_name, A = _retrieve_name(A), np.array(A)
	if not(np.sum(A.shape) - A.shape[0] == A.shape[0]):
		raise IndexError(f"Matrix, '{matrix_name}' must be square!")
	i, diags, long = 0, np.zeros_like(A), np.zeros_like(A)
	while i < len(A):
		j = 0
		while j < len(A):
			aij = A[i][j]
			if i == j: long[i][j] = aij
			else: diags[i][j] = aij
			j += 1
		i += 1
	if np.sum(long) >= np.sum(diags):
		logging.info(f"Matrix, '{matrix_name}' is strictly, diagonally dominant.")
		is_strictly_diagonal = True
	else:
		logging.warning(f"Matrix, '{matrix_name}' is not strictly, diagonally dominant. Solution may be inaccurate.")
		is_strictly_diagonal = False
	# is_strictly_diagonal = ex.fast_diagonality(A)
	return is_strictly_diagonal

def eigen_values(A: tuple) -> np.ndarray:
	r"""Directly finds eigenvalues of matrix by its determinant. Not recommended for large, sparse matrices.

	Parameters
	----------
	A : tuple
		Matrix of interest.

	Returns
	-------
	lambdas : np.ndarray
		Eigenvector containing roots.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	Warnings
	--------
	Not recommended to ever use because main logic is `sympy.solve(sympy.det(A - I))` wherein `I` is the identity matrix to `A`.
	"""
	# See Also
	# --------
	matrix_name, A = _retrieve_name(A), np.array(A)
	# -------------- TODO: Fix this -------------- #
	if not(np.sum(A.shape) - A.shape[0] == A.shape[0]):
		raise IndexError(f"Matrix, '{matrix_name}' must be square!")
	sym_r = sp.Symbol("r")
	i, identityA = 0, np.zeros_like(A)
	while i < len(A):
		j = 0
		while j < len(A[0]):
			if i == j: identityA[i][j] = 1
			j += 1
		i += 1
	lambda_identity = identityA*sym_r
	determinant = sp.det(sp.Matrix(A - lambda_identity))
	roots = sp.solve(determinant)
	#roots = ex.fast_eigen_values(A)
	##reals, complexes = roots
	# -------------------------------------------- #
	lambdas = []
	for r in roots:
		r = complex(r)
		if np.imag(r) == 0: r = np.real(r)
		lambdas.append(r)
	#for c in complexes:
	#	if c == 0: lambdas.append(reals[complexes.index(c)])
	#	else: lambdas.append(complex(reals[complexes.index(c)], c))
	return np.array(lambdas)

# preceded by eigen_values

def spectral_radius(A: tuple) -> float:
	r"""Finds the spectral radius of matrix.

	Parameters
	----------
	A : tuple
		Matrix of interest.

	Returns
	-------
	rho : float
		Spectral radius.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	See Also
	--------
	EigenValues.qr_algorithm : Function to find eigenvector of matrix, `A` according to QR Algorithm.

	Notes
	-----
	:math:`\rho(\mathbf{A}) = \max|\lambda|`, where :math:`\lambda` is the set of eigenvalues for `A` [1]_.
	"""
	matrix_name, A = _retrieve_name(A), np.array(A)
	if not(np.sum(A.shape) - A.shape[0] == A.shape[0]):
		raise IndexError(f"Matrix, '{matrix_name}' must be square!")
	#rho = np.max(np.abs(eigen_values(A)))
	rho = np.max(np.abs(EigenValues(A).qr_algorithm()["Lambdas"].values[-1]))
	return rho

# preceded by spectral_radius

class Norm:
	r"""Find the natural norm of a vector or between two vectors.

	Parameters
	----------
	x, x0 : tuple
		Newly and previously (optional) approximated array.

	Attributes
	----------
	x, x0 : np.ndarray
		Newly and previously (if given) approximated array.

	Methods
	-------
	l_infinity(), l_two()
		Evaluates the :math:`l_{\infty}` or :math:`l_{2}` norm, respectively.

	Raises
	------
	IndexError
		If the input vectors are not the same length.

	Notes
	-----
	Definition [1]_:
		A matrix norm on the set of all :math:`n \times n` matrices is a real-valued function, :math:`||\cdot||`, defined on this set, satisfying for all :math:`n \times n` matrices :math:`\mathbf{A}` and :math:`\mathbf{B}` and all real numbers :math:`\alpha`:
			(i) :math:`||\mathbf{A}|| \geq 0`;
			(ii) :math:`||\mathbf{A}|| = 0` iff :math:`\mathbf{A}` is a matrix with all zero entries;
			(iii) :math:`||\alpha\mathbf{A}|| = |\alpha|||\mathbf{A}||`;
			(iv) :math:`||\mathbf{A} + \mathbf{B}|| \leq ||\mathbf{A}|| + ||\mathbf{B}||`;
			(v) :math:`||\mathbf{A}\mathbf{B}|| \leq ||\mathbf{A}||||\mathbf{B}||`

	Theorem [1]_:
		If :math:`||\cdot||` is a vector norm on :math:`\mathbb{R}^{n}`, then

		.. math::
			||\mathbf{A}|| = \underset{||\vec{x}|| = 1}{\max}||\mathbf{A}\vec{x}||
		is a matrix norm.
	"""

	def __init__(self, x: tuple, x0: Optional[tuple]=None):
		self.__vector_name, self.x = _retrieve_name(x), np.array(x)
		if not isinstance(x0, type(None)):
			self.__old_vector_name, self.x0 = _retrieve_name(x0), np.array(x0)
			if not(self.x0.shape[0] == 0 or len(x) == len(x0)):
				raise IndexError(f"'{self.__vector_name}' and '{self.__old_vector_name}' must be the same size!")
		else: self.__old_vector_name, self.x0 = "x0", x0

	# @nb.jit(nopython=True)
	def l_infinity(self) -> float:
		r"""Maximum difference between absolute sum of i'th rows.

		Returns
		-------
		norm : float
			Scalar value.

		Attributes
		----------
		norm : float
			Scalar value.

		Notes
		-----
		Best thought as "actual" distance between vectors.

		Also calculates infinity norm of matri(x/ces).

		Examples
		--------
		.. math::
			\vec{x0} &= (1, 1, 1)^{(t)} \\
			\vec{x} &= (1.2001, 0.99991, 0.92538)^{(t)} \\
			\implies ||x - x0|| &= max{|1.2001 - 1|, |0.99991 - 1|, |0.92538 - 1|} \\
			 &= 0.2001
		"""
		# evaluate and store norm, ||.||
		vec_name, x = self.__vector_name, self.x
		old_vec_name, x0 = self.__old_vector_name, self.x0
		# initialize loop
		norm_tpl = np.zeros_like(x, dtype=float)
		if isinstance(x0, type(None)):
			if np.sum(x.shape) == x.shape[0]:
				for i in range(x.shape[0]):
					norm_tpl[i] = abs(x[i])
			elif np.sum(x.shape) > x.shape[0]:
				for i in range(x.shape[0]):
					for j in range(x.shape[1]):
						norm_tpl[i] += abs(x[i][j])
		elif len(x) == len(x0):
			if np.sum(x0.shape) == x0.shape[0]:
				for i in range(x0.shape[0]):
					norm_tpl[i] = abs(x[i] - x0[i])
			elif np.sum(x0.shape) > x0.shape[0]:
				if np.sum(x.shape) > x.shape[0]:
					for i in range(x0.shape[0]):
						for j in range(x0.shape[1]):
							norm_tpl[i] += float(abs(x[i][j] - x0[i][j]))
				elif np.sum(x.shape) == np.sum(x0.shape):
					for i in range(x0.shape[0]):
						norm_tpl[i] = abs(x[i] - x0[i])
		# if no errors, then evaluate norm
		self.norm = norm = np.amax(norm_tpl)
		# if isinstance(self.x0, type(None)):
		# 	self.norm = norm = ex.fast_l_infinity(self.x)
		# else:
		# 	self.norm = norm = ex.fast_l_infinity(self.x, self.x0)
		return norm # return the l_infinity norm

	# @nb.jit(nopython=True)
	def l_two(self) -> float:
		r"""Square root of sum of differences squared along i'th row.

		Returns
		-------
		norm : float
			Scalar value.

		Attributes
		----------
		norm : float
			Scalar value.

		See Also
		--------
		spectral_radius : Function to find the spectral radius of vector.

		Examples
		--------
		.. math::
			\vec{x0} &= (1, 1, 1)^{(t)} \\
			\vec{x} &= (1.2001, 0.99991, 0.92538)^{(t)} \\
			\implies ||x - x0|| &= \sqrt{(1.2001 - 1)^{2} + (0.99991 - 1)^{2} + (0.92538 - 1)^{2}} \\
			 &= 0.21356
		"""
		# evaluate and store norm, ||.||
		if isinstance(self.x0, type(None)):
			if np.sum(self.x.shape) == self.x.shape[0]:
				discriminant = np.sum(self.x**2)
			elif np.sum(self.x.shape) > self.x.shape[0]:
				discriminant = spectral_radius(np.matmul(self.x.transpose(), self.x))
		else:
			vec = self.x - self.x0
			if np.ndim(vec) == 1:
				discriminant = np.sum(vec**2)
			else:
				discriminant = spectral_radius(np.matmul(vec.transpose(), vec))
		# evaluate and store norm, ||.||
		self.norm = norm = math.sqrt(discriminant)
		return norm # return the l_two norm

# preceded by norms.()l_infinity() and Norm().l_two()

def condition_number(
	A: tuple,
	norm_type: Optional[str]="l_two"
) -> float:
	r"""Find the condition number of a given matrix and norm type.

	Parameters
	----------
	A : tuple
		Input matrix for analysis.
	norm_type : {'l_two', 'l_infinity'}, optional
		Selects norm comparison which is 'l_two' by default.

	Returns
	-------
	K : float
		Condition number of matrix, `A`.

	Raises
	------
	ValueError
		If input `norm_type` is not understood as neither `'l_infinity'` nor `'l_two'`.

	See Also
	--------
	Norm.l_infinity : Yields the :math:`l_{\infty}` norm.
	Norm.l_two : Yields the :math:`l_{2}` norm.

	Notes
	-----
	Will write evaluation of condition number to logfile.

	Definition [1]_:
		The condition number of the non-singular matrix, :math:`\mathbf{A}` relative to a norm, :math:`||\cdot||` is

		.. math::
			K(\mathbf{A}) = ||\mathbf{A}|| \cdot ||\mathbf{A}^{-1}||

	A matrix is well-conditioned if :math:`K(\mathbf{A})` is close to 1 and is ill-conditioned if significantly greater than 1.
	"""
	matrix_name, A = _retrieve_name(A), np.array(A)
	BadNormTypeError = lambda norm_type: f"Input `norm_type`='{norm_type}' not understood. Please input 'l_infinity' or 'l_two'."
	i, A_inv = 0, np.zeros_like(A)
	while i < len(A):
		j = 0
		while j < len(A):
			aij = A[i][j]
			if aij != 0: A_inv[i][j] = 1/aij
			j += 1
		i += 1
	if norm_type == "l_infinity":
		norm, abnorm = Norm(A).l_infinity(), Norm(A_inv).l_infinity()
		# norm, abnorm = ex.fast_l_infinity(A), ex.fast_l_infinity
	elif norm_type == "l_two":
		norm, abnorm = Norm(A).l_two(), Norm(A_inv).l_two()
	else: raise ValueError(BadNormTypeError(norm_type))
	K = norm*abnorm
	logging.info(f"Condition Number K('{matrix_name}') = {K}")
	return K

def make_array(
	domain: tuple,
	function: FunctionType
	# variable: Optional[str]="x"
) -> np.ndarray:
	r"""Maps domain to range.

	Parameters
	----------
	domain : tuple
		Collection if input data.
	function : lambda
		Function that maps the domain to range.
	variable : string, optional
		String representation of variable to respect in function.

	Returns
	-------
	mapped : np.ndarray
		Mapped range from function.

	Notes
	-----
	Writes to logfile the input expression, and that the expression was in fact used.

	If the input function happens to already be a NumPy array, then that array will simply be returned without processing.
	"""
	function_name = _retrieve_name(function)
	BadFunctionError = lambda function_name: f"'{function_name}' must be a lambda expression."
	if isinstance(function, (list, tuple, np.ndarray)):
		mapped = np.array(function)
	else:
		# if isinstance(function, str):
		# 	function_str = ex.fast_parse_latex(function)
		# 	function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
		# else:
		if not isinstance(function, (FunctionType)): raise TypeError(BadFunctionError(function_name))
		logging.info(f"Input expression '{_retrieve_expression(function)}' used.")
		domain, mapped = np.array(domain), np.zeros_like(domain)
		for i in range(len(domain)):
			if np.sum(domain.shape) > np.sum(domain.shape[0]):
				for j in range(len(domain[0])):
					mapped[i][j] = (function(domain[i][j]))
			else: mapped[i] = function(domain[i])
	return mapped

def symmetry(A: tuple) -> bool:
	r"""Determines boolean truth value whether given matrix is symmetric.

	Parameters
	----------
	A : tuple
		Matrix of interest.

	Returns
	-------
	is_symmetric : bool
		True if symmetric, else False.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	Notes
	-----
	Writes to logfile that `A` is either symmetric or asymmetric.
	"""
	matrix_name, A = _retrieve_name(A), np.array(A)
	if not(np.sum(A.shape) - A.shape[0] == A.shape[0]):
		raise IndexError(f"Matrix, '{matrix_name}' must be square!")
	i, At, is_symmetric = 0, np.transpose(A), False
	for ai in A:
		j = 0
		for aj in ai:
			if aj == At[i][j]: is_symmetric = True
			else:
				is_symmetric = False
				logging.warning(f"Matrix, '{matrix_name}' is not symmetric.")
				return is_symmetric
			j += 1
		i += 1
	if is_symmetric: logging.info(f"Matrix, '{matrix_name}' is symmetric.")
	# is_symmetric = ex.fast_symmetry(A)
	return is_symmetric

def positive_definite(A: tuple) -> bool:
	r"""Determines boolean truth value whether given matrix is positive definite.

	Parameters
	----------
	A : tuple
		Matrix of interest.

	Returns
	-------
	is_positive_definite : bool
		True if positive definite, else False.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	Notes
	-----
	Writes to logfile that `A` is either positive definite or not.
	"""
	matrix_name, A = _retrieve_name(A), np.array(A)
	if not(np.sum(A.shape) - A.shape[0] == A.shape[0]):
		raise IndexError(f"Matrix, '{matrix_name}' must be square!")
	is_symmetric, obj = symmetry(A), EigenValues(A)
	if is_symmetric and tridiagonality(A):
		eigenvalues = np.array(obj.qr_algorithm()["Lambdas"].values[-1])
	else:
		df = obj.power_method(np.ones(len(A)))
		eigenvalues = df["Mu"].values[-1]*np.array(df["Lambdas"].values[-1])
	if is_symmetric and np.all(np.where(eigenvalues>=0)):
		is_positive_definite = True
	else: is_positive_definite = False
	# is_symmetric = symmetry(A)
	# xn, xt = np.reshape(x, (len(x), 1)), np.array(x)
	# y = np.matmul(np.matmul(xt, A), xn)
	# if is_symmetric and y[0] > 0: is_positive_definite = True
	# else: is_positive_definite = False
	if is_positive_definite: logging.info(f"Matrix, '{matrix_name}' is positive definite.")
	# is_symmetric = ex.fast_symmetry(A)
	return is_positive_definite

def tridiagonality(A: tuple) -> bool:
	r"""Determine boolean truth value whether given matrix is tridiagonal.

	Parameters
	----------
	A : tuple
		Matrix of interest.

	Returns
	-------
	is_tridiagonal : bool
		True if tridiagonal, else False.

	Raises
	------
	IndexError
		Matrix of interest must be square.

	Notes
	-----
	Writes to logfile that matrix is either tridiagonal or not.
	"""
	matrix_name, A = _retrieve_name(A), np.array(A)
	if not(np.sum(np.shape(A)) - np.shape(A)[0] == np.shape(A)[0]):
		raise IndexError(f"Matrix, '{matrix_name}' must be square!")
	diagonals = np.diagflat(np.diag(A))
	above = np.diagflat(np.diag(A, k=1), k=1)
	below = np.diagflat(np.diag(A, k=-1), k=-1)
	non_A = A - (diagonals + above + below)
	if np.sum(non_A) != 0:
		logging.warning(f"Matrix, '{matrix_name}' is not tridiagonal.")
		is_tridiagonal = False
	else:
		logging.info(f"Matrix, '{matrix_name}' is tridiagonal.")
		is_tridiagonal = True
	# is_tridiagonal = ex.fast_tridiagonality(A)
	return is_tridiagonal
#   #   #   #   #   #   #   #   #


#################################
## Specific Functions
# --------------------
# eigenvalue solvers
class EigenValues:
	r"""Find the characteristic (eigen) values of matrix. Typically thought as roots of polynomial from determinant.

	Parameters
	----------
	A : tuple
		Characteristic matrix.
	power : float, optional
		Signed power to which function error must be within.
	max_iter : int, optional
		Maximum iterations for which function may loop.

	Attributes
	----------
	A : np.ndarray
		Input characteristic matrix.
	tol : float
		Specified tolerance to which method terminates.
	max_iter : int
		Maximum iterations allowed for method.
	is_diagonal, is_tridiagonal : bool
		Truth value of whether matrix is diagonal and tridiagonal, respectively.

	Methods
	-------
	power_method(x: tuple)
		Determine the dominating eigenvalue and resulting eigenvector from initial guess, `x`.
	inverse_power_method(x: tuple, q: float)
		Determine the eigenvalue close to `q` and resulting eigenvector from initial guess, `x`.
	qr_algorithm()
		Directly determine eigenvector of matrix, `A`.

	Raises
	------
	IndexError
		Matrix of interest must be square.
	ValueError
		If iterations constraint is not an integer.

	Notes
	-----
	Specified tolerance evaluated by `10**power`.

	If `is_diagonal` is `True`, then matrix, `A` is strictly, diagonally dominant. Else, not strictly, diagonally dominant. Similar for `is_tridiagonal`.
	"""

	def __init__(
		self,
		A: tuple,
		power: float=-6,
		max_iter: int=100
	):
		self.__matrix_name = _retrieve_name(A)
		if np.array(A).shape[0] != np.array(A).shape[1]: raise IndexError(f"Matrix, '{self.__matrix_name}' must be square!")
		if max_iter <= 0 or not isinstance(max_iter, (int, float)): raise ValueError(f"Maximum iterations, N = {max_iter} must be an integer greater than zero.")
		self.A = A = np.array(A)
		self.tol = float(10**power)
		self.max_iter = int(max_iter)
		self.is_diagonal = diagonality(A)
		self.is_symmetric = symmetry(A)
		self.is_tridiagonal = tridiagonality(A)

	__BadVectorDataError = lambda matrix_name, matrix_shape, vector_name, vector_shape: f"'{matrix_name}' of shape {matrix_shape} and '{vector_name}' of shape {vector_shape} must be the same length!"

	def power_method(self, x: tuple) -> pd.DataFrame:
		r"""Approximate the dominant eigenvalue and associated eigenvector of matrix, `A` given some non-zero vector, `x`.

		Parameters
		----------
		vector : tuple
			Initial guess for eigenvector.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		vector : np.ndarray
			Initial guess for eigenvector.
		iterations, mu, lambdas, errors : np.ndarray
			Collection of iterations, eigenvalues, eigenvectors, and propogated errors through method.

		Raises
		------
		IndexError
			If `x` is not a one-dimensional array.
		"""
		self.__vector_name = _retrieve_name(x)
		if np.sum(np.array(x).shape) - np.array(x).shape[0] > 1: raise IndexError(f"Systems vector, '{self.__vector_name}' must be one-dimensional array!")
		if len(x) != len(self.A): raise IndexError(EigenValues.__BadVectorDataError(self.__matrix_name, self.A.shape, self.__vector_name, np.array(x).shape))
		self.x = x = np.array(x)
		mu = [Norm(x).l_infinity()]
		x = x/mu[-1]
		k, eigenvectors, errors = 1, [x], [self.tol*10]
		while errors[-1] > self.tol and k <= self.max_iter:
			y = np.matmul(self.A, x)
			for yi in y:
				if abs(yi) == Norm(y).l_infinity(): yp = float(yi)
			mu.append(yp)
			eigenvectors.append(y/yp)
			errors.append(Norm(x, eigenvectors[-1]).l_infinity())
			x = eigenvectors[-1]; k += 1
		self.iterations = np.arange(k)
		self.mu = np.array(mu)
		self.lambdas = eigenvectors
		self.errors = np.array(errors)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Mu": self.mu,
			"Lambdas":self.lambdas,
			"Errors": self.errors
		})

	def inverse_power_method(self, x: tuple, q: float) -> pd.DataFrame:
		r"""Approximate eigenvalue closest to target, `q` and associated eigenvector of matrix, `A` given some non-zero vector, `x`.

		Parameters
		----------
		x : tuple
			Initial guess for eigenvector.
		q : float
			Target to which the closest eigenvalue of matrix will be found.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		x : np.ndarray
			Initial guess at eigenvector.
		iterations, mu, lambdas, errors : np.ndarray
			Collection of iterations, eigenvalues, eigenvectors, and propogated errors through method.

		Raises
		------
		IndexError
			If `x` is not a one-dimensional array.

		Notes
		-----
		Supposed to converge faster than `power_method` [1]_.
		"""
		self.__vector_name = _retrieve_name(x)
		if np.sum(np.array(x).shape) - np.array(x).shape[0] > 1: raise IndexError(f"Systems vector, {self.__vector_name} must be one-dimensional array!")
		if len(x) != len(self.A): raise IndexError(EigenValues.__BadVectorDataError(self.__matrix_name, self.A.shape, self.__vector_name, np.array(x).shape))
		self.x = x = np.array(x)
		self.q = float(q)
		A = np.linalg.inv(self.A-q*np.identity(len(self.A)))
		mu = [1/Norm(x).l_infinity() + q]
		k, eigenvectors, errors = 1, [x], [self.tol*10]
		while errors[-1] > self.tol and k <= self.max_iter:
			y = np.matmul(A, x)
			for yi in y:
				if abs(yi) == Norm(y).l_infinity(): yp = float(yi)
			mu.append(1/yp + q)
			eigenvectors.append(y/yp)
			errors.append(Norm(x, x0=eigenvectors[-1]).l_infinity())
			x = eigenvectors[-1]; k += 1
		self.iterations = np.arange(k)
		self.mu = np.array(mu)
		self.lambdas = eigenvectors
		self.errors = np.array(errors)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Mu": self.mu,
			"Lambdas": self.lambdas,
			"Errors": self.errors
		})

	def qr_algorithm(self) -> pd.DataFrame:
		r"""Approximate dominant eigenvalue and associated eigenvector of matrix, `A` by decomposition [1]_.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		iterations, lambdas, errors : np.ndarray
			Collection of iterations, eigenvectors, and propogated errors through method.

		Warnings
		--------
		Matrix, `A` must be symmetric and tridiagonal!

		Notes
		-----
		This method is preferred over `power_method` and `inverse_power_method` by keeping round-off error to a minimum [1]_.

		Examples
		--------
		Refer to this `example <https://www.youtube.com/watch?v=FAnNBw7d0vg>`_ for an explanation and demonstration [2]_.
		"""
		# if self.is_symmetric and self.is_tridiagonal:
		A = self.A
		k, eigenvectors, errors = 1, [np.diag(A)], [self.tol*10]
		while errors[-1] > self.tol and k <= self.max_iter:
			Q = np.zeros_like(A, dtype=float)
			R = np.zeros_like(A, dtype=float)
			QI = []
			for j in range(len(A[0])):
				ai = np.array(np.zeros(len(A)))
				for i in range(len(A)):
					ai[i] = A[i][j]
				ai_perp = 0
				for i in range(j):
					R[i][j] = np.dot(ai, QI[i])
					ai_perp += R[i][j]*QI[i]
				ai -= ai_perp
				R[j][j] = np.sqrt(np.sum(ai**2))
				qi = ai/R[j][j]
				QI.append(qi)
				i = 0
				for q in qi:
					Q[i][j] = q
					i += 1
			A = np.matmul(R, Q)
			eigenvectors.append(np.diag(A))
			err = np.average([Norm(np.diag(A, k=-1)).l_infinity(), Norm(np.diag(A, k=1)).l_infinity()])
			errors.append(err); k += 1
		self.iterations = np.arange(k)
		self.lambdas = eigenvectors
		self.errors = np.array(errors)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Lambdas": self.lambdas,
			"Errors": self.errors
		})
		# else: raise ValueError(f"Matrix, {self.__matrix_name} must be symmetric!")

# solve system of equations
class SystemOfEquations:
	r"""Solve a linear system of equations (SOE): :math:`\mathbf{A}\vec{x} = \vec{b}`.

	Parameters
	----------
	A, b : tuple
		Characteristic matrix of coefficients and vector that is particular solution from SOE.
	power : float, optional
		Signed power to which function error must be within.
	max_iter : int, optional
		Maximum iterations for which function may loop.

	Attributes
	----------
	A, b : np.ndarray
		Characteristic matrix of coefficients and particular solution from SOE.
	tol : float
		Specified tolerance to which method terminates.
	max_iter : int
		Maximum iterations allowed for method.
	is_diagonal, is_positive_definite, is_symmetric, is_tridiagonal : bool
		Truth value of whether matrix is diagonal, positive definite, symmetric, and tridiagonal.

	Methods
	-------
	conjugate_gradient(x: tuple, C=None)
		Iteratively solves SOE within as many iterations as number of equations. Pre-conditions by default to solve with :math:`\sqrt{n}` iterations.
	gaussian_elimination()
		Perform Gaussian Elimination with Back-Substitution on SOE.
	steepest_descent(x: tuple)
		Iteratively solve SOE.

	Raises
	------
	IndexError
		Matrix of interest must be square.
	IndexError
		If `b` is not a one-dimensional array.
	ValueError
		If iterations constraint is not an integer.

	Notes
	-----
	Specified tolerance evaluated by `10**power`.

	If `is_diagonal` is `True`, then matrix, `A` is strictly, diagonally dominant. Else, not strictly, diagonally dominant. Similar for `is_tridiagonal`.
	"""

	def __init__(
		self,
		A: tuple,
		b: tuple,
		power: Optional[float]=-6,
		max_iter: Optional[int]=100
	):
		self.__matrix_name = _retrieve_name(A)
		if np.array(A).shape[0] != np.array(A).shape[1]: raise IndexError(f"Matrix, '{self.__matrix_name}' must be square!")
		self.__solution_name = _retrieve_name(b)
		if len(b) != len(A): raise IndexError(SystemOfEquations.__BadVectorDataError(self.__matrix_name, self.A.shape, self.__solution_name, np.array(b).shape))
		if np.sum(np.array(b).shape) - np.array(b).shape[0] > 1: raise IndexError(f"Systems vector, '{self.__solution_name}' must be one-dimensional array!")
		if max_iter <= 0 or not isinstance(max_iter, (int, float)): raise ValueError(f"Maximum iterations, N = {max_iter} must be an integer greater than zero.")
		self.A = A = np.array(A)
		self.b = np.array(b)
		self.tol = float(10**power)
		self.max_iter = int(max_iter)
		self.is_diagonal = diagonality(A)
		self.is_symmetric = symmetry(A)
		self.is_positive_definite = positive_definite(A)
		self.is_tridiagonal = tridiagonality(A)
		obj = EigenValues(A, power=power)
		if self.is_symmetric and self.is_tridiagonal:
			self.eigen_values = obj.qr_algorithm()["Lambdas"].values[-1]
		else:
			df = obj.power_method(np.ones(len(A)))
			self.eigenvalues = df["Mu"].values[-1]*np.array(df["Lambdas"].values[-1])
		self.spectral_radius = spectral_radius(A)
		self.condition_number = condition_number(A)

	__BadVectorDataError = lambda matrix_name, matrix_shape, vector_name, vector_shape: f"'{matrix_name}' of shape {matrix_shape} and '{vector_name}' of shape {vector_shape} must be the same length!"

	def conjugate_gradient(
		self,
		x: tuple,
		C: Optional[Union[tuple,bool]]=None
	) -> pd.DataFrame:
		r"""Use initial guess vector, `x` and (if desired) pre-conditioning matrix, `C` to solve SOE: :math:`\mathbf{A}\vec{x} = \vec{b}`.

		Parameters
		----------
		x : tuple
			Vector that is initial guess to solution for SOE.
		C : tuple or bool, optional
			Pre-conditioning matrix. Will pre-condition by default. If set to `True`, will use the diagonal of matrix, `A`.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		x : np.ndarray
			Initial guess for solution.
		C : None or np.ndarray
			Stores matrix used for pre-conditioning if not `None`.
		iterations, approximations, errors : np.ndarray
			Collection of iterations, approximations, and normative errors through method.

		Raises
		------
		ValueError
			If `A` is not positive definite.
		IndexError
			If `x` is not a one-dimensional array.

		Notes
		-----
		More computationally expensive than `gaussian_elimination` for smaller systems and is best suited for large, sparse matrices.
		If pre-conditioned, can solve in :math:`\sqrt{n}` iterations.
		"""
		if self.is_positive_definite:
			self.__vector_name = _retrieve_name(x)
			if np.sum(np.array(x).shape) - np.array(x).shape[0] > 1: raise IndexError(f"Systems vector, '{self.__vector_name}' must be one-dimensional array!")
			self.x = x = np.array(x)
			b, self.C = self.b, C
			r0 = b - np.matmul(self.A, x)
			if isinstance(C, type(None)):
				do_precondition = True
				v0 = r0
			elif isinstance(C, bool):
				if C == True:
					do_precondition = True
					self.C = C = np.diagflat(np.diag(self.A))
					Minv = np.linalg.inv(C*C.T)
					v0 = np.matmul(Minv, r0)
				else:
					do_precondition = False
					v0 = r0
			else:
				do_precondition = False
				self.C = C = np.array(C)
				Minv = np.linalg.inv(C*C.T)
				v0 = np.matmul(Minv, r0)
			k, approximations, errors = 1, [x], [self.tol*10]
			while errors[-1] > self.tol and k <= self.max_iter:
				if do_precondition:
					alpha = float(np.matmul(r0.T, r0)/np.matmul(np.matmul(v0.T, self.A), v0))
				else:
					alpha = float(np.matmul(np.matmul(r0.T, Minv), r0)/np.matmul(np.matmul(v0.T, self.A), v0))
				x1 = x + alpha*v0
				approximations.append(x1)
				errors.append(Norm(x1, x).l_infinity())
				r1 = r0 - alpha*np.matmul(self.A, v0)
				if do_precondition:
					s1 = float(np.matmul(r1.T, r1)/np.matmul(r0.T, r0))
				else: s1 = float(np.matmul(np.matmul(r1.T, Minv), r1)/np.matmul(np.matmul(r0.T, Minv), r0))
				x, r0 = x1, r1
				if do_precondition: v0 = r1 + s1*v0
				else: v0 = np.matmul(Minv, r1) + s1*v0
				k += 1
			self.iterations = np.arange(k)
			self.approximations = approximations
			self.errors = np.array(errors)
			return pd.DataFrame(data={
				"Iterations": self.iterations,
				"Approximations": self.approximations,
				"Errors": self.errors
			})
		else: raise ValueError(f"Matrix, {self.__matrix_name} must be positive definite.")

	def gaussian_elimination(self) -> np.ndarray:
		r"""Directly find the solution to :math:`\mathbf{A}\vec{x} = \vec{b}` by Gaussian Elimination with Back Substitution.

		Returns
		-------
		x : np.ndarray
			Input vector to SOE.

		Attributes
		----------
		Aug : np.ndarray
			Augmented matrix representation of SOE.

		Raises
		------
		ValueError
			If a unique solution could not be find which indicates linearly dependent SOE.
		"""
		n = len(self.A)
		m = n - 1
		Aug = np.zeros((n, n + 1))
		Aug[:n,:n] = self.A
		Aug[:,n] = self.b[:]
		for i in range(m):
			E = Aug
			try:
				p = np.where(Aug[i:n,i]!=0)[0][0] + i
			except:
				raise ValueError(f"No unique solution could be found.")
			if i != p:
				E[[p, i]] = E[[i, p]]
			for j in range(i+1, n):
				mji = Aug[j,i]/Aug[i,i]
				E[j,:] = E[j,:] - mji*E[i,:]
			Aug = E
		if Aug[m][m] == 0: raise ValueError(f"No unique solution could be found.")
		x = np.zeros(n)
		x[m] = Aug[m,n]/Aug[m,m]
		for i in range(m-1, -1, -1):
			aijxj = 0
			for j in range(i+1, n): aijxj += Aug[i,j]*x[j]
			x[i] = (Aug[i,n] - aijxj)/Aug[i,i]
		return x

	def steepest_descent(self, x: tuple) -> pd.DataFrame:
		r"""Approximate solution vector, x given matrix, `A` initial guess vector, `x`, and vector, `b`.

		Parameters
		----------
		x : tuple
			Initial guess for input vector to SOE.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		x : np.ndarray
			Initial guess for solution.
		iterations, approximations, errors : np.ndarray
			Collection of iterations, approximations, and normative errors through method.

		Raises
		------
		IndexError
			If `x` is not a one-dimensional array.
		"""
		self.__vector_name = _retrieve_name(x)
		if np.sum(np.array(x).shape) - np.array(x).shape[0] > 1: raise IndexError(f"Systems vector, '{self.__vector_name}' must be one-dimensional array!")
		self.x = x = np.array(x)
		k, approximations, errors = 1, [x], [self.tol*10]
		while errors[-1] > self.tol and k <= self.max_iter:
			r = self.b - np.matmul(self.A, x)
			alpha = float(np.matmul(r.T, r)/np.matmul(np.matmul(r.T, self.A), r))
			x1 = x + alpha*r
			approximations.append(x1)
			errors.append(Norm(x1, x).l_infinity())
			x = x1; k += 1
		self.iterations = np.arange(k)
		self.approximations = approximations
		self.errors = np.array(errors)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Approximations": self.approximations,
			"Errors": self.errors
		})
# --------------------

# --------------------
# iterative techniques
class SingleVariableIteration:
	r"""Given :math:`f(x)` such that :math:`x \in [a, b]`, find the root of a single-variable, equation within tolerance.

	Parameters
	----------
	function : lambda
		Input function.
	a, b : float
		Left and right-hand bound of interval, respectively.
	power : float, optional
		Signed, specified power of tolerance until satisfying method.
	variable : string, optional
		Respected variable in derivative. Assumed to be 'x' if not stated.
	iter_guess : bool or integer, optional
		Boolean value of `True` by default. If integer, iterate for that integer.
	function_slope : float, optional
		Absolute maximum slope of function.

	Attributes
	----------
	function : expression
		Input function.
	variable : string, optional
		Respected variable in derivative. Assumed to be `'x'` if not stated.
	a, b : float
		Left and right-hand bound of interval, respectively.
	tol : float
		Tolerance to satisfy method.
	iter_guess : bool or integer
		Boolean value of `True` by default. If integer, iterate for that integer.
	function_slope : float
		Absolute maximum slope of functon. Assumed 0 if not defined.

	Methods
	-------
	find_k()
		Find the greatest value for first derivative of function.
	max_iterations()
		Find maximum number of iterations for method if not provided.
	bisection()
		Search for solution by halving the bounds wherein `a` and `b` initially yield opposite signs in function.
	false_position(p0: float, p1: float)
		solution bounded by `a` and `b` wherein initial guesses `p0` and `p1` yield opposite signs in function.
	fixed_point(p0: float)
		Root-finding method to find solution near initial guess.
	newton_raphson(p0: float)
		Root-finding method to find solution near initial guess.
	secant_method(p0: float, p1: float)
		Initial guesses `p0` and `p1` must yield opposite signs in function. Solution is NOT bounded by `a` and `b`.

	Raises
	------
	TypeError
		If input function cannot be understood as lambda expression.

	Notes
	-----
	self.tol evaluated by: `10**power`.

	Convergence Rates:
		`newton_raphson` > `secant_method` > `false_position` > `fixed_point` > `bisection`
	"""

	def __init__(
		self,
		function: FunctionType,
		a: float,
		b: float,
		power: Optional[float]=-6,
		variable: Optional[str]="x",
		iter_guess: Optional[Union[bool,int]]=True,
		function_slope: Optional[float]=0
	):
		self.__function_name = function_name = _retrieve_name(function)
		# if isinstance(function, (str)):
		# 	function_str = ex.fast_parse_latex(function)
		# 	function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
		# 	#print("String expression converted to lambda function.")
		if isinstance(function, (FunctionType)):
			#funcString = str(inspect.getsourcelines(function)[0])
			#funcString = funcString.strip("['\\n']").split(" = ")[1]
			#sym_function_idx = funcString.find(": ")+2
			#sym_function = funcString[sym_function_idx:]
			function_str = "Lambda"
		else: raise TypeError(SingleVariableIteration.__TypeError_Lambda(function_name))
		self.function, self.function_str, self.variable = function, function_str, variable
		self.a, self.b, self.tol = float(a), float(b), float(10**power)
		self.iter_guess, self.function_slope = iter_guess, function_slope

	# __TypeError_String = lambda function_name: f"ERROR! '{function_name}' must be a LaTeX formatted equation of type string."
	__TypeError_Lambda = lambda function_name: f"The input function, '{function_name}' must be a lambda expression."
	__MaxIterError = lambda N: f"Maximum iterations, N = {N} must be an integer greater than zero."
	__OppositeSignError_Interval = lambda function_name, f, a, b: f"Interval bounds must yield opposite signs in function, '{function_name}':= [f(a={a}) = {f(a)}, f(b={b}) = {f(b)}]"
	__OppositeSignError_Guess = lambda function_name, f, p0, p1: f"Interval bounds must yield opposite signs in function, '{function_name}':= [f(p0={p0}) = {f(p0)}, f(p1={p1}) = {f(p1)}]"

	def find_k(self) -> float:
		r"""Find greatest integer for maximum iterations for tolerance.

		Returns
		-------
		k : float
			Maximum possible slope of input function.

		Attributes
		----------
		self.function_slope : float
			Maximum possible slope of input function.
		"""
		k = self.function_slope
		# determine form of derivative
		# if self.function_str != "Lambda":
		# 	df = lambda x: ex.fast_eval_latex(ex.fast_derive_latex(self.function_str, self.variable), {self.variable: x})
		# else:
		df = sp.lambdify(sp.Symbol(self.variable), sp.diff(self.function(sp.Symbol(self.variable))))
		for alpha in np.linspace(self.a, self.b, int(1e3)):
			if abs(df(alpha)) > k: k = abs(df(alpha))
		self.function_slope = k
		return k

	def max_iterations(self, method: str, p0: Optional[float]=0) -> int:
		r"""Find greatest integer for maximum iterations within tolerance.

		Parameters
		----------
		method : {"bisection", "fixed_point", "newton_raphson", "secant_method", "false_position"}
			Selection of iterative method for iterations are needed.
		p0 : float, optional
			Initial guess for function solution. Not needed for `"bisection"` method.

		Returns
		-------
		max_iter : int
			Maximum number of iterations required for specified tolerance.

		Attributes
		----------
		max_iter : int
			Maximum number of iterations required for specified tolerance.

		Raises
		------
		ValueError
			Prescribed method is not an available option.

		Warnings
		--------
		Will round away from zero to higher integers.

		Notes
		-----
		Informs user in logfile the maximum number of iterations for method.

		Examples
		--------
		If `method == "bisection"` & `a`=1, `b`=2, and `power`=-3, then:

		.. math::
			N &\geq -\log(`tol`/(`b` - `a`))/\log(2) \\
			 &\geq -\log((10^{-3}/(2 - 1))/\log(2) \\
			 &\geq 9.96 \\
			\implies N = 10

		Else, if `a`=1, `b`=2, `power`=-3, `p0`=1.5, nd `k`=0.9, then:

		.. math::
			N &\geq \log(`tol`/max('p0' - `a`, `b` - `p0`))/log(`k`) \\
			 &\geq \log(10^{-3}/max(1.5 - 1, 2 - 1.5))/\log(0.9) \\
			 &\geq \log(10^{-3}/0.5)/\log(0.9) \\
			 &\geq 58.98 \\
			\implies N >= 59
		"""
		a, b, k = self.a, self.b, self.function_slope
		p0 = float(p0)
		if method == "bisection":
			self.max_iter = max_iter = math.ceil(-math.log(self.tol/(b - a))/math.log(2))
		elif method in ("fixed_point", "newton_raphson", "secant_method", "false_position"):
			self.max_iter = max_iter = math.ceil(-math.log(self.tol/max(p0 - a, b - p0))/math.log(k))
		else: raise ValueError(f"I am sorry. The desired method must be: 'bisection', 'fixed_point', 'newton_raphson', 'secant_method', or 'false_position'.")
		logging.info(f"With the inputs, I will terminate the technique after so many iterations, N = {max_iter}")
		return self.max_iter

	# next 5 functions preceded by find_k & max_iterations

	def bisection(self) -> pd.DataFrame:
		r"""Root-finding method: :math:`f(x) = 0` [1]_.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, evaluated points, `p` and propogated errors through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer greater than zero.
		ValueError
			If bounds did not evaluate to have opposite signs from function.
		TypeError
			If input function cannot be understood as lambda expression.

		Warnings
		--------
		Writes to logfile if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Notes
		-----
		Relying on the Intermediate Value Theorem (IVT), this is a bracketed, root-finding method. Generates a sequence :math:`{p_{n}}_{n=1}^{\infty}` such :math:`f(x=p_{n}) = 0` and converges by :math:`\mathcal{O}(1 / (2^{N}))` [1]_.
		This method is rather slow to converge but will always converge to a solution; therefore, is a good starter method.

		Examples
		--------
		If  f(x) = x**3 + 4*x**2 = 10

		=>  f(x) = x**3 + 4*x**2 - 10 = 0
		"""
		f, a, b = self.function, self.a, self.b
		# calculate if expression
		if isinstance(f, (FunctionType)):
			# check if f(a) and f(b) are opposite signs
			if f(a)*f(b) < 0:
				if self.iter_guess == True: # if left unassigned, guess
					N = self.max_iterations("bisection")
				elif isinstance(self.iter_guess, (int, float)): # if defined, use
					N = int(self.iter_guess)
				# else, break for bad assignment
				else: raise ValueError(SingleVariableIteration.__MaxIterError(self.iter_guess))
				k, approximations, errors = 1, [f(a)], [1] # initialize
				# exit by whichever condition is TRUE first
				while errors[-1] >= self.tol and k <= N:
					x = (b - a)/2
					p = a + x 				# new value, p
					approximations.append(p)
					if f(a)*f(p) > 0: a = p	# adjust next bounds
					else: b = p
					errors.append(abs(x))	# error of new value, p
					k += 1 	# iterate to k + 1
				if k <= N: logging.info("Congratulations! Solution found!")
				else: logging.warning("Solution could not be found with initial guess or tolerance.")
				self.iterations = np.arange(k)
				self.approximations = np.array(approximations)
				self.errors = np.array(errors)
				return pd.DataFrame(data={
					"Iterations": self.iterations,
					"Approximations": self.approximations,
					"Errors": self.errors
				})
			# abort if f(a) is not opposite f(b)
			else: raise ValueError(SingleVariableIteration.__OppositeSignError_Interval(self.__function_name, f, a, b))
		# abort if not expression
		else: raise TypeError(SingleVariableIteration.__TypeError_Lambda(self.__function_name))

	def false_position(self, p0: float, p1: float) -> pd.DataFrame:
		r"""Attempt method with initial guesses, `p0` and `p1` in [`a`, `b`].

		Is root-finding method by solving the equation :math:`g(p) = p` via :math:`f(p) - p = 0`.

		!!! Use function with lowest slope !!!

		Parameters
		----------
		p0, p1 : float
			Initial guesses.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, evaluated points, `p` and propogated errors through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer greater than zero.
		ValueError
			If initial guesses did not evaluate to have opposite signs from function.
		TypeError
			If input function cannot be understood as lambda expression.

		Warnings
		--------
		Writes to logfile if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Notes
		-----
		Similar to `secant_method` but includes a test to ensure solution is root-bracketed and is therefore slower to converge than the `secant_method`.

		Check that :math:`|g'(x)| \leq (\text{leading coefficient of g'(x)})` for all :math:`x \in [a, b]`.

		Theorem:
		1) Existence of a fixed-point:
			If :math:`g \in C[a,b]` and :math:`g(x) \in C[a, b]` for all :math:`x \in [a, b]`, then function, :math:`g` has a fixed point, :math:`p \in [a, b]`.

		2) Uniqueness of a fixed point:
			If :math:`g'(x)` exists on :math:`[a, b]` and a positive constant, `k` < 1 exist with :math:`\{|g'(x)| \leq k | x \in (a, b)\}`, then there is exactly one fixed-point, :math:`p \in [a, b]`.

		Converges by :math:`\mathcal{O}(\text{linear})` if :math:`g'(p) \neq 0`, and :math:`\mathcal{O}(\text{quadratic})` if :math:`g'(p) = 0` and :math:`g''(p) < M`, where :math:`M = g''(\xi)` that is the error function.

		Examples 
		--------
		If  g(x) = x**2 - 2

		Then	p = g(p) = p**2 - 2

		=>  p**2 - p - 2 = 0
		"""
		f, a, b = self.function, self.a, self.b
		self.p0, self.p1 = p0, p1 = float(p0), float(p1)
		# calculate if expression
		if isinstance(f, (FunctionType)):
			# check if f(p0) and f(p1) are opposites signs
			if f(p0)*f(p1) < 0:
				if self.iter_guess == True: # if left unassigned, guess
					if self.function_slope == 0: self.find_k()
					N = self.max_iterations("false_position", p0=p0)
				elif isinstance(self.iter_guess, (int, float)): # if defined, use
					N = int(self.iter_guess)
				# else, break for bad assignment
				else: raise ValueError(SingleVariableIteration.__MaxIterError(self.iter_guess))
				k, approximations, errors = 1, [f(a)], [1] # initialize
				# exit by whichever condition is TRUE first
				while errors[-1] >= self.tol and k <= N:
					q0, q1 = f(p0), f(p1)
					p = p1 - q1*(p1 - p0)/(q1 - q0) # new value, p
					approximations.append(p)
					errors.append(abs(p - p0))		# error of new value, p
					if f(p)*q1 < 0: p0 = p1			# adjust next bounds
					p1 = p; k += 1 					# iterate to k + 1
				if k <= N: logging.info("Congratulations! Solution found!")
				else: logging.warning("Solution could not be found with initial guess or tolerance.")
				self.iterations = np.arange(k)
				self.approximations = np.array(approximations)
				self.errors = np.array(errors)
				return pd.DataFrame(data={
					"Iterations": self.iterations,
					"Approximations": self.approximations,
					"Errors": self.errors
				})
			# abort if f(p0) is not opposite f(p1)
			else: raise ValueError(SingleVariableIteration.__OppositeSignError_Guess(self.__function_name, f, p0, p1))
		# abort if not expression
		else: raise TypeError(SingleVariableIteration.__TypeError_Lambda(self.__function_name))

	def fixed_point(self, p0: float) -> pd.DataFrame:
		r"""Attempt method with initial guess, `p0` in [`a`, `b`].

		Is root-finding method by solving the equation :math:`g(p) = p` via :math:`f(p) - p = 0`.

		!!! Use function with lowest slope !!!

		Parameters
		----------
		p0 : float
			Initial guess.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, evaluated points, `p` and propogated errors through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer greater than zero.

		TypeError
			If input function cannot be understood as lambda expression.

		Warnings
		--------
		Writes to logfile if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Notes
		-----
		Not root-bracketed!

		Check that :math:`|g'(x)| \leq (\text{leading coefficient of g'(x)})` for all :math:`x \in [a, b]`.

		Theorem:
		1) Existence of a fixed-point:
			If :math:`g \in C[a,b]` and :math:`g(x) \in C[a, b]` for all :math:`x \in [a, b]`, then function, :math:`g` has a fixed point, :math:`p \in [a, b]`.

		2) Uniqueness of a fixed point:
			If :math:`g'(x)` exists on :math:`[a, b]` and a positive constant, `k` < 1 exist with :math:`\{|g'(x)| \leq k | x \in (a, b)\}`, then there is exactly one fixed-point, :math:`p \in [a, b]`.

		Converges by :math:`\mathcal{O}(\text{linear})` if :math:`g'(p) \neq 0`, and :math:`\mathcal{O}(\text{quadratic})` if :math:`g'(p) = 0` and :math:`g''(p) < M`, where :math:`M = g''(\xi)` that is the error function.

		Examples 
		--------
		If  g(x) = x**2 - 2

		Then	p = g(p) = p**2 - 2
		
		=>  p**2 - p - 2 = 0
		"""
		f, a, b = self.function, self.a, self.b
		self.p0 = p0 = float(p0)
		# calculate if expression
		if isinstance(f, (FunctionType)):
			if self.iter_guess == True: # if left unassigned, guess
				if self.function_slope == 0: self.find_k()
				N = self.max_iterations("fixed_point", p0=p0)
			elif isinstance(self.iter_guess, (int, float)): # if defined, use
				N = int(self.iter_guess)
			# else, break for bad assignment
			else: raise ValueError(SingleVariableIteration.__MaxIterError(self.iter_guess))
			k, approximations, errors = 1, [f((a+b)/2)], [1] # initialize
			# exit by whichever condition is TRUE first
			while errors[-1] >= self.tol and k <= N:
				p = f(p0)		# new value, p
				approximations.append(p)
				errors.append(abs((p - p0)/p0))	# error of new value, p
				p0 = p; k += 1 	# iterate to k + 1
			if k <= N: logging.info("Congratulations! Solution found!")
			else: logging.warning("Solution could not be found with initial guess or tolerance.")
			self.iterations = np.arange(k)
			self.approximations = np.array(approximations)
			self.errors = np.array(errors)
			return pd.DataFrame(data={
				"Iterations": self.iterations,
				"Approximations": self.approximations,
				"Errors": self.errors
			})
		# abort if not expression
		else: raise TypeError(SingleVariableIteration.__TypeError_Lambda(self.__function_name))

	def newton_raphson(self, p0: float) -> pd.DataFrame:
		r"""Attempt method with initial guess, p0 in [a, b].

		Is root-finding method by solving the equation :math:`g(p) = p` via :math:`f(p) - p = 0`.

		!!! Use function with lowest slope !!!

		Parameters
		----------
		p0 : float
			Initial guess.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, evaluated points, `p` and propogated errors through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer greater than zero.
		TypeError
			If input function cannot be understood as lambda expression.

		Warnings
		--------
		Write to logfile if solution was found, or state that solution did not converge with given guess or prescribed tolerance.

		Not root-bracketed and has trouble with symmetric functions!

		:math:`f'(x) \neq 0`


		Notes
		-----
		Initial guess, `p0` must be close to real solution; else, will converge to different root or oscillate (if symmetric).

		Newton-Raphson has quickest convergence rate.

		This method can be viewed as fixed-point iteration.

		Check that :math:`|g'(x)| \leq (\text{leading coefficient of g'(x)})` for all :math:`x \in [a, b]`.

		Technique based on first Taylor polynomial expansion of :math:`f` about :math:`p_{0}` (that is `p0`) and evaluated at :math:`x = p`. :math:`|p - p_{0}|` is assumed small; therefore, :math:`2^{\text{nd}}`-order Taylor term, the error, is small.

		Theorem:
		1) Existence of a fixed-point:
			If :math:`g \in C[a,b]` and :math:`g(x) \in C[a, b]` for all :math:`x \in [a, b]`, then function, :math:`g` has a fixed point, :math:`p \in [a, b]`.

		2) Uniqueness of a fixed point:
			If :math:`g'(x)` exists on :math:`[a, b]` and a positive constant, `k` < 1 exist with :math:`\{|g'(x)| \leq k | x \in (a, b)\}`, then there is exactly one fixed-point, :math:`p \in [a, b]`.

		Converges by :math:`\mathcal{O}(\text{linear})` if :math:`g'(p) \neq 0`, and :math:`\mathcal{O}(\text{quadratic})` if :math:`g'(p) = 0` and :math:`g''(p) < M`, where :math:`M = g''(\xi)` that is the error function.

		Examples 
		--------
		If  g(x) = x**2 - 2

		Then	p = g(p) = p**2 - 2

		=>  p**2 - p - 2 = 0
		"""
		f, a, b = self.function, self.a, self.b
		self.p0 = p0 = float(p0)
		# calculate if expression
		if isinstance(f, (FunctionType)):
			# determine form of derivative
			# if self.function_str != "Lambda":
			# 	df_str = ex.fast_derive_latex(self.function_str, self.variable)
			# 	df = lambda x: ex.fast_eval_latex(df_str, {self.variable: x})
			# else: df = sp.lambdify(sp.Symbol(self.variable), sp.diff(self.function(sp.Symbol(self.variable))))
			df = sp.lambdify(sp.Symbol(self.variable), sp.diff(self.function(sp.Symbol(self.variable))))
			if self.iter_guess == True: # if left unassigned, guess
				if self.function_slope == 0: self.find_k()
				N = self.max_iterations("newton_raphson", p0=p0)
			elif isinstance(self.iter_guess, (int, float)): # if defined, use
				N = int(self.iter_guess)
			# else, break for bad assignment
			else: raise ValueError(SingleVariableIteration.__MaxIterError(self.iter_guess))
			k, approximations, errors = 1, [f(a)], [1] # initialize
			# exit by whichever condition is TRUE first
			while errors[-1] >= self.tol and k <= N:
				fp0 = f(p0)
				dfp0 = df(p0)
				p = p0 - (fp0/dfp0)			# new value, p
				approximations.append(p)
				errors.append(abs(p - p0)) 	# error of new value, p
				p0 = p; k += 1				# iterate to k + 1
			if k <= N: logging.info("Congratulations! Solution found!")
			else: logging.warning("Solution could not be found with initial guess or tolerance.")
			self.iterations = np.arange(k)
			self.approximations = np.array(approximations)
			self.errors = np.array(errors)
			return pd.DataFrame(data={
				"Iterations": self.iterations,
				"Approximations": self.approximations,
				"Errors": self.errors
			})
		# abort if not expression
		else: raise TypeError(SingleVariableIteration.__TypeError_Lambda(self.__function_name))

	def secant_method(self, p0: float, p1: float) -> pd.DataFrame:
		r"""Attempt method with initial guesses, `p0` and `p1` in [`a`, `b`].
		
		Is root-finding method by solving the equation :math:`g(p) = p` via :math:`f(p) - p = 0`.

		!!! Use function with lowest slope !!!

		Parameters
		----------
		p0, p1 : float
			Initial guesses.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, evaluated points, `p` and propogated errors through method.

		Raises
		------
		ValueError
			If input for desired iterations was assigned not an integer greater than zero.
		ValueError
			If initial guesses did not evaluate to have opposite signs from function.
		TypeError
			If input function cannot be understood as lambda expression.

		Warnings
		--------
		Write to logfile if solution was found, or state that solution did not converge with given guess or prescribed tolerance.


		Notes
		-----
		Not root-bracketed.

		Method is less computationally expensive than `newton_raphson` may converge at lower rate by circumventing need to calculate derivative.

		Check that :math:`|g'(x)| \leq (\text{leading coefficient of g'(x)})` for all :math:`x \in [a, b]`.

		Theorem:
		1) Existence of a fixed-point:
			If :math:`g \in C[a,b]` and :math:`g(x) \in C[a, b]` for all :math:`x \in [a, b]`, then function, :math:`g` has a fixed point, :math:`p \in [a, b]`.

		2) Uniqueness of a fixed point:
			If :math:`g'(x)` exists on :math:`[a, b]` and a positive constant, `k` < 1 exist with :math:`\{|g'(x)| \leq k | x \in (a, b)\}`, then there is exactly one fixed-point, :math:`p \in [a, b]`.

		Converges by :math:`\mathcal{O}(\text{linear})` if :math:`g'(p) \neq 0`, and :math:`\mathcal{O}(\text{quadratic})` if :math:`g'(p) = 0` and :math:`g''(p) < M`, where :math:`M = g''(\xi)` that is the error function.

		Examples 
		--------
		If  g(x) = x**2 - 2

		Then	p = g(p) = p**2 - 2

		=>  p**2 - p - 2 = 0
		"""
		f, a, b = self.function, self.a, self.b
		self.p0, self.p1 = p0, p1 = float(p0), float(p1)
		# calculate if expression
		if isinstance(f, (FunctionType)):
			# check if f(p0) and f(p1) are opposite signs
			if f(p0)*f(p1) < 0:
				if self.iter_guess == True: # if left unassigned, guess
					if self.function_slope == 0: self.find_k()
					N = self.max_iterations("secant_method", p0=p0)
				elif isinstance(self.iter_guess, (int, float)): # if defined, use
					N = int(self.iter_guess)
				# else, break for bad assignment
				else: raise ValueError(SingleVariableIteration.__MaxIterError(self.iter_guess))
				k, approximations, errors = 1, [f(a)], [1] # initialize
				# exit by whichever condition is TRUE first
				while errors[-1] >= self.tol and k <= N:
					q0, q1 = f(p0), f(p1)
					p = p1 - q1*(p1 - p0)/(q1 - q0)	# new value, p
					approximations.append(p)
					errors.append(abs(p - p0))		# error of new value
					p0, p1 = p1, p; k += 1 			# iterate to k + 1
				if k <= N: logging.info("Congratulations! Solution found!")
				else: logging.warning("Solution could not be found with initial guess or tolerance.")
				self.iterations = np.arange(k)
				self.approximations = np.array(approximations)
				self.errors = np.array(errors)
				return pd.DataFrame(data={
					"Iterations": self.iterations,
					"Approximations": self.approximations,
					"Errors": self.errors
				})
			# abort if f(p0) is not opposite f(p1)
			else: raise ValueError(SingleVariableIteration.__OppositeSignError_Guess(self.__function_name, f, p0, p1))
		# abort if not expression
		else: raise TypeError(SingleVariableIteration.__TypeError_Lambda(self.__function_name))

class MultiVariableIteration:
	r"""Iteratively find the solution to a system of equations (SOE): :math:`\mathbf{A}\vec{x} = \vec{b}`. Ideal for large, sparse systems.

	Parameters
	----------
	A : tuple
		Either one-dimensional vector of input functions or matrix of characteristic values.
	x : tuple
		Either one-dimensional vector of variables or initial guesses for SOE.
	b : tuple
		Solution vector.
	power : float, optional
		Signed, specified power of tolerance until satisfying method.
	max_iter : int, optional
		Number of iterations.
	norm_type : {'l_infinity', 'l_two'}, optional
		String representation of desired norm function. `'l_infinity'` by default.

	Attributes
	----------
	A : np.ndarray
		Either one-dimensional vector of input functions or matrix of characteristic values.
	x : np.ndarray
		Either one-dimensional vector of variables or initial guesses for SOE.
	b : np.ndarray
		Solution vector.
	tol : float
		Specified tolerance to which method terminates.
	max_iter : int
		Maximum iterations allowed for method.
	norm_type : string
		String representation of desired norm function.
	is_diagonal, is_symmetric, is_tridiagonal : bool
		Truth value of whether matrix is diagonal, symmetric, and tridiagonal, respectively if not lambda expressions.
	eigen_values : np.ndarray
		Eigenvalues of characteristic matrix, `A` if not lambda expressions.
	spectral_radius, condition_number : float
		Spectral radius and condition number of characteristic matrix, `A`, respectively if not lambda expressions.

	Methods
	-------
	find_omega(omega=0)
		Suggests optimum :math:`\omega` over input.
	gauss_seidel()
		Improves on `jacobi()` for faster solution.
	jacobi()
		Iteratively find solution until within tolerance.
	newton_raphson(variables: Tuple[str])
		Given one-dimensional array of equations respect input variables to build gradient (Jacobian) matrix.
	successive_relaxation(omega=None)
		Adjusts solution rate of `gauss_seidel()` by scalar :math:`\omega` which is `None` by default to find the most optimum.

	Raises
	------
	TypeError
		Not all elements in matrix of interest (if one-dimensional) are lambda expressions.
	IndexError
		Matrix of interest must be square.
	IndexError
		If `x` is not a one-dimensional array.
	IndexError
		If `b` is not a one-dimensional array.
	ValueError
		If iterations constraint is not an integer greater than zero.
	ValueError
		If desired norm method was neither `'l_infinity'` nor `'l_two'`.

	See Also
	--------
	diagonality : Determines if matrix, `A` is strictly, diagonally dominant.
	symmetry : Dtermines if matrix, `A` is symmetric.
	tridiagonality : Determines if matrix, `A` is tridiagonal.
	EigenValues.qr_algorithm : Function to find eigenvalues of matrix, A given initial vector, x and solution vector, b..
	spectral_radius : Function to find the spectral radius of characteristic matrix, A.
	condition_number : Finds the condition number of matrix, A.
	SystemOfEquations : Alternative techniques to solve smaller SOE.

	Notes
	-----
	Specified tolerance evaluated by: `10**power`.

	`norm_type` may be either `'l_infinity'` or `'l_two'`. Is 'l_infinity' by default.
	"""

	def __init__(
		self,
		A: tuple,
		x: tuple,
		b: tuple,
		power: Optional[float]=-6,
		max_iter: Optional[int]=100,
		norm_type: Optional[str]="l_infinity"
	):
		A, x, b = np.array(A), np.array(x), np.array(b)
		self.__matrix_name = _retrieve_name(A)
		self.__vector_name = _retrieve_name(x)
		self.__solution_name = _retrieve_name(b)
		BadMatrixError = lambda matrix_name: f"Matrix, '{matrix_name}' must be square matrix of floats or one-dimensional array of lambda expressions!"
		BadVectorError = lambda vector_name: f"Systems vector, '{vector_name}' must be one-dimensional array!"
		BadSystemError = f"System of equations are not all same length!"
		BadMaxIterError = lambda N: f"Maximum iterations, N = {N} must be an integer greater than zero."
		BadNormTypeError = lambda norm_type: f"Desired norm type, '{norm_type}' was not understood. Please choose 'l_infinity' or 'l_two'."
		if np.ndim(A) == 1:
			for a in A:
				if not isinstance(a, FunctionType):
					raise TypeError(BadMatrixError(self.__matrix_name))
		else:
			if np.sum(np.array(A).shape[0]) != np.array(A).shape[1]: raise IndexError(BadMatrixError(self.__matrix_name))
			self.is_diagonal = diagonality(A)
			self.is_symmetric = symmetry(A)
			self.is_tridiagonal = tridiagonality(A)
			self.eigen_values = EigenValues(A, power=power).qr_algorithm()["Lambdas"].values[-1]
			self.spectral_radius = spectral_radius(A)
			self.condition_number = condition_number(A, norm_type)
		if np.sum(np.array(x).shape) - np.array(x).shape[0] > 1: raise IndexError(BadVectorError(self.__vector_name))
		if np.sum(np.array(b).shape) - np.array(b).shape[0] > 1: raise IndexError(BadVectorError(self.__solution_name))
		if len(A) != len(x) or len(A) != len(b) or len(x) != len(b): raise IndexError(BadSystemError)
		if max_iter <= 0 or not isinstance(max_iter, (int, float)): ValueError(BadMaxIterError(max_iter))
		if norm_type != "l_infinity" and norm_type != "l_two": raise ValueError(BadNormTypeError(norm_type))
		self.A = np.array(A)
		self.x = np.array(x)
		self.b = np.array(b)
		self.tol = float(10**power)
		self.max_iter = int(max_iter)
		self.norm_type = norm_type

	__NoSolutionWarning = lambda N, tol: f"Solution could not be found from initial guess within {N} iterations or tolerance, {tol}."
	__SolutionInformation = "Congratulations! Solution found!"

	def __find_xk(self, x: np.ndarray) -> np.ndarray:
		return np.matmul(self.T, x) + self.c

	def find_omega(self, omega: Optional[float]=0) -> float:
		r"""Given the characteristic matrix and solution vector, determine if prescribed `omega` is the optimum choice. Will find optimum if not prescribed and possible

		Parameters
		----------
		omega : float, optional
			Relaxation parameter.

		Returns
		-------
		omega : float
			The :math:`\omega` used for Successive Relaxation method.

		Attributes
		----------
		user_omega : float
			Supplied/default omega.
		is_positive_definite : bool
			Whether or not matrix, `A` is positive definite.
		best_omega : float
			If found, is the optimum choice of omega.

		Warnings
		--------
		If 0 < `omega` < 2, then method will converge regardless of choice for `x`.
		
		If an optimal omega cannot be found, then `self.best_omega` assigned from supplied/default omega.
		
		Will write to logfile that matrix, `A` is not tridiagonal, but will proceed with calculation all the same.
		
		If matrix, `A` is poorly defined and not found to be positive definite, then this is written to logfile but calculation proceeds.
		

		See Also
		--------
		tridiagonality : Determines if matrix, `A` is tridiagonal or not.
		spectral_radius : Uses the spectral radius of Gauss-Seidel's T-matrix to calculate :math:`\omega`.

		Notes
		-----
		Unless specified and changed from the default, `omega=0` :math:`\omega` will be chosen if possible.
		"""
		self.user_omega = omega
		xn, xt = np.reshape(self.x, (len(self.x), 1)), self.x
		y = np.matmul(np.matmul(xt, self.A), xn)
		if self.is_symmetric and y[0] > 0: theorem_6_22 = True
		else: theorem_6_22 = False
		i, theorem_6_25 = 1, True
		while i <= len(self.A) and theorem_6_25 == True:
			# Ai = self.A[:i,:i]
			# if ex.fast_determinant(Ai) > 0: theorem_6_25 = True
			Ai = sp.Matrix(self.A[:i,:i])
			if sp.det(Ai) > 0: theorem_6_25 = True
			else : theorem_6_25 = False
			i += 1
		if theorem_6_22 or theorem_6_25:
			self.is_positive_definite = True
			if 0 < omega and omega < 2:
				logging.info("According to Ostrowski-Reich's Theorem, the successive relaxation technique will converge.")
			if self.is_tridiagonal:
				D = np.diagflat(np.diag(self.A))
				L = np.diagflat(np.diag(self.A, k=-1), k=-1)
				U = np.diagflat(np.diag(self.A, k=1), k=1)
				DL, DL_inv = D - L, np.zeros_like(D - L)
				for i in range(len(DL_inv)):
					for j in range(len(DL_inv[0])):
						if DL[i][j] != 0: DL_inv[i][j] = 1/(DL[i][j])
				Tg = DL_inv*U
				omega = 2 / (1 + math.sqrt(1 - spectral_radius(Tg)))
				logging.info(f"I believe {omega} would be the best choice.")
			else:
				logging.warning(f"Matrix, '{self.__matrix_name}' is not tridiagonal.")
				logging.info(f"Assigning supplied omega, {omega} as `best_omega`.")
		else:
			self.is_positive_definite = False
			logging.warning(f"Matrix, '{self.__matrix_name}' is not positive definite.")
			logging.info(f"Assigning supplied omega, {omega} as `best_omega`.")
		self.best_omega = omega
		return omega

	def gauss_seidel(self) -> pd.DataFrame:
		r"""Given :math:`\mathbf{A}\vec{x} = \vec{b}`, use `norm_type` to find :math:`\vec{x}` via the Gauss-Seidel Method.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, approximations, and normative errors through method.

		Warnings
		--------
		Writes to logfile whether or not a solution was found within the specified tolerance with the supplied, initial guess.

		See Also
		--------
		Norm.l_infinity : Will find :math:`||x_{i} - x_{0}||_{\infty}`
		Norm.l_two : Will find :math:`||x_{i} - x_{0}||_{2}`

		Notes
		-----
		This improves on `jacobi` by using the most recently calculated entries in the approximation vector, `x` after each iteration.

		The primary algorithm by which method marches approximation vector, `x`

		.. math::
			\vec{x}^{(k)} = \bigl( (\mathbf{D} - \mathbf{L})^{-1} * \mathbf{U} \bigr) \cdot \vec{x}^{(k - 1)} + \bigl( (\mathbf{D} - \mathbf{L})^{-1} \bigr) \cdot \vec{b}
		"""
		x = self.x
		# A = np.zeros((N, N))
		# np.fill_diagonal(A, ai)
		# A = A + np.diagflat(bi, 1)
		# A = A + np.diagflat(ci, -1)
		# x0 = np.zeros(N)
		# b = np.array(di)
		# A1, A2 = np.zeros((n, n)), np.zeros((n, n))
		# np.fill_diagonal(A1, np.diagonal(A))
		# A1 = A1 - np.tril(A, k=-1)
		# i = 0
		# while i < n:
		# 	j = 0
		# 	while j <= i:
		# 		a1ij = A1[i][j]
		# 		if a1ij != 0:
		# 			A2[i][j] = 1/a1ij
		# 		j += 1
		# 	i += 1
		# self.T = np.matmul(A2, np.triu(A, k=1))
		# self.c = np.matmul(A2, b)
		k, n, approximations, errors = 1, len(x), [x], [self.tol*10]
		while errors[-1] > self.tol and k <= self.max_iter:
			xi = np.zeros_like(x)
			for i in range(n):
				y1 = y2 = 0
				for j in range(i): y1 += float(self.A[i][j]*xi[j])
				for j in range(i+1, n): y2 += float(self.A[i][j]*x[j])
				xi[i] = float((-y1 - y2 + self.b[i])/self.A[i][i])
			# xi = self.__find_xk(x0)
			if self.norm_type == "l_infinity":
				norm = Norm(xi, x).l_infinity()
			elif self.norm_type == "l_two":
				norm = Norm(xi, x).l_two()
			approximations.append(xi)
			errors.append(norm)
			x = xi; k += 1 # iterate to k + 1
		if k <= self.max_iter: logging.info(MultiVariableIteration.__SolutionInformation)
		else: logging.warning(MultiVariableIteration.__NoSolutionWarning(self.max_iter, self.tol))
		self.iterations = np.arange(k)
		self.approximations = approximations
		self.errors = np.array(errors)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Approximations": self.approximations,
			"Errors": self.errors
		})

	def jacobi(self) -> pd.DataFrame:
		r"""Given :math:`\mathbf{A}\vec{x} = \vec{b}`, use `norm_type` to find :math:`\vec{x}` via the Jacobi Method.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, approximations, and normative errors through method.

		Warnings
		--------
		Writes to logfile whether or not a solution was found within the specified tolerance with the supplied, initial guess.

		See Also
		--------
		Norm.l_infinity : Will find :math:`||x_{i} - x_{0}||_{\infty}`
		Norm.l_two : Will find :math:`||x_{i} - x_{0}||_{2}`

		Notes
		-----
		The primary algorithm by which method marches approximation vector, `x`

		.. math::
			\vec{x}^{(k)} = \bigl( \mathbf{D}^{-1} * (\mathbf{L} + \mathbf{U}) \bigr) \cdot \vec{x}^{(k - 1)} + ( \mathbf{D}^{-1} ) \cdot \vec{b}
		"""
		x = self.x
		k, n, approximations, errors = 1, len(x), [x], [self.tol*10]
		while errors[-1] > self.tol and k <= self.max_iter:
			xi = np.zeros_like(x)
			for i in range(n):
				y = 0
				for j in range(n):
					if j != i: y += float(self.A[i][j]*x[j])
				xi[i] = float((-y + self.b[i])/self.A[i][i])
			if self.norm_type == "l_infinity":
				norm = Norm(xi, x).l_infinity()
			elif self.norm_type == "l_two":
				norm = Norm(xi, x).l_two()
			approximations.append(xi)
			errors.append(norm)
			x = xi; k += 1 # iterate to k + 1
		if k <= self.max_iter: logging.info(MultiVariableIteration.__SolutionInformation)
		else: logging.warning(MultiVariableIteration.__NoSolutionWarning(self.max_iter, self.tol))
		self.iterations = np.arange(k)
		self.approximations = approximations
		self.errors = np.array(errors)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Approximations": self.approximations,
			"Errors": self.errors
		})

	def newton_raphson(self, variables: Tuple[str]) -> pd.DataFrame:
		r"""Employ the Newton-Raphson Method to find solution of non-linear systems of equations within tolerance.

		Parameters
		----------
		variables : tuple
			Collection of string representations for variables to respect in derivations.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, approximations, and normative errors through method.

		Raises
		------
		TypeError
			If an element of `variables` is not of type string.

		Notes
		-----
		Modified form of `MultiVariableIteration` to analyze a one-dimensional array of non-linear SOE. Each element should be a lambda expression wherein each variable is represented.

		Examples 
		--------
		>>> A = [lambda x1, x2, x3: 3*x1 - sympy.cos(x2*x3) - 1/2,
			lambda x1, x2, x3: x1**2 - 81*(x2 + 0.1)**2
				+ sympy.sin(x3) + 1.06,
			lambda x1, x2, x3: sympy.exp(-x1*x2)
				+ 20*x3 + (10*math.pi - 3)/3
			]
		>>> x, b = (0.1, 0.1, -0.1), (0, 0, 0)
		>>> variables = ("x1", "x2", "x3")
		>>> MultiVariableIteration(A, x, b).newton_raphson(variables)["Approximations"].values[-1]
		[0.5, 0., -0.52359877]
		"""
		def jacobian_form(g):
			n = len(g)
			jacMatrix = np.zeros((n, n), dtype=FunctionType)
			for i in range(n):
				for j in range(n):
					jacMatrix[i][j] = sp.lambdify(variables, sp.diff(g[i], variables[j]))
			return jacMatrix
		functions, f, x, b = [], [], self.x, self.b
		for var in variables:
			if isinstance(var, str): continue
			else: raise TypeError(f"'{var}' must be of type string.")
		variables = [sp.symbols(var) for var in variables]
		k = 0
		for a in self.A:
			f.append(sp.lambdify(variables, a(*variables) - float(b[k])))
			functions.append(a(*variables) - float(b[k]))
			k += 1
		jacobian = jacobian_form(functions)
		k, n, approximations, errors = 1, len(x), [x], [self.tol*10]
		while errors[-1] >= self.tol and k <= self.max_iter:
			J = np.zeros_like(jacobian, dtype=float)
			for i in range(len(jacobian[0])):
				for j in range(len(jacobian)):
					J[i][j] = jacobian[i][j](*x)
			g = np.zeros_like(x)
			for i in range(n): 
				g[i] = f[i](*(x.reshape((1, n))[0]))
			# y0 = np.linalg.solve(J, -g)
			if positive_definite(J):
				y0 = SystemOfEquations(J, -g).conjugate_gradient(x)["Approximations"].values[-1]
			else:
				# y0 = SystemOfEquations(J, -g).steepest_descent(x)["Approximations"].values[-1]
				y0 = MultiVariableIteration(J, x, -g).gauss_seidel()["Approximations"].values[-1]
			xk = x + y0
			if self.norm_type == "l_two":
				norm = Norm(xk, x).l_two()
			elif self.norm_type == "l_infinity":
				norm = Norm(xk, x).l_infinity()
			errors.append(norm)
			approximations.append(xk.reshape((1, n))[0])
			x = xk; k += 1
		self.iterations = np.arange(k)
		self.approximations = approximations
		self.errors = np.array(errors)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Approximations": self.approximations,
			"Errors": self.errors
		})

	def successive_relaxation(self, omega: Optional[Union[None,float]]=None) -> pd.DataFrame:
		r"""Given :math:`\mathbf{A}\vec{x} = \vec{b}`, use `norm_type` to find :math:`\vec{x}` via the Successive Relaxation Method. Is Successive Over-Relaxation (SOR) if `omega` > 1, Successive Under-Relaxation (SUR) if `omega` < 1, and is Gauss-Seidel if `omega` = 1.

		Parameters
		----------
		omega : None or float, optional
			Relaxation parameter.

		Attributes
		----------
		iterations, approximations, errors : np.ndarray
			Collection of iterations, approximations, and normative errors through method.

		Returns
		-------
		pandas.DataFrame : DataFrame
			Summarized dataframe from iterations.

		Warnings
		--------
		Writes to logfile optimal choice of omega, regardless of assignment, and whether or not a solution was found within the specified tolerance with the supplied, initial guess.

		See Also
		--------
		find_omega : Will analyze SOE to find an optimal :math:`\omega`, if possible.
		gauss_seidel : Gauss-Seidel Method modified by omega.
		Norm.l_infinity : Will find :math:`||x_{i} - x_{0}||_{\infty}`
		Norm.l_two : Will find :math:`||x_{i} - x_{0}||_{2}`

		Notes
		-----
		SOR and SUR modify, respectively, on `gauss_seidel` by decreasing or increasing, respectively, the spectral radius of `A` to accelerate or deccelerate convergence, respectively.

		The primary algorithm by which method marches approximation vector, `x`

		.. math::
			\vec{x}^{(k)} = \bigl( (\mathbf{D} - \omega\mathbf{L})^{-1} * ((1 - \omega)*\mathbf{D} + \omega\mathbf{U}) \bigr) \cdot \vec{x}^{(k - 1)} + \omega( (\mathbf{D} - \omega\mathbf{L})^{-1} ) \cdot \vec{b}

		which is similar to `gauss_seidel`

		.. math::
			\vec{x}^{(k)} = \bigl( (\mathbf{D} - \mathbf{L})^{-1} * \mathbf{U} \bigr) \cdot \vec{x}^{(k - 1)} + \bigl( (\mathbf{D} - \mathbf{L})^{-1} \bigr) \cdot \vec{b}

		`omega` will be analyzed independent of assigned value which will be used if not specified in assignment and if possible.
		"""
		BadOmegaError = lambda omega: f"ERROR! Either a positive omega greater than zero was not given (w = {omega}), or I could not choose one."
		if omega == None:
			try: w = self.user_omega
			except AttributeError:
				try: w = self.best_omega
				except AttributeError:
					w = self.find_omega()
					logging.warning(f"Omega was not given; therefore, I attempted to choose one, {w}.")
				else: logging.info(f"Using `best_omega` = {w}.")
			else: logging.info(f"Using `user_omega` = {w}.")
			if w <= 0: raise ValueError(BadOmegaError(w))
		elif omega != None and isinstance(omega, (int, float)) and omega > 0:
			w = self.find_omega(omega=omega)
			logging.info(f"omega = {omega} given. Which is not optimum: {w}")
			w = omega
		else: raise ValueError(BadOmegaError(omega))
		x = self.x
		k, n, approximations, errors = 1, len(x), [x], [self.tol*10]
		while errors[-1] > self.tol and k <= self.max_iter:
			xi = np.zeros_like(x)
			xgs = self.gauss_seidel()["Approximations"].values[-1]
			for i in range(n):
				xi[i] = float((1 - w)*x[i] + w*xgs[i])
			if self.norm_type == "l_infinity":
				norm = Norm(xi, x).l_infinity()
			elif self.norm_type == "l_two":
				norm = Norm(xi, x).l_two()
			approximations.append(xi)
			errors.append(norm)
			x = xi; k += 1 # iterate to k + 1
		if k <= self.max_iter: logging.info(MultiVariableIteration.__SolutionInformation)
		else: logging.warning(MultiVariableIteration.__NoSolutionWarning(self.max_iter, self.tol))
		self.iterations = np.arange(k)
		self.approximations = approximations
		self.errors = np.array(errors)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Approximations": self.approximations,
			"Errors": self.errors
		})
# --------------------

# --------------------
# interpolations
class CubicSpline:
	r"""Given a domain and range, construct a piecewise-polynomial approximation (spline) within each interval by some condition.

	Parameters
	----------
	domain, function : tuple
		Input domain and range from which to build interpolating splines.
	variable : string
		Respected variable in derivative of equation. Assumed to be `"x"` if not stated.

	Attributes
	----------
	domain, function, mapped : np.ndarray
		Input domain, function, and mapped range.
	variable : string
		Variable to respect in derivation.

	Methods
	-------
	clamped(function_derivative: Optional[tuple])
		Use the derivative at the endpoints of the domain.
	natural()
		Assume the derivative at either end of domain is one.

	Raises
	------
	IndexError
		If `domain` is not a one-dimensional array.
	TypeError
		If `function` is not an expression or function and is not an one-dimensional array.
	IndexError
		If `domain` and `function` are of unequal length.

	See Also
	--------
	make_array : Translates `function` to `mapped` array from given `domain`.
	endpoint : Find derivatives at endpoints if not explicitly provided by data, `function_derivative` nor a lambda expression.
	midpoint : Finds the derivatives at points within the bounds given `domain` and `function`.

	Notes
	-----
	Method uses many, low-ordered polynomials to fit larger datasets. This minimizes computational load, which, conversely, greatly increases for larger datasets that yield high-ordered polynomials.

	General form

	.. math::
		S_{j}(x) = a_{j} + b_{j}(x - x_{j}) + c_{j}(x - x_{j})^{2} + dj(x - x_{j})^{3}

	`clamped()` splines fit the constructed polynomial to the given data and its derivatives at either endpoint.

	`natural()` splines set the derivative at either endpoint to be 1.

	Definitions of cubic spline conditions:
		a) :math:`S(x)` is a cubic polynomial, :math:`S_{j}(x)` on sub-interval :math:`[x_{j}, x_(j+1)]` for each :math:`j \in [0, 1, ..., n-1]`;

		b) :math:`S_{j}(x_{j}) = f(x_{j})` and :math:`S_{j}(x_{j+1}) = f(x_{j+1})` for each :math:`j \in [0, 1, ..., n-1]`;

		c) :math:`S_{j+1}(x_{j+1}) = S_{j}(x_{j+1})` for each :math:`j \in [0, 1, ..., n-2]`;

		d) :math:`S_{j+1}'(x_{j+1}) = S_{j}'(x_{j+1})` for each :math:`j \in [0, 1, ..., n-2]`;

		e) One of the following conditions is satisfied:
			1) :math:`S''(x_{0}) = S''(x_{n}) = 0` -> `'natural'`

			2) :math:`S'(x_{0}) = f'(x_{0})` and :math:`S'(x_{n}) = f'(x_{n})` -> `'clamped'`
	"""

	def __init__(
		self,
		domain: tuple,
		function: tuple,
		variable: Optional[str]="x"
	):
		self.__domain_name, self.__function_name = _retrieve_name(domain), _retrieve_name(function)
		self.domain = X = np.array(domain)
		if np.sum(X.shape) > X.shape[0]: raise IndexError(CubicSpline.__BadDomainError(self.__domain_name))
		# if isinstance(function, (str)):
		# 	self.function_str = function_str = ex.fast_parse_latex(function)
		# 	self.function = function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
		# 	self.mapped = make_array(X, function)
		# 	#print("String expression converted to lambda function.")
		# #elif isinstance(function, (FunctionType)):
		# #	self.function_str = function_str = _retrieve_expression(function)
		# #	self.function = function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
		# #	self.g = make_array(X, function)
		if isinstance(function, (list, tuple, np.ndarray)):
			self.mapped = self.function = function = np.array(function)
		else: raise TypeError(CubicSpline.__BadFunctionError(self.__function_name))
		if np.sum(self.domain.shape) != np.sum(self.mapped.shape) or self.domain.shape[0] != self.mapped.shape[0]:
			raise IndexError(CubicSpline.__BadDataError(self.__domain_name, self.__function_name))
		self.variable = variable
	
	__BadDomainError = lambda domain_name: f"Input domain, '{domain_name}' was not a one-dimensional array."
	__BadFunctionError = lambda function_name: f"Input range, '{function_name}' was neither function of type string nor an one-dimensional array."
	__BadDataError = lambda domain_name, function_name: f"Arrays '{domain_name}' and '{function_name}' must be of equal length."

	def clamped(self, function_derivative: Optional[tuple]=None) -> Tuple[np.ndarray, Tuple[FunctionType]]:
		"""The bookend polynomials will have the same slope entering and exiting the interval as the derivative at the respective endpoint.

		Parameters
		----------
		function_derivative : tuple, optional
			Derivative at each point in `function`.

		Returns
		-------
		Y : np.ndarray
			Finally evaluated solutions.
		splines : list
			Aggregate of lambda expressions for the spline in each interval.

		Raises
		------
		ValueError
			If `function_derivative` is not an expression or function and is not an one-dimensional array.
		IndexError
			If `domain`, `function`, and `function_derivative` are not the same length.
		ValueError
			Output message that derivative data or expression is missing.

		See Also
		--------
		midpoint : Calculates derivative of points within dataset.
		endpoint : Calculates derivatives at either end of dataset.

		Notes
		-----
		`function_derivative` will be calculated from `domain` and `mapped` if not specified.
		"""
		def _algorithm(g, gp):
			Y, YP = np.array(g), np.array(gp)
			# STEP 1:   build list, h_i
			H = np.zeros(n)
			for i in range(n):
				H[i] = X[i+1] - X[i]
			# STEP 2:   define alpha list endpoints
			A, AP, ALPHA = Y, YP, np.zeros(m)
			ALPHA[0] = 3*(A[1] - A[0])/H[0] - 3*AP[0]
			ALPHA[n] = 3*AP[n] - 3*(A[n] - A[n-1])/H[n-1]
			# STEP 3:   build list, alpha_i
			for i in range(1, n):
				ALPHA[i] = 3/H[i]*(A[i+1] - A[i]) - 3/H[i-1]*(A[i] - A[i-1])
			# Algorithm 6.7 to solve tridiagonal
			# STEP 4:   define l, mu, and z first points
			L, MU, Z, C = np.zeros(m), np.zeros(m), np.zeros(m), np.zeros(m)
			L[0], MU[0] = 2*H[0], 0.5
			Z[0] = ALPHA[0]/L[0]
			# STEP 5:   build lists l, mu, and z
			for i in range(1, n):
				L[i] = 2*(X[i+1] - X[i-1]) - H[i-1]*MU[i-1]
				MU[i] = H[i]/L[i]
				Z[i] = (ALPHA[i] - H[i-1]*Z[i-1])/L[i]
			# STEP 6:   define l, z, and c endpoints
			L[n] = H[n-1]*(2-MU[i-1])
			Z[n] = (ALPHA[n] - H[n-1]*Z[n-1])/L[n]
			C[n] = Z[n]
			# STEP 7:   build lists c, b, and d
			B, D = np.zeros(n), np.zeros(n)
			for i in range(1, n+1):
				j = n-i
				C[j] = Z[j] - MU[j]*C[j+1]
				B[j] = (A[j+1] - A[j])/H[j] - H[j]*(C[j+1] + 2*C[j])/3
				D[j] = (C[j+1] - C[j])/(3*H[j])
			return Y, A, B, C, D
		try: self.__function_derivative_name = _retrieve_name(function_derivative)
		except IndexError: self.__function_derivative_name = "fp"
		BadDerivativeError = lambda fp_name: f"Derivative range, '{fp_name}' was neither function nor expression and not an one-dimensional array."
		BadDataError = lambda domain_name, function_name, fp_name: f"Arrays '{domain_name}', '{function_name}', and '{fp_name}' must be of equal length."
		MissingDerivativeError = lambda fp_name: f"Missing derivative data or expression assignment for '{fp_name}'."
		f, X, g, variable = self.function, self.domain, self.mapped, self.variable
		if not isinstance(function_derivative, type(None)):
			# if isinstance(function_derivative, (FunctionType)): gp = make_array(X, function_derivative)
			# else:
			function_derivative = np.array(function_derivative)
			if np.sum(function_derivative.shape) > function_derivative.shape[0]: raise ValueError(BadDerivativeError(self.__function_derivative_name))
			elif len(X) != len(function_derivative): raise IndexError(BadDataError(self.__domain_name, self.__function_name, self.__function_derivative_name))
			else: gp = function_derivative
		else:
			# if isinstance(f, (str, FunctionType)):
			# 	##f = sp.lambdify(variable, sym_function)
			# 	##fp = sp.diff(sym_function)
			# 	#fp = sp.lambdify(self.variable, sp.diff(self.function_str, self.variable))
			# 	#gp = make_array(X, fp)
			# 	gp = make_array(X, ex.fast_derive_latex(self.function_str, variable))
			# #if isinstance(f, (FunctionType)):
			# #	f = _retrieve_expression(f)
			# #	f = make_array(X, f)
			# #elif isinstance(f, (str)):
			# #	gp = make_array(X, ex.fast_derive_latex(self.function_str, variable))
			# elif isinstance(g, np.ndarray):
			if isinstance(f, (list, tuple, np.ndarray)):
				if len(X) >= 3: point_type="three"
				elif len(X) >= 5: point_type="five"
				obj = Derivative(X, f, X[1]-X[0], point_type=point_type)
				gp = [obj.endpoint(0)]
				for i in range(1, len(X) - 1): gp.append(obj.midpoint(i))
				gp.append(obj.endpoint(-1))
				gp = np.array(gp)
			else: raise ValueError(MissingDerivativeError(self.__function_derivative_name))
		m, n = len(X), len(X) - 1
		Y, A, B, C, D = _algorithm(g, gp)
		splines, splines_str = [], []
		# ltx_expression = r"aj + bj*(x - xj) + cj*(x - xj)^{2} + dj*(x - xj)^{3}"
		for j in range(n):
			xj, aj, bj, cj, dj = X[j], A[j], B[j], C[j], D[j]
			# ltx_dict = {
			# 	"aj": aj,
			# 	"bj": bj,
			# 	"cj": cj,
			# 	"dj": dj,
			# 	"xj": xj
			# }
			# parsed_string = ex.fast_parse_latex(ltx_expression, ltx_dict)
			# splines_str.append(parsed_string)
			# sj = lambda x: ex.fast_eval_latex(parsed_string, {variable: x})
			sj = sp.lambdify(sp.Symbol(variable), aj + bj*(sp.Symbol(variable) - xj) + cj*(sp.Symbol(variable) - xj)**2 + dj*(sp.Symbol(variable) - xj)**3)
			splines.append(sj)
		return Y, splines

	def natural(self) -> Tuple[np.ndarray, Tuple[FunctionType]]:
		"""The endpoint derivatives entering and exiting the interval are assumed to be 1.

		Returns
		-------
		Y : np.ndarray
			Finally evaluated solutions.
		splines : list
			Aggregate of lambda expressions for each spline on each interval.
		"""
		def _algorithm(g):
			Y = g
			# STEP 1:   build list, h_i
			H = np.zeros(n)
			for i in range(n):
				H[i] = X[i+1] - X[i]
			# STEP 2:   build list, alpha_i
			A, ALPHA = Y, np.zeros(m)
			for i in range(1, n):
				ALPHA[i] = 3/H[i]*(A[i+1] - A[i]) - 3/H[i-1]*(A[i] - A[i-1])
			# Algorithm 6.7 to solve tridiagonal
			# STEP 3:   define l, mu, and z first points
			L, MU, Z, C = np.zeros(m), np.zeros(m), np.zeros(m), np.zeros(m)
			L[0], MU[0], Z[0] = 1, 0, 0
			# STEP 4:   build lists l, mu, and z
			for i in range(1, n):
				L[i] = 2*(X[i+1] - X[i-1]) - H[i-1]*MU[i-1]
				MU[i] = H[i]/L[i]
				Z[i] = (ALPHA[i] - H[i-1]*Z[i-1])/L[i]
			# STEP 5:   define l, z, and c endpoints
			L[n], Z[n], C[n] = 1, 0, 0
			# STEP 6:   build lists c, b, and d
			B, D = np.zeros(n), np.zeros(n)
			for i in range(1, n+1):
				j = n-i
				C[j] = Z[j] - MU[j]*C[j+1]
				B[j] = (A[j+1] - A[j])/H[j] - H[j]*(C[j+1] + 2*C[j])/3
				D[j] = (C[j+1] - C[j])/(3*H[j])
			return Y, A, B, C, D
		X, g, variable = self.domain, self.mapped, self.variable
		m, n = len(X), len(X) - 1
		Y, A, B, C, D = _algorithm(g)
		splines, splines_str = [], []
		# ltx_expression = r"aj + bj*(x - xj) + cj*(x - xj)**2 + dj*(x - xj)**3"
		for j in range(n):
			xj, aj, bj, cj, dj = X[j], A[j], B[j], C[j], D[j]
			# ltx_dict = {
			# 	"aj": aj,
			# 	"bj": bj,
			# 	"cj": cj,
			# 	"dj": dj,
			# 	"xj": xj
			# }
			# parsed_string = ex.fast_parse_latex(ltx_expression, ltx_dict)
			# splines_str.append(parsed_string)
			# #sj = lambda x: ex.fast_eval_latex(parsed_string, {variable: x})
			sj = sp.lambdify(sp.Symbol(variable), aj + bj*(sp.Symbol(variable) - xj) + cj*(sp.Symbol(variable) - xj)**2 + dj*(sp.Symbol(variable) - xj)**3)
			splines.append(sj)
		return Y, splines

def hermite(
	domain: tuple,
	function: tuple,
	variable: Optional[str]="x",
	function_derivative: Optional[tuple]=None
) -> FunctionType:
	r"""Given a `domain` and `function`, construct a Hermetic polynomial.

	Parameters
	----------
	domain, function, function_derivative : tuple
		Input domain, range, and derivative (optional) from which to build Hermetic polynomial.
	variable : string
		Respected variable in derivative of equation. Defaults to `"x"`.

	Returns
	-------
	polynomial : lambda
		Lambdified Hermetic polynomial.

	Raises
	------
	IndexError
		If `domain` is not a one-dimensional array.
	IndexError
		If `function` is not a one-dimensional array.
	IndexError
		If `domain` and `function` are of unequal length.
	TypeError
		If `function_derivative` is not an expression or function and is not an one-dimensional array.
	IndexError
		If `domain`, `function`, or `function_derivative` are of unequal lengths.
	TypeError
		If `function_derivative` is not given and `function` is not an expression, then missing derivative data or expression.

	Warns
	-----
	MadePolyInformation : string
		Displays the string form of the equation.

	Warnings
	--------
	Slow computation time for larger datasets.

	Notes
	-----
	`function_derivative` calculated if not specified.

	Osculating curve incorporates Taylor and Lagrangian polynomials to kiss the data and match each data point's derivatives which fits the curve to the shape of the data and its trend.
	"""
	domain_name, function_name, function_derivative_name = _retrieve_name(domain), _retrieve_name(function), _retrieve_name(function_derivative)
	domain, function = np.array(domain), np.array(function)
	BadDomainError = lambda domain_name: f"Input domain, '{domain_name}' was not a one-dimensional array."
	BadFunctionError = lambda function_name: f"Input range, '{function_name}' was not a one-dimensional array."
	BadDataError = lambda domain_name, function_name: f"Arrays '{domain_name}' and '{function_name}' must be of equal length."
	BadFunctionDerivativeError = lambda function_derivative_name: f"Input function derivative range, '{function_derivative_name}'was neither lambda expression nor an one-dimensional array."
	BadFunctionDerivativeDataError = lambda domain_name, function_name, function_derivative_name: f"Arrays '{domain_name}', '{function_name}', and '{function_derivative_name}' must be of equal length."
	MissingDerivativeError = lambda function_derivative_name: f"Missing derivative data or expression assignment for '{function_derivative_name}'"
	MadePolyInformation = lambda polynomial_str: f"I have found your requested polynomial! P = {polynomial_str}"
	if np.sum(domain.shape) > domain.shape[0]: raise IndexError(BadDomainError(domain_name))
	# if isinstance(function, (str, FunctionType)):
	# 	# if isinstance(function, str):
	# 	# 	function_str = ex.fast_parse_latex(function)
	# 	# 	function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
	# 	g = make_array(domain, function)
	if isinstance(function, (list, tuple, np.ndarray)):
		if np.sum(np.array(function).shape) > np.array(function).shape[0]: raise IndexError(BadFunctionError(function_name))
		if len(domain) != len(function): raise IndexError(BadDataError(domain_name, function_name))
		g = np.array(function)
	else: raise IndexError(BadFunctionError(function_name))
	if isinstance(function_derivative, type(None)):
		# if isinstance(function, FunctionType):
		# 	# if isinstance(function, str):
		# 	# 	fp_str = ex.fast_derive_latex(ex.fast_parse_latex(function), variable)
		# 	# 	fp = lambda x: ex.fast_eval_latex(fp_str, {variable: x})
		# 	# elif isinstance(function, FunctionType):
		# 	# fp = sp.lambdify(sp.Symbol(variable), sp.diff(function(sp.Symbol(variable))))
		# 	# else:
		# 	#print("Warning! " + missing_FP)
		# 	if len(domain) >= 3: point_type="three"
		# 	elif len(domain) >= 5: point_type="five"
		# 	#fp = [endpoint(domain, g, domain[1]-domain[0], "left", point_type)]
		# 	#for i in range(1, len(domain) - 1):
		# 	#	fp.append(midpoint(domain, g, domain[i]-domain[i-1], i, point_type))
		# 	#fp.append(endpoint(domain, g, domain[-2]-domain[-1], "right", point_type))
		# 	obj = Derivative(domain, g, domain[1]-domain[0], point_type=point_type, variable=variable)
		# 	fp = [obj.endpoint(0)]
		# 	for i in range(1, len(domain) - 1):
		# 		fp.append(obj.midpoint(i))
		# 	fp.append(obj.endpoint(-1))
		# 	gp = make_array(domain, fp)
		# else:
		if isinstance(g, (list, tuple, np.ndarray)):
			if np.sum(g.shape) > np.sum(g.shape[0]): raise TypeError(BadFunctionDerivativeError(function_derivative_name))
			if len(domain) != len(g): raise IndexError(BadFunctionDerivativeDataError(domain_name, function_name, function_derivative_name))
			if len(domain) >= 3: point_type="three"
			elif len(domain) >= 5: point_type="five"
			obj = Derivative(domain, g, domain[1]-domain[0], point_type=point_type)
			fp = [obj.endpoint(0)]
			for i in range(1, len(domain) - 1):
				fp.append(obj.midpoint(i))
			fp.append(obj.endpoint(-1))
			gp = np.array(fp)
		else: raise(TypeError("Uknown input."))
	elif not isinstance(function_derivative, type(None)):
		# if isinstance(function_derivative,(str, FunctionType)):
		# 	if isinstance(function_derivative, str):
		# 		function_derivative_str = ex.fast_parse_latex(function_derivative)
		# 		function_derivative = lambda x: ex.fast_eval_latex(function_derivative_str, {variable: x})
		# 	gp = make_array(domain, function_derivative)
		if isinstance(function_derivative, (list, tuple, np.ndarray)):
			if np.sum(function_derivative.shape) > np.sum(function_derivative.shape[0]): raise ValueError(BadFunctionDerivativeError(function_derivative_name))
			if len(domain) != len(function_derivative): raise ValueError(BadFunctionDerivativeDataError(domain_name, function_name, function_derivative_name))
			gp = np.array(function_derivative)
		else: raise TypeError(MissingDerivativeError(function_derivative_name))
	else: raise TypeError(MissingDerivativeError(function_derivative_name))
	m, n = 2*len(domain)+1, len(domain)
	Q, Z = np.zeros((m,m)), np.zeros(m)
	for i in range(n):
		Z[2*i], Z[2*i + 1] = domain[i], domain[i]
		Q[2*i][0], Q[2*i + 1][0] = g[i], g[i]
		Q[2*i + 1][1] = gp[i]
		if i != 0: Q[2*i][1] = (Q[2*i][0] - Q[2*i - 1][0]) \
			/ (Z[2*i] - Z[2*i - 1])
	for i in range(2, m):
		for j in range(2, i + 1):
			Q[i][j] = (Q[i][j - 1] - Q[i - 1][j - 1]) / (Z[i] - Z[i - j])
	polynomial, terms = 0, 1
	for i in range(n):
		j = 2*i
		polynomial += Q[j][j]*terms
		j = 2*i + 1
		terms *= sp.Symbol(variable) - domain[i]
		polynomial += Q[j][j]*terms
		terms *= sp.Symbol(variable) - domain[i]
	polynomial = sp.lambdify(sp.Symbol(variable), sp.simplify(polynomial))
	# polynomial_str, terms = f"0", "1"
	# for i in range(n):
	# 	j = 2*i
	# 	polynomial_str += f"+({Q[j][j]}*{terms})"
	# 	j = 2*i + 1
	# 	terms = f"({terms})*({variable} - {domain[i]})"
	# 	polynomial_str += f"+({Q[j][j]}*{terms})"
	# 	terms = f"({terms})*({variable} - {domain[i]})"
	# polynomial = lambda x: ex.fast_eval_latex(polynomial_str, {variable: x})
	# polynomial = sp.lambdify(sp.Symbol(variable), sp.simplify(sp.sympify(polynomial_str)))
	#print("Congratulations! ", made_poly + str(polynomial(sp.Symbol(variable))))
	return polynomial

def lagrange(
	domain: tuple,
	function: tuple,
	degree: Optional[int]=None,
	variable: Optional[str]="x"
) -> Tuple[FunctionType, np.ndarray]:
	r"""Given a domain and range, construct a Lagrangian polynomial.

	Parameters
	----------
	domain, function : tuple
		Input domain and range from which to build Lagrangian polynomial.
	degree : int
		Degree of polynomial.
	variable : string
		Respected variable in derivative of equation. Defaults to `"x"`.

	Returns
	-------
	polynomial : lambda
		Lambdified Lagrangian polynomial.
	errors : np.ndarray
		Propogation of bounding error through construction.

	Raises
	------
	IndexError
		If `domain` is not a one-dimensional array.
	IndexError
		If `function` is not a one-dimensional array.
	IndexError
		If `domain` and `function` are of unequal length.

	Notes
	-----
	Polynomial will quickly begin to oscillate for larger datasets.

	Polynomial is of the following form

	.. math::
		P(x) &= f(x_{0})L_{n,0}(x) + ... + f(x_{n})L_{n,n}(x) \text{, where} \\
		L_{n,k} &= \prod_{i=0, i \neq k}^{n} (x - x_{i})/(x_{k} - x_{i})

	Examples
	--------
	A Lagrange polynomial between (2,4) and (5,1) would be found as follows

	.. math::
		L_{0}(x) &= (x - 5)/(2 - 5) = -(x - 5)/3 \\
		L_{1}(x) &= (x - 2)/(5 - 2) = (x - 2)/3 \\
		\implies P(x) &= (4)*(-(x - 5)/3) + (1)*((x - 2)/3) \\
		 &= -x + 6
	"""
	def term(xk, yk, x):
		num, den, L_k = [], [], []
		for xl in domain:
			if xl != xk:
				num.append(x-xl)
				den.append(xk-xl)
		L_k = np.divide(np.prod(num), np.prod(den))
		return L_k * yk
	def error(n, xi, x):
		roots, g, xi_error = [], [], []
		for i in range(n+1):
			root = domain[i]
			roots.append(x - root)
			g = np.prod(roots)
			for k in range(n+1):
				xi = sp.simplify(sp.diff(xi))
			dxi = np.abs(xi.evalf(subs={x: root})/(math.factorial(k)))
			xi_error.append(np.abs(dxi))
			xi_err = np.max(xi_error)
			g_prime = sp.diff(g)
			r = sp.solve(g_prime)
			if i == 0:
				r = g_prime
				gx = g.evalf(subs={x: r})
			elif i == 1:
				gx = g.evalf(subs={x: r[0]})
			else:
				R = []
				for s in r:
					if not isinstance(s, complex):
						R.append(g.evalf(subs={x: s}))
				gx = np.amax(np.abs(R))
		return np.abs(xi_err*gx)
	domain_name, function_name = _retrieve_name(domain), _retrieve_name(function)
	domain, function = np.array(domain), np.array(function)
	if isinstance(degree, type(None)):
		degree = len(domain) - 1
	else:
		degree = int(degree)
	BadDomainError = lambda domain_name: f"Input domain, '{domain_name}' was not a one-dimensional array."
	BadFunctionError = lambda function_name: f"Input range, '{function_name}' was not a one-dimensional array or lambda expression."
	BadDataError = lambda domain_name, function_name: f"Arrays '{domain_name}' and '{function_name}' must be of equal length."
	MadePolyInformation = lambda polynomial_str: f"I have found your requested polynomial! P = {polynomial_str}"
	if np.sum(domain.shape) > np.sum(domain.shape[0]): raise IndexError(BadDomainError(domain_name))
	# if isinstance(function, (str, FunctionType)):
	# 	function = make_array(domain, function)
	if isinstance(function, (list, tuple, np.ndarray)):
		if np.sum(function.shape) > np.sum(function.shape[0]): raise IndexError(BadFunctionError(function_name))
		elif len(domain) != len(function): raise IndexError(BadDataError(domain_name, function_name))
	else: raise TypeError(BadFunctionError(function_name))
	terms, errors = [], np.zeros(len(domain))
	for k in range(degree + 1):
		xk = domain[k]
		terms.append(term(xk, function[k], sp.Symbol(variable)))
		errors[k] = error(k, sp.simplify(sum(terms)), sp.Symbol(variable))
	polynomial = sp.lambdify(sp.Symbol(variable), sp.simplify(sum(terms)))
	# logging.info(MadePolyInformation(str(polynomial)))
	return polynomial, errors

class LeastSquares:
	r"""Interpolate across all points in dataset to minimize error according to rule of fit.

	Parameters
	----------
	domain, function : tuple
		Input domain and range from which to build interpolating polynomial.

	Attributes
	----------
	linear(n: int)
		`n`th-degree polynomial to fit data.
	power()
		Fit power law to data.

	Raises
	------
	IndexError
		If `domain` is not a one-dimensional array.
	IndexError
		If `function` is not a one-dimensional array.
	IndexError
		If `domain` and `function` are of unequal length.
	"""

	def __init__(
		self,
		domain: tuple,
		function: tuple
	):
		self.__domain_name, self.__function_name = _retrieve_name(domain), _retrieve_name(function)
		BadDomainError = lambda domain_name: f"Input domain, '{domain_name}' was not a one-dimensional array."
		BadFunctionError = lambda function_name: f"Input range, '{function_name}' was not a one-dimensional array."
		BadDataError = lambda domain_name, function_name: f"Arrays '{domain_name}' and '{function_name}' must be of equal length."
		domain, function = np.array(domain), np.array(function)
		if np.sum(domain.shape) > np.sum(domain.shape[0]): raise IndexError(BadDomainError(self.__domain_name))
		if np.sum(function.shape) > np.sum(function.shape[0]): raise IndexError(BadFunctionError(self.__function_name))
		if len(domain) != len(function): raise IndexError(BadDataError(self.__domain_name, self.__function_name))
		self.domain, self.function = domain, function

	__MadePolynomialInformation = lambda polynomial_str: f"Information: I have found your requested polynomial! P = {polynomial_str}"

	def linear(
		self,
		degree: int,
		variable: Optional[str]="x"
	) -> Tuple[FunctionType, float]:
		r"""Construct a polynomial of some degree while minimizing the least squares error.

		Parameters
		----------
		degree : int
			Degree of polynomial.

		Returns
		-------
		polynomial : lambda
			Lambdified linear least square polynomial.
		error : float
			Total error.

		Raises
		------
		ValueError
			If prescribed `degree` is not an integer greater than zero.

		See Also
		--------
		SystemOfEquations.conjugate_gradient : Utilize the Conjugate Gradient Method to solve SOE.

		Notes
		-----
		Least squares error := :math:`E = \sum_{i=1}^{m}(y_{i} - P_{n}(x_{i}))^{2}`

		Constructed polynomial of the form: :math:`P(x) = a_{n}x^{n} + a_{n - 1}x^{n - 1} + \dots + a_{1}x + a_{0}`
		"""
		BadDegreeError = lambda n: f"Degree of polynomial, n = {n} must be integer and greater than zero."
		if not isinstance(degree,(int)) or degree <= 0: raise ValueError(BadDegreeError(degree))
		X, Y = self.domain, self.function
		m = len(X)
		A, x = np.zeros((degree+1, degree+1)), np.ones((degree+1,1))
		b = np.zeros_like(x)
		for i in range(degree+1):
			for j in range(degree+1):
				for k in range(m):
					A[i][j] += (X[k])**(i + j)
			for j in range(m):
				b[i] += Y[j]*(X[j]**(i))
		# x = np.linalg.solve(A, b)
		if positive_definite(A):
			x = SystemOfEquations(A, b).conjugate_gradient(x)["Approximations"].values[-1]
		else:
			x = SystemOfEquations(A, b).steepest_descent(x)["Approximations"].values[-1]
			# x = MultiVariableIteration(A, x, b).gauss_seidel()["Approximations"].values[-1]
		polynomial = 0
		for i in range(len(x)): polynomial += x[i]*(sp.Symbol(variable)**i)
		polynomial = sp.lambdify(sp.Symbol(variable), sp.simplify(polynomial))
		# polynomial_str = "0"
		# for i in range(len(x)): polynomial_str += f"+{x[i]}(({variable})^({i}))"
		# polynomial_str = ex.fast_parse_latex(polynomial_str)
		# polynomial = lambda x: ex.fast_eval_latex(polynomial_str, {variable: x})
		#print(least_squares.__MadePolynomialInformation(polynomial_str))
		error = 0
		for i in range(len(x)):
			error += float(Y[i] - polynomial(x[i]))**2
		return polynomial, error

	def power(self) -> Tuple[float, float, FunctionType]:
		r"""Given a domain and range, yield the coefficients for an equation and the equation of the form :math:`y = ax^{b}` [3]_.

		Returns
		-------
		a, b : float
			Leading coefficient and exponent of equation.
		expression : lambda
			Lambda expression of curve-fit with calculated leading coefficient, `a` and exponent, `b`.
		"""
		X, Y = self.domain, self.function
		q1, q2, q3, q4 = [], [], [], []
		for i in range(len(X)):
			q1.append(math.log(X[i])*math.log(Y[i]))
			q2.append(math.log(X[i]))
			q3.append(math.log(Y[i]))
			q4.append(math.log(X[i])**2)
		num = len(X)*np.sum(q1) - np.sum(q2)*np.sum(q3)
		den = len(X)*np.sum(q4) - (np.sum(q2))**2
		b = num/den
		a = math.exp((np.sum(q3) - b*np.sum(q2))/len(X))
		expression = lambda x: a*(x**b)
		# expression = lambda x: ex.fast_eval_latex(f"{a}*x^{b}", {"x": x})
		return a, b, expression

def linear_interpolation(
	x0: float,
	y0: float,
	x1: float,
	y1: float,
	x: float
) -> float:
	r"""y = y0 + (x - x0)*(y1 - y0)/(x1 - x0)"""
	return y0 + (x - x0)*(y1 - y0)/(x1 - x0)

def newton_difference(
	domain: tuple,
	function: Union[tuple,FunctionType],
	center_point: float,
	variable: Optional[str]="x",
	direction: Optional[str]="auto"
) -> FunctionType:
	r"""Given a domain and range, construct some polynomial by Newton's Divided Difference.

	Parameters
	----------
	domain : tuple
		Input domain.
	function : tuple or lambda
		Desired/Found range of interest.
	center_point : float
		Point about which polynomial is evaluated.
	variable : string, optional
		Dependent variable to respect in polynomial construction. Defaults to `"x"`.
	direction : {"auto", "forward", "backward"}, optional
		`'forward'` or `'backward'` construction. Will be chosen automatically if not specified.

	Returns
	-------
	polynomial : lambda
		Lambdified constructed polynomial.

	Raises
	------
	IndexError
		If `domain` is not a one-dimensional array.
	IndexError
		If `function` is not a one-dimensional array.
	IndexError
		If `domain` and `function` are of unequal length.
	ValueError
		If `direction` is neither `'forward'` nor `'backward'`.

	Warns
	-----
	MadePolynomialInformation : string
		Displays the string form of the equation.

	See Also
	--------
	make_array : Maps inputs `function`, if lambda expression, to range from `domain`.

	Notes
	-----
	Direction will be chosen if not specified.

	Polynomials best made with even spacing in `domain`; although, this is not completely necessary.
	"""
	domain_name, function_name = _retrieve_name(domain), _retrieve_name(function)
	BadDomainError = lambda domain_name: f"Input domain, '{domain_name}' was not a one-dimensional array."
	BadFunctionError = lambda function_name: f"Input function, '{function_name}' was not a one-dimensional array."
	BadDataError = lambda domain_name, function_name: f"Arrays '{domain_name}' and '{function_name}' must be of equal length."
	BadDirectionError = lambda direction: f"Supplied direction ('{direction}') was not understood. Please specify 'forward' or 'backward', or let me choose."
	MadePolynomialInformation = lambda polynomial_str: f"I have found your requested polynomial! P = {polynomial_str}"
	domain, center_point = np.array(domain), float(center_point)
	if isinstance(function, FunctionType):
		# if isinstance(function, str):
		# 	function_str = ex.fast_parse_latex(function)
		# 	function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
		# #print("String expression converted to lambda function.")
		function = make_array(domain, function)
	elif isinstance(function, (list, tuple, np.ndarray)):
		function = np.array(function)
	if np.sum(domain.shape) > domain.shape[0]: raise IndexError(BadDomainError(domain_name))
	if np.sum(function.shape) > function.shape[0]: raise IndexError(BadFunctionError(function_name))
	if len(domain) != len(function): raise IndexError(BadDataError(domain_name, function_name))
	if direction == "auto":
		if center_point <= np.median(domain): direction = "forward"
		else: direction = "backward"
	elif direction != "forward" and direction != "backward": raise ValueError(BadDirectionError(direction))
	fterm = lambda fxn, i, j: (fxn[i][j] - fxn[i-1][j])/(fxn[i][0] - fxn[i-j][0])
	m, n = len(domain), len(domain) + 1
	fxn, coeff = np.zeros((m,n)), []
	m, n = m - 1, n - 1	 # change m and n from length to index
	fxn[:,0], fxn[:,1] = domain, function
	for j in range(1, m):
		for i in range(1, m):
			fk = fterm(fxn, i, j)
			fxn[i][j+1] = fk
			if direction == "forward" and i == j:
				coeff.append(fk)
			elif direction == "backward" and i == m - 1:
				coeff.append(fk)
	polynomial, terms = 0, 1
	for c in coeff:
		terms *= sp.Symbol(variable) - domain[coeff.index(c)]
		polynomial += c*np.prod(terms)
	if direction == "forward": polynomial = sp.simplify(polynomial + function[0])
	elif direction == "backward": polynomial = sp.simplify(polynomial + function[m])
	#print(MadePolynomialInformation(polynomial_str))
	polynomial = sp.lambdify(sp.Symbol(variable), polynomial)
	# for c in coeff:
	# 	term_str += f"(x - {domain[coeff.index(c)]})"
	# 	polynomial_str += f"+{c}*{term_str}"
	# if direction == "forward": polynomial_str += f"+{function[0]}"
	# elif direction == "backward": polynomial_str += f"+{function[m]}"
	# #print(MadePolynomialInformation(polynomial_str))
	# polynomial = lambda x: ex.fast_eval_latex(polynomial_str, {variable: x})
	return polynomial
# --------------------

# --------------------
# numerical differentiation and integration
class Derivative:
	r"""Find the numeric derivative at some point within dataset.

	Parameters
	----------
	domain : tuple
		Domain of collected data.
	function : tuple or lambda
		Range of collected data.
	h : float
		Step-size through interval.
	point_type : {"three", "five", "2nd_derivative"}, optional
		Determines if 3 or 5 point stencil method is used. `"2nd_derivative"` possible for `midpoint()` method. Defaults to 3 point.

	Attributes
	----------
	domain, function : np.ndarray
		Domain and mapped range from data.
	h : float
		Step-size through interval.
	point_type : string
		Stencil method used.

	Methods
	----------
	endpoint(point: int)
		Find the derivative at endpoint of dataset.
	midpoint(point: int)
		Find the derivative at some point within dataset.

	Raises
	------
	IndexError
		If `domain` is not a one-dimensional array.
	IndexError
		If `function` is function and not a one-dimensional array
	ValueError
		If `function` is neither a lambda expression nor one-dimensional array.
	IndexError
		If `domain` and `function` are of unequal length.
	ValueError
		If `point_type` is not `'three'`, `'five'`, nor `'2nd_derivative'`.

	Warnings
	--------
	`point_type="2nd_derivative"` only available for `midpoint` method.

	See Also
	--------
	make_array : Maps input lambda expression, `function` to range from `domain`.

	Notes
	-----
	5 point, :math:`\mathcal{O}(h^{4})` is more accurate than 3 point, :math:`\mathcal{O}(h^{2})`; however, round-off error increases.
	`midpoint` has half the error of `endpoint` because of using more information and performing fewer calculations.
	"""

	def __init__(
		self,
		domain: tuple,
		function: Union[tuple,FunctionType],
		h: float,
		point_type: Optional[str]="three"
	):
		self.__domain_name, self.__function_name = _retrieve_name(domain), _retrieve_name(function)
		BadDomainError = lambda domain_name: f"Input domain, '{domain_name}' was not a one-dimensional array."
		BadFunctionError = lambda function_name: f"Input function, '{function_name}' was not a one-dimensional array."
		BadDataError = lambda domain_name, function_name: f"Arrays '{domain_name}' and '{function_name}' must be of equal length."
		BadTypeError = lambda type: f"I am sorry. The selected type, '{type}' was not understood. Please select: 'three', 'five', or '2nd_derivative'."
		if isinstance(function, FunctionType):
			# if isinstance(function, str):
			# 	self.function_str = function_str = ex.fast_parse_latex(function)
			# 	function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
			# else: self.function_str = function_str = "Lambda"
			self.function = make_array(domain, function)
		elif isinstance(function, (list, tuple, np.ndarray)):
			if np.sum(np.array(domain).shape) > np.array(domain).shape[0]: raise IndexError(BadDomainError(self.__domain_name))
			if np.sum(np.array(function).shape) > np.array(function).shape[0]: raise IndexError(BadFunctionError(self.__function_name))
			if len(domain) != len(function): raise IndexError(BadDataError(self.__domain_name, self.__function_name))
			self.function = np.array(function)
		else: raise ValueError(BadFunctionError(self.__function_name))
		self.step_size = h = float(h)
		if point_type != "three" \
			and point_type != "five" \
				and point_type != "2nd_derivative": raise ValueError(BadTypeError(point_type))
		else: self.point_type = point_type
		# self.variable = variable
		
	__BadPointError = lambda index: f"Index, {index} must be an integer."

	def endpoint(self, point: int) -> float:
		r"""Find the derivative of a bookend point at either end of a dataset.

		Parameters
		----------
		point : int
			Index location in `domain` to evaluate derivative.

		Returns
		-------
		derivative : float
			Evaluated derivative at point.
		"""
		if not isinstance(point,int): raise ValueError(Derivative.__BadPointError(point))
		else: i = point
		derivative = 0
		if i == 0:
			if self.point_type == "three":
				derivative = (-3*self.function[i] + 4*self.function[i+1] - self.function[i+2])/(2*self.step_size)
			if self.point_type == "five":
				derivative = (-25*self.function[i] + 48*self.function[i+1] \
					- 36*self.function[i+2] + 16*self.function[i+3] \
						- 3*self.function[i+4])/(12*self.step_size)
		elif i == -1 or i == len(self.domain)-1:
			if self.point_type == "three":
				derivative = (-3*self.function[i] + 4*self.function[i-1] - self.function[i-2])/(2*self.step_size)
			if self.point_type == "five":
				derivative = (-25*self.function[i] + 48*self.function[i-1] \
					- 36*self.function[i-2] + 16*self.function[i-3] \
						- 3*self.function[i-4])/(12*self.step_size)
		return derivative

	def midpoint(self, point: int) -> float:
		r"""Find the derivative of some point within a dataset.

		Parameters
		----------
		point : int
			Index location in `domain` to evaluate derivative.

		Returns
		-------
		derivative : float
			Evaluated derivative at point.
		"""
		if not isinstance(point,int): raise ValueError(Derivative.__BadPointError(point))
		else: i = point
		derivative = 0
		if self.point_type == "three":
			derivative = (self.function[i+1] - self.function[i-1])/(2*self.step_size)
		elif self.point_type == "five":
			derivative = (self.function[i-2] - 8*self.function[i-1] \
				+ 8*self.function[i+1] - self.function[i+2])/(12*self.step_size)
		elif self.point_type == "2nd_derivative":
			derivative = (self.function[i-1] - 2*self.function[i] + self.function[i+1])/(self.step_size**2)
		return derivative

class Integrate:
	r"""Find the definite integral by some composite numeric quadrature.

	Parameters
	----------
	function : tuple or lambda
		Either mapped range from or mapping function for `domain`.
	domain : tuple
		Domain over which `function` is evaluated.
	a, b, h : float
		Left and right-hand bound of interval and step-size through that interval.
	scheme : {"open", "closed"}, optional
		`"open"` excludes the endpoints of dataset; conversely, `"closed"` includes endpoints. Defaults to `"open"`.

	Methods
	-------
	simpson()
		Apply Simpson's Rule.
	trapezoidal()
		Apply Trapezoidal Quadrature.

	Attributes
	----------
	function, domain : np.ndarray
		Domain and range defining integration bounds.
	a, b, h : float
		Left and right-hand bound of interval and step-size through that interval.
	scheme : string
		Defines integration scheme.

	Raises
	------
	IndexError
		If `domain` is not a one-dimensional array.
	TypeError
		If `function` is not an expression.

	Notes
	-----
	Dataset may contain unevenly spaces points.

	Unless specified and if `domain` is defined, `a` and `b` will be the left and right-hand bounds, respectively, of `domain`. If `domain` is not defined and `a`, `b`, and `h` are, then `domain` is constructed by `np.arange(a, b, h)`.
	"""

	def __init__(
		self,
		function: Union[tuple,FunctionType],
		domain: Optional[tuple]=None,
		a: Optional[float]=None,
		b: Optional[float]=None,
		h: Optional[float]=None,
		scheme: Optional[str]="open"
	):
		self.__domain_name, self.__function_name = _retrieve_name(domain), _retrieve_name(function)
		BadDomainError = lambda domain_name: f"Input domain, '{domain_name}' was not a one-dimensional array."
		BadFunctionError = lambda function_name: f"Input range, '{function_name}' must be expression, not list or tuple."
		if isinstance(domain, type(None)):
			domain = np.arange(a, b+h, h)
		elif np.sum(np.array(domain).shape) > np.sum(np.array(domain).shape[0]):
			raise IndexError(BadDomainError(self.__domain_name))
		else: raise IndexError(BadDomainError(self.__domain_name))
		if isinstance(function, (list, tuple, np.ndarray)):
			function = np.array(function)
		elif isinstance(function, FunctionType):
			# if isinstance(function, str):
			# 	self.function_str = function_str = ex.fast_parse_latex(function)
			# 	function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
			self.function = function = make_array(domain, function)
			#print("String expression converted to lambda function.")
		#elif not isinstance(function,(FunctionType, sp.Expr)):
		#	if np.sum(domain.shape) > np.sum(domain.shape[0]): raise ValueError("ERROR! " + bad_X)
		#	else: raise ValueError("ERROR! " + bad_f)
		else: raise TypeError(BadFunctionError(self.__function_name))
		if isinstance(domain, type(None)):
			self.domain = np.arange(a, b, h)
		else:
			self.domain = np.array(domain)
			# self.variable = variable
			if a == None: a = domain[0]
			if b == None: b = domain[-1]
			if h == None: h = domain[1]-domain[0]
		self.a, self.b, self.h = float(a), float(b), float(h)
		self.scheme = scheme

	def simpson(self) -> Tuple[np.ndarray, np.ndarray, float]:
		r"""Gives exact result for polynomials of degree < 3 because error function utilizes the fourth derivative.

		Notes
		-----
		Theorem:
			Let :math:`f` be in :math:`C^{4}[a,b]`, :math:`n` be even, :math:`h = (b-a)/n`, and :math:`x_{j} = a + jh` for :math:`j = 0, 1, ..., n`. There exists a :math:`\mu` \in (a,b)` for which the quadrature for :math:`n` sub-intervals can be written with its error term as:

			.. math::
				\int_{a}^{b}f(x)dx = \frac{h}{3}\bigl[ f(a) + 2*[\sum_{j=1}^{n/2 - 1}{f(x_{2j})}] + 4[\sum_{j=1}^{n/2}{f(x_{2j-1})}] + f(b) \bigr] - (b-a)h^{4}f^{\text{iv}}(\mu)/180.

			Where: :math:`(b-a)h^{4}f^{\text{iv}}(\mu)/180 \rightarrow \mathcal{O}(h^{4})`

		Returns
		-------
		X, Y : np.ndarray
			Domain and range used to calculate numeric integral.
		F : float
			Numeric integral.
		"""
		f, X = self.function, self.domain
		a, b, h = self.a, self.b, self.h
		if self.scheme == "open":
			n = math.ceil((b-a)/h)
			XJ1, XJ2, XJ, = [], [], [a]
			YJ1, YJ2, YJ, = [], [], [f(a) if not isinstance(f, np.ndarray) else f[0]]
			for j in range(1, int(n/2)):
				XJ1.append(a + 2*j*h)
				YJ1.append(f(XJ1[-1]) if not isinstance(f, np.ndarray) else f[2*j])
			z1 = np.sum(YJ1)
			for j in range(1, int(n/2+1)):
				XJ2.append(a + (2*j - 1)*h)
				YJ2.append(f(XJ2[-1]) if not isinstance(f, np.ndarray) else f[2*j-1])
			z2 = np.sum(YJ2)
			for k in range(np.array(XJ1).shape[0]):
				XJ.append(XJ2[k]); YJ.append(YJ2[k])
				XJ.append(XJ1[k]); YJ.append(YJ1[k])
			XJ.append(XJ2[k]); YJ.append(YJ2[k])
			XJ.append(b)
			YJ.append(f(b) if not isinstance(f, np.ndarray) else f[-1])
			X = XJ; Y = YJ
			if not isinstance(f, np.ndarray): F = h/3*(f(a) + 2*z1 + 4*z2 + f(b))
			else: F = h/3*(f[0] + 2*z1 + 4*z2 + f[-1])
		elif self.scheme == "closed":
			if not isinstance(f, np.ndarray): Y = make_array(X, f)
			else: Y = f
			F = 3*h/8*(Y[0] + 3*(np.sum(Y[1:-1])) + Y[-1])
		return X, Y, F

	def trapezoidal(self) -> Tuple[np.ndarray, np.ndarray, float]:
		r"""Gives exact result for polynomials of degree < 2 because error function utilizes the second derivative.

		Notes
		-----
		Theorem:
			Let :math:`f` be in :math:`C^{2}[a,b]`, :math:`h = (b-a)/n`, and :math:`x_{j} = a + jh` for :math:`j = 0, 1, ..., n`. There exists a :math:`\mu \in (a,b)` for which the quadrature for :math:`n` sub-intervals can be written with its error term as:

			.. math::
				\int_{a}^{b}f(x)dx = \frac{h}{2}\bigl[ f(a) + 2[\sum_{j=1}^{n - 1}{f(x_{j})}] + f(b) \bigr] - (b-a)*(h^{2})f''(\mu)/12.

			Where: :math:`(b-a)*(h^{2})f''(\mu)/12 \rightarrow \mathcal{O}(h^{2})`

		Returns
		-------
		X, Y : np.ndarray
			Domain and range used to calculate numeric integral.
		F : float
			Numeric integral.
		"""
		f, X = self.function, self.domain
		a, b, h = self.a, self.b, self.h
		if self.scheme == "open":
			XJ, YJ = [a], [f(a) if not isinstance(f, np.ndarray) else f[0]]
			n = math.ceil((b-a)/h)
			for j in range(1, n):
				XJ.append(a + j*h)
				YJ.append(f(XJ[-1]) if not isinstance(f, np.ndarray) else f[j])
			z = np.sum(YJ[1:])
			XJ.append(b);
			YJ.append(f(b) if not isinstance(f, np.ndarray) else f[-1])
			X = XJ; Y = YJ
			if not isinstance(f, np.ndarray): F = h/2*(f(a) + 2*z + f(b))
			else: F = h/2*(Y[0] + 2*z + Y[-1])
		elif self.scheme == "closed":
			if not isinstance(f, np.ndarray):
				Y = make_array(X, f)
				if a < X[0]: Y[0] = f(a)
				if b > X[-1]: Y[-1] = f(b)
			else: Y = f
			F = h/2*(Y[0] + Y[-1])
		return X, Y, F

def gaussian_legendre(function, a, b):
	return sc.integrate.quad(function, a, b)

def richard_extrapolation(
	function: Union[FunctionType,tuple],
	center_point: float,
	h: float,
	order: int,
	direction: Optional[str]="auto",
	variable: Optional[str]="x"
) -> FunctionType:
	r"""Results in higher-accuracy of derivative at point in function with lower-order formulas to minimize round-off error and increase :math:`\mathcal{O}(h)` of truncation error.

	Parameters
	----------
	function : lambda or tuple
		Polynomial over which derivative must be calculated.
	center_point, h : float
		Point about and step-size through which extrapolation centers.
	order : int
		Order for rate of convergence.
	direction : {"auto", "forward", "backward"}, optional
		`'forward'` or `'backward'` construction. Will choose direction if not specified.
	variable : string, optional
		Dependent variable to respect in polynomial construction. Defaults to `"x"`.

	Returns
	-------
	polynomial : lambda
		Lambdified constructed polynomial.

	Raises
	------
	ValueError
		`order` must be an integer greater than zero.
	ValueError
		If `direction` is neither `'forward'` nor `'backward'`.
	TypeError
		If `function` is not an expression.

	See Also
	--------
	newton_difference : Newton Difference method to build extrapolation for function's derivative and order of error.
	"""
	function_name = _retrieve_name(function)
	BadExpressionError = lambda function_name: f"Function, '{function_name}' must be a lambda expression."
	BadOrderError = lambda order: f"Order, n = {order} must be an integer greater than zero."
	BadDirectionError = lambda direction: f"Supplied direction ('{direction}') was not understood. Please specify 'forward' or 'backward'."
	BadDataError = lambda domain_name, function_name: f"Arrays '{domain_name}' and '{function_name}' must be of equal length."
	if not isinstance(order, (int, float)) or order <= 0: raise ValueError(BadOrderError(order))
	if direction != "auto" and direction != "forward" and direction != "backward": raise ValueError(BadDirectionError(direction))
	if isinstance(function, FunctionType):
		# if isinstance(function, str):
		# 	function_str = ex.fast_derive_latex(ex.fast_parse_latex(function), variable)
		# 	function = lambda x: ex.fast_eval_latex(function_str, {variable: x})
		center_point, h = float(center_point), float(h)
		X, FX = [], []
		for i in range(order+1):
			dx = h / (2**order) * (2**i)
			X.append(center_point + dx)
			FX.append(function(center_point + dx))
	#elif isinstance(function,(FunctionType, sp.Expr)):
	#	sym_function = sp.N(sp.sympify(function(variable)))
	#	function = sp.lambdify(variable, sym_function)
	#	print(f"Information: Input expression, {sym_function} used.")
	#elif isinstance(function, (list, tuple, np.ndarray)):
	#	if np.sum(np.array(domain).shape) != 0 and len(domain) == len(function):
	#		X, FX = np.array(domain), np.array(function)
	#	else: raise ValueError(BadDataError(_retrieve_name(domain), function_name))
	else:
		raise TypeError(BadExpressionError(function_name))
	return newton_difference(X, FX, center_point, variable=variable, direction=direction)
# --------------------

# --------------------
# differential equations
class __ode(object):
	r"""Assign common attributes to objects.

	Parameters
	----------
	function : lambda
		Time derivative of function(s) to approximate.
	a, b, alpha : float
		Initial and final time with initial value in function at `a`.
	variables : tuple, optional
		Collection of symbolic or string variables to respect in function.
	steps : int, optional
		Maximum number of time steps to discretize domain.

	Attributes
	----------
	function : expression
		Time derivative of function(s) to approximate.
	a, b, alpha : float
		Initial and final time with initial value in function at `a`.
	variables : tuple, optional
		Collection of symbolic or string variables to respect in function.
	steps : int, optional
		Maximum number of time steps to discretize domain.

	Raises
	------
	ValueError
		If `steps` constraint is not an integer greater than zero.
	TypeError
		If input `function`(s) cannot be understood as lambda expression.

	Warnings
	--------
	Make sure the independent variable is the first element of `variables`!
	"""

	def __init__(
		self,
		function: Tuple[FunctionType],
		a: float,
		b: float,
		alpha: float,
		variables: Optional[Tuple[str]]=("t", "y"),
		steps: Optional[int]=100
	):
		if steps <= 0 or not isinstance(steps, (int, float)): raise ValueError(f"Number of time steps, N = {steps} must be an integer greater than zero.")
		if np.sum(np.array(function).shape) > 0:
			F, F_str = [], []
			for f in function:
				# if isinstance(f, str):
				# 	#g = lambda x: eval(f)
				# 	#f = sp.lambdify(*variables, g(*variables))
				# 	function_str = ex.fast_parse_latex(f)
				# 	F_str.append(function_str)
				# 	f = lambda t, y: ex.fast_eval_latex(function_str, {"t": t, "y": y})
				# 	#print("String expression converted to lambda function.")
				# elif isinstance(f, FunctionType):
				# 	F_str.append("Lambda")
				# else: raise TypeError("Unknown input.")
				if isinstance(f, FunctionType): F.append(f)
			function = F
			# function_str = F_str
		else:
			# if isinstance(function, str):
			# 	#g = lambda x: eval(function)
			# 	#function = sp.lambdify(*variables, g(*variables))\
			# 	function_str = ex.fast_parse_latex(function)
			# 	function = lambda t, y: ex.fast_eval_latex(function_str, {"t": t, "y": y})
			# 	#print("String expression converted to lambda function.")
			# elif isinstance(function, FunctionType):
			# 	#sym_function = sp.N(sp.sympify(function(*variables)))
			# 	#function = sp.lambdify(variables, sym_function)
			# 	#print(f"Information: Input expression, {sym_function} used.")
			# 	function_str = "Lambda"
			# else: raise TypeError("Unknown input.")
			if not isinstance(function, FunctionType): raise TypeError("Input function(s) must be lambda expression(s).")
		self.function = function
		# self.function_str = function_str
		self.a, self.b = a, b
		self.step_size = float((b - a)/(steps + 1))
		self.alpha = alpha
		self.variables = variables
		self.steps = int(steps + 1)

class IVP(__ode):
	r"""Class containing Initial Value Problem (IVP) methods.

	Parameters
	----------
	function : expression
		Time derivative of function(s) to approximate.
	a, b, alpha : float
		Initial and final time with initial value in function at `a`.
	variables : tuple, optional
		Collection of string variables to respect in `function`(s).
	steps : int, optional
		Maximum number of time steps to discretize domain.

	Attributes
	----------
	function : expression
		Time derivative of function to approximate.
	a, b, alpha : float
		Initial and final time with initial value in function at `a`.
	variables : tuple, optional
		Collection of symbolic or string variables to respect in function.
	steps : int, optional
		Maximum number of time steps to discretize domain.

	Methods
	-------
	backward_euler()
		Implicit, first-order accuracy from Taylor approximation. Best suited to stiff equations.
	forward_euler()
		Explicit, first-order accuracy from Taylor approximation. Not recommended.
	improved_euler()
		Explicit, first-order accuracy from Taylor approximation.
	runge_kutta()
		Explicit, fourth-order accuracy bypassing higher-order derivatives as in Taylor-based methods.
	trapezoidal(power=-6, max_iter=100)
		Implicit, second-order accuracy derived from Trapezoidal Integration.

	Raises
	------
	ValueError
		If `steps` constraint is not an integer greater than zero.
	TypeError
		If input `function`(s) cannot be understood as lambda expression.

	Notes
	-----
	Make sure the independent variable is the first element of `variables`!
	"""

	def __init__(
		self,
		function: Tuple[FunctionType],
		a: float,
		b: float,
		alpha: float,
		variables: Optional[Tuple[str]]=("t", "y"),
		steps: Optional[int]=100
	) -> pd.DataFrame:
		super().__init__(function, a, b, alpha, variables=variables, steps=steps)

	def backward_euler(
		self,
		power: float=-6,
		max_iter: int=100
	) -> pd.DataFrame:
		r"""Implicitly use information at next time step to approximate IVP differential equation at mesh points between `a` and `b`.

		Parameters
		----------
		power : int, optional
			Signed power to which function error must be within.
		max_iter : int, optional
			Maximum iterations for Newton-Raphson loop.

		Returns
		-------
		pandas.DataFrame() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Attributes
		----------
		step_size : float
			Domain step size.
		iterations, domain, range, increments : tuple
			Collection of steps through, domain used in, range from, and increments between steps in method.

		Raises
		------
		TypeError
			If input `function`(s) cannot be understood as lambda expression.

		See Also
		--------
		SingleVariableIteration.newton_raphson : Root-finding method of single variable equation given an initial guess.
		trapezoidal : Another implicit method but with second-order accuracy.

		Notes
		-----
		Implicit time stepping scheme which is generally suited for stiff equations being conditionally stable.

		Gives first-order accuracy, :math:`\mathcal{O}(h)`.
		"""
		h, t, w0 = self.step_size, self.a, self.alpha
		Y, increments = [w0], [0]
		for i in range(1, self.steps):
			t = self.a + i*h
			# w = w0 + h*function(t + h, w0 + h*function(t, w0))
			w = lambda x: x - (w0 + h*self.function(t + h, x))
			#w = "x - (w0 + h*" + self.function_str + ")"
			#sys.stdout =  open(os.devnull, "w")
			obj = SingleVariableIteration(w, t, t+h, power=power, variable="t", iter_guess=max_iter)
			w = obj.newton_raphson(w0)["Approximations"].values[-1]
			#sys.stdout = sys.__stdout__
			Y.append(w)
			increments.append(abs(w - w0))
			# t, w0 = a + i*h, w
			w0 = w
		self.iterations = np.arange(self.steps)
		self.domain = np.linspace(self.a, t+h, self.steps)
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Domain": self.domain,
			"Range": self.range,
			"Increments": self.increments
		})

	def forward_euler(self) -> pd.DataFrame:
		r"""Explicitly march forward through time to approximate IVP differential equation at mesh points between `a` and `b`.

		Returns
		-------
		pandas.DataFrame() : DataFrame
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Attributes
		----------
		step_size : float
			Domain step size.
		iterations, domain, range, increments : tuple
			Collection of steps through, domain used in, range from, and increments between steps in method.

		Raises
		------
		TypeError
			If input `function`(s) cannot be understood as lambda expression.

		Warnings
		--------
		Error grows linearly; therefore, method is a good place to start, but others should be explored.

		Notes
		-----
		Explicit time stepping scheme via first-order Taylor approximations.
		"""
		h, t, w0 = self.step_size, self.a, self.alpha
		Y, increments = [w0], [0]
		for i in range(1, self.steps):
			t = self.a + i*h
			w = w0 + h*self.function(t, w0)
			Y.append(w)
			increments.append(w - w0)
			w0 = w
		self.iterations = np.arange(self.steps)
		self.domain = np.linspace(self.a, t+h, self.steps)
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Domain": self.domain,
			"Range": self.range,
			"Increments": self.increments
		})

	def improved_euler(self) -> pd.DataFrame:
		r"""Explicit implementation of second-order, Runge-Kutta Method. Also known as Modified Euler Method.

		Returns
		-------
		pandas.DataFrame() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Attributes
		----------
		step_size : float
			Domain step size.
		iterations, domain, range, increments : tuple
			Collection of steps through, domain used in, range from, and increments between steps in method.

		Raises
		------
		TypeError
			If input `function`(s) cannot be understood as lambda expression.

		See Also
		--------
		runge_kutta

		Notes
		-----
		Is equivalent to :math:`2^{\text{nd}}`-Order Runge-Kutta (Midpoint) Method where endpoints `a` and `b` are 0.5 and :math:`\lambda` = 1 with :math:`\mathcal{O}(h^{2})`.

		Explicit time stepping scheme.
		"""
		h, t, w0 = self.step_size, self.a, self.alpha
		ea, eb, lam = 1/2, 1/2, 1
		Y, increments = [w0], [0]
		for i in range(1, self.steps):
			t = self.a + i*h
			w = w0 + h*(ea*self.function(t, w0) + eb*self.function(t + lam*h, w0 + lam*h*self.function(t, w0)))
			Y.append(w)
			increments.append(abs(w - w0))
			w0 = w
		self.iterations = np.arange(self.steps)
		self.domain = np.linspace(self.a, t+h, self.steps)
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Domain": self.domain,
			"Range": self.range,
			"Increments": self.increments
		})

	@_alias(improved_euler)
	def modified_euler(self) -> pd.DataFrame:
		"""`modified_euler` is an alias for `improved_euler`."""
		logging.warn(self.modified_euler.__doc__)
		pass

	def runge_kutta(self) -> pd.DataFrame:
		r"""Explicit, fourth-order method.

		Returns
		-------
		pandas.DataFrame() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Attributes
		----------
		step_size : float
			Domain step size.
		iterations, domain, range, increments : tuple
			Collection of steps through, domain used in, range from, and increments between steps in method.

		Raises
		------
		TypeError
			If input `function`(s) cannot be understood as lambda expression.

		Notes
		-----
		Achieves higher-order, local truncation error, :math:`\mathcal{O}(h^{4})` like Taylor-based methods--such as `forward_euler`--but without the need to compute the higher-order derivatives.

		Explicit time stepping scheme.
		"""
		h, t, w0 = self.step_size, self.a, self.alpha
		Y, increments = [w0], [0]
		for i in range(1, self.steps):
			t = self.a + i*h
			k1 = h*self.function(t, w0)
			k2 = h*self.function(t + h/2, w0 + k1/2)
			k3 = h*self.function(t + h/2, w0 + k2/2)
			k4 = h*self.function(t + h, w0 + k3)
			w = w0 + (k1 + 2*k2 + 2*k3 + k4) / 6
			Y.append(w)
			increments.append(w - w0)
			w0 = w
		self.iterations = np.arange(self.steps)
		self.domain = np.linspace(self.a, t+h, self.steps)
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Domain": self.domain,
			"Range": self.range,
			"Increments": self.increments
		})

	def trapezoidal(
		self,
		power: float=-6,
		max_iter: int=100
	) -> pd.DataFrame:
		r"""Implicit method derived from Trapezoidal integration and sometimes called Crank-Nicholson.

		Parameters
		----------
		power : int, optional
			Signed power to which function error must be within.
		max_iter : int, optional
			Maximum iterations for Newton-Raphson loop.

		Returns
		-------
		pandas.DataFrame() : dataframe
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Attributes
		----------
		step_size : float
			Domain step size.
		iterations, domain, range, increments : tuple
			Collection of steps through, domain used in, range from, and increments between steps in method.

		Raises
		------
		TypeError
			If input `function`(s) cannot be understood as lambda expression.

		See Also
		--------
		SingleVariableIteration.newton_raphson : Root-finding method of single variable equation given an initial guess.

		Notes
		-----
		Preferred method to `backward_euler` because of :math:`\mathcal{O}(h^{2})` accuracy.

		Tolerance of `SingleVariableIteration.newton_raphson` defined by `10**power`.
		"""
		h, t, w0 = self.step_size, self.a, self.alpha
		self.tol = 10**power
		variables = [sp.symbols(v) for v in self.variables]
		fpy = sp.lambdify(variables, sp.diff(self.function(*variables), variables[0]))
		Y, increments = [w0], [0]
		for i in range(1, self.steps):
			t = self.a + i*h
			k1 = w0 + h*self.function(t, w0)/2
			j, wj0, do_calc = 1, k1, True
			while do_calc:
				wj1 = wj0 - (wj0 - h/2*self.function(t + h, wj0) - k1)/(\
					1 - h/2*fpy(t + h, wj0))
				if abs(wj1 - wj0) <= self.tol:
					w, do_calc = wj1, False
				else:
					wj0 = wj1; j += 1
					if j >= max_iter: do_calc = True
			# f = lambda x: x - h/2*self.function(t + h, x) - k1
			# obj = SingleVariableIteration(f, self.a, self.b, power=power, variable="t", iter_guess=max_iter)
			# w = obj.newton_raphson(k1)["Approximations"].values[-1]
			Y.append(w)
			increments.append(abs(w - w0))
			w0 = w
		self.iterations = np.arange(self.steps)
		self.domain = np.linspace(self.a, t+h, self.steps)
		self.range = np.array(Y)
		self.increments = np.array(increments)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Domain": self.domain,
			"Range": self.range,
			"Increments": self.increments
		})

	@_alias(trapezoidal)
	def crank_nicholson(self) -> pd.DataFrame:
		"""`crank_nicholson` is an alias for `trapezoidal`."""
		logging.warn(self.crank_nicholson.__doc__)
		pass

class BVP(__ode):
	r"""Class containing Boundary Value Problem (BVP) methods.

	Parameters
	----------
	function : lambda
		Time derivative of `function`(s) to approximate.
	a, b, alpha, beta : float
		Initial and final time with initial values in `function`(s) at `a` and `b`.
	variables : tuple, optional
		Collection of string variables to respect in `function`(s).
	steps : int, optional
		Maximum number of time `steps` to discretize domain.

	Attributes
	----------
	function : expression
		Time derivative of `function`(s) to approximate.
	a, b, alpha, beta : float
		Initial and final time with initial values in `function`(s) at `a` and `b`.
	variables : tuple
		Collection of string variables to respect in `function`(s).
	steps : int
		Maximum number of time `steps` to discretize domain.

	Methods
	-------
	finite_difference_method(solver_method="gauss_seidel")
	linear_shooting_method()

	Raises
	------
	ValueError
		If `steps` constraint is not an integer greater than zero.
	TypeError
		If input `function` cannot be understood as lambda expression.

	Notes
	-----
	Make sure the independent variable is the first element of `variables`!
	"""

	def __init__(
		self,
		function: Tuple[FunctionType],
		a: float,
		b: float,
		alpha: float,
		beta: float,
		variables: Optional[Tuple[str]]=("x", "y", "yp"),
		steps: int=100
	) -> pd.DataFrame:
		super().__init__(function, a, b, alpha, variables=variables, steps=steps)
		self.beta = beta

	def finite_difference_method(self, solver_method="gauss_seidel") -> Tuple[pd.DataFrame,pd.DataFrame]:
		r"""Solve a BVP differential equation with Dirichlet boundary conditions by 2 IVP differential equations.

		Parameters
		----------
		solver_method : {"jacobi", "gauss_seidel", "successive_relaxation"}, optional
			Unless specified, SOE will be solved by the `"gauss_seidel"` method.

		Returns
		-------
		pandas.DataFrame() : DataFrame
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.
		pandas.DataFrame() : DataFrame
			Dataframe of cumulative errors through the required number of iterations according to `solver_method`.

		Attributes
		----------
		step_size : float
			Domain step size.
		iterations : tuple
			Collection of steps through method.
		domain : tuple
			Discretized domain between endpoints a and b for so many steps.
		range : tuple
			Range mapped from method through discretized domain between endpoints a and b for so many steps.
		derivatives : tuple
			Collection of derivatives at each step.

		Raises
		------
		TypeError
			If input expression cannot be understood as lambda or sympy expression nor as string.
		ValueError
			Prescribed method is not an available option.

		See Also
		--------
		MultiVariableIteration.jacobi
		MultiVariableIteration.gauss_seidel
		MultiVariableIteration.successive_relaxation

		Notes
		-----
		Uses a Taylor polynomial with a first-order and a second-order IVP equations.

		Converges :math:`\mathcal{O}(h^{2})`.
		"""
		h, alpha, beta = self.step_size, self.alpha, self.beta
		ai, bi, ci, di = [], [], [], []
		p, q, r, ypp = self.function
		t = self.a + h
		ai.append(2 + (h**2)*q(t))
		bi.append(-1 + (h/2)*p(t))
		di.append(-(h**2)*r(t) + (1 + (h/2)*p(t))*alpha)
		for i in range(2, self.steps):
			t = self.a + i*h
			ai.append(2 + (h**2)*q(t))
			bi.append(-1 + (h/2)*p(t))
			ci.append(-1 - (h/2)*p(t))
			di.append(-(h**2)*r(t))
		t = self.b - h
		ai.append(2 + (h**2)*q(t))
		ci.append(-1 - (h/2)*p(t))
		di.append(-(h**2)*r(t) + (1 - (h/2)*p(t))*beta)
		A = np.diagflat(ai)
		A = A + np.diagflat(bi, 1)
		t = A + np.diagflat(ci, -1)
		x = np.zeros(self.steps)
		c = np.array(di)
		obj = MultiVariableIteration(A, x, c, max_iter=1000)
		if solver_method == "gauss_seidel":
			obj.gauss_seidel()
		elif solver_method == "successive_relaxation":
			obj.successive_relaxation()
		elif solver_method == "jacobi":
			obj.jacobi()
		else: raise ValueError("The desired method must be: 'jacobi', 'gauss_seidel', or 'successive_relaxation'.")
		approximations = obj.approximations[-1]
		approximations = np.insert(approximations, 0, alpha)
		approximations = np.append(approximations, beta)
		self.iterations = np.arange(self.steps+2)
		self.domain = np.linspace(self.a, self.b, self.steps+2)
		self.range = np.array(approximations)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Domain": self.domain,
			"Range": self.range
		}), pd.DataFrame(data={
			"Iterations": obj.iterations,
			"Errors": obj.errors
		})

	def linear_shooting_method(self) -> pd.DataFrame:
		r"""Solve a BVP differential equation with 2 IVP differential equations.

		Returns
		-------
		pandas.DataFrame() : DataFrame
			Dataframe of method iterations and time domains, range of approximations for input function, and iterative increments.

		Attributes
		----------
		step_size : float
			Domain step size.
		iterations, domain, range, derivatives : tuple
			Collection of steps through, domain used in, range from, and derivatives at each step in method.

		Raises
		------
		TypeError
			If input `function`(s) cannot be understood as lambda expression.
		"""
		h, alpha, beta = self.step_size, self.alpha, self.beta
		u1, u2, v1, v2 = [alpha], [0], [0], [1]
		p, q, r, ypp = self.function
		for i in range(self.steps):
			t = self.a + i*h
			k11 = h*u2[i]
			k12 = h*(p(t)*u2[i] + q(t)*u1[i] + r(t))
			k21 = h*(u2[i] + k12/2)
			k22 = h*(p(t + h/2)*(u2[i] + k12/2) + q(t + h/2)*(u1[i] + k11/2) + r(t + h/2))
			k31 = h*(u2[i] + k22/2)
			k32 = h*(p(t + h/2)*(u2[i] + k22/2) + q(t + h/2)*(u1[i] + k21/2) + r(t + h/2))
			k41 = h*(u2[i] + k32)
			k42 = h*(p(t + h)*(u2[i] + k32) + q(t + h)*(u1[i] + k31) + r(t + h))
			u1.append(u1[i] + (k11 + 2*k21 + 2*k31 + k41)/6)
			u2.append(u2[i] + (k12 + 2*k22 + 2*k32 + k42)/6)
			###############################
			k11 = h*v2[i]
			k12 = h*(p(t)*v2[i] + q(t)*v1[i])
			k21 = h*(v2[i] + k12/2)
			k22 = h*(p(t + h/2)*(v2[i] + k12/2) + q(t + h/2)*(v1[i] + k11/2))
			k31 = h*(v2[i] + k22/2)
			k32 = h*(p(t + h/2)*(v2[i] + k22/2) + q(t + h/2)*(v1[i] + k21/2))
			k41 = h*(v2[i] + k32)
			k42 = h*(p(t + h)*(v2[i] + k32) + q(t + h)*(v1[i] + k31))
			v1.append(v1[i] + (k11 + 2*k21 + 2*k31 + k41)/6)
			v2.append(v2[i] + (k12 + 2*k22 + 2*k32 + k42)/6)
		w1, w2 = [alpha], [(beta - u1[-1])/v1[-1]]
		for i in range(1, self.steps+1):
			w1.append(u1[i] + w2[0]*v1[i])
			w2.append(u2[i] + w2[0]*v2[i])
			t = self.a + i*h
		self.iterations = np.arange(self.steps+1)
		self.domain = np.linspace(self.a, self.b, self.steps+1)
		self.range = np.array(w1)
		self.derivatives = np.array(w2)
		return pd.DataFrame(data={
			"Iterations": self.iterations,
			"Domain": self.domain,
			"Range": self.range,
			"Derivatives": self.derivatives
		})
# --------------------
#   #   #   #   #   #   #   #   #


#################################
## Test
# test compile of module.
class test:			# test class
	def test():		# test function
		"""Was the module loaded correctly?

		Raises
		------
		success : string
			Prints a message of successful function call.
		"""
		success = "Test complete."
		sys.exit(success)
#   #   #   #   #   #   #   #   #


#################################
## End of Code
# if true, run `main()`
if __name__ == "__main__":
	test.test()	 # "Test complete."
#   #   #   #   #   #   #   #   #