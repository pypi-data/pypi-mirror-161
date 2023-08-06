import numpy as np
from scipy.optimize import minimize
from scipy.linalg import eig
from ..core import CycleEquation

__all__ = ['PhiK']


class PhiK(CycleEquation):

    def __init__(self, n, k, musqr, states=None, basis='symbolic'):
        """
        :param n: int
            Cycle length
        :param k: int
            potential exponent
        :param constants: int
            In this implementation of PhiK, this is mu squared. Naming is simply a convention
        """
        self.n = n
        self.k = k
        self.musqr = musqr
        self.s = musqr + 2
        self.states = states
        self.basis = basis

    @property
    def symbols(self):
        return [-1, 0, 1]

    def eqn(self):
        """ Calculate phi-k equations with respect to a tensor of initial conditions
        lattice_state : np.ndarray
            State variable

        """
        s = self.s
        k = self.k
        states_tensor = self.states
        # the equations of motion
        eqn_tensor = (-1 * np.roll(states_tensor, -1, axis=1) + (-1 * (s - 2) * states_tensor ** k +
                                                                 s * states_tensor) - np.roll(states_tensor, 1, axis=1))
        # the l2 norm, giving us a scalar cost functional
        return eqn_tensor

    def cost(self):
        """ L2 norm of equations used as cost function.

        """
        return (0.5 * np.linalg.norm(self.eqn(), axis=1) ** 2).sum()

    def costgrad(self):
        """ Gradient of L2 norm of equations used as cost function.

        """
        s = self.s
        states = self.states
        Ftensor = self.eqn()
        JTF = -np.roll(Ftensor, 1, axis=1) - np.roll(Ftensor, -1, axis=1) + (
                -3 * (s - 2) * states ** 2 + s) * Ftensor
        return JTF.ravel()

    def jac_tensor(self, states=None):
        """ Calculate all Jacobians for cuurent state

        """
        n, k = self.n, self.k
        if states is None:
            states = self.states
        J = np.zeros([3 ** n, n, n])
        upper_rows, upper_cols = self._kth_diag_indices(J[0], -1)
        lower_rows, lower_cols = self._kth_diag_indices(J[0], 1)
        zeroth = np.repeat(np.arange(3 ** n), len(upper_rows))
        upper_rows = np.tile(upper_rows, 3 ** n)
        upper_cols = np.tile(upper_cols, 3 ** n)
        lower_rows = np.tile(lower_rows, 3 ** n)
        lower_cols = np.tile(lower_cols, 3 ** n)

        J[zeroth, upper_rows, upper_cols] = -1
        J[zeroth, lower_rows, lower_cols] = -1
        J[:, 0, -1] = -1
        J[:, -1, 0] = -1
        tensor_diagonal = (-3 * (self.s - 2) * states ** 2 + self.s).ravel()

        rows, cols = np.diag_indices(n)
        zeroth = np.repeat(np.arange(3 ** n), len(rows))

        J[zeroth, np.tile(rows, 3 ** n), np.tile(cols, 3 ** n)] = tensor_diagonal
        return J

    def _kth_diag_indices(self, a, k):
        rows, cols = np.diag_indices_from(a)
        if k < 0:
            return rows[-k:], cols[:k]
        elif k > 0:
            return rows[:-k], cols[k:]
        else:
            return rows, cols

    def n_cycle_everything(self, compute_eig=False):
        converged_cycles = self.hunt()
        n_jacobians = self.jac_tensor(converged_cycles)

        if compute_eig:
            all_eig_val = []
            all_eig_vec = []
            for each_jac in n_jacobians:
                val, vec = eig(each_jac)
                all_eig_val.append(val)
                all_eig_vec.append(vec[np.newaxis])
            all_eig_val = np.concatenate(all_eig_val)
            all_eig_vec = np.concatenate(all_eig_vec)
            return converged_cycles, all_eig_val, all_eig_vec, n_jacobians
        else:
            return converged_cycles, None, None, n_jacobians

    def generate_states(self, prime=True, sort=False):
        """ Produces all possible combinations of k-ary alphabet, puts them in tensor of shape (k**n, n)

        :return:
        """

        self.states = np.concatenate([coord.ravel().reshape(-1, 1) for coord in np.meshgrid(*(self.symbols for i in
                                                                                              range(self.n)))],
                                     axis=1)
        if sort:
            self.states = np.sort(self.states, axis=0)
        if prime:
            self.states = self.prime_cycles()

        return self

    def hunt(self, method='l-bfgs-b', **kwargs):
        options = kwargs.get('scipy_options')
        cycles = minimize(self.costwrapper(), self.states, jac=self.costgradwrapper(), method=method,
                          options=options)
        cycle_tensor = cycles.x.reshape(-1, self.n)
        return cycle_tensor

    def costwrapper(self):
        """ Functions for scipy routines must take vectors of state variables, not class objects. 


        :return: 
        """

        def minfunc_(x):
            return self.__class__(self.n, self.k, self.musqr, states=x.reshape(-1, self.n)).cost()

        return minfunc_

    def costgradwrapper(self):
        """ Functions for scipy routines must take vectors of state variables, not class objects. 


        :return: 
        """

        def _minjac(x):
            return self.__class__(self.n, self.k, self.musqr, states=x.reshape(-1, self.n)).costgrad()

        return _minjac

    def change_basis(self, to=None):
        if to is None or self.basis == to:
            return self.states
        elif to == 'string':
            # cast as strings of length 2 because of negative sign
            return self.states.astype('|S2')
        elif to == 'symbolic':
            return self.states - 2
        elif to == 'proxy':
            return self.states + 2

    def prime_cycles(self, check_neg=False, check_rev=False):
        initial_conditions = self.states
        # initial conditions should be you entire list of possible shadow state configurations
        # check_neg is a value that takes either 1 or 0 where if it is 1, it will check for phi to negative phi symmetry
        initial_conditions[initial_conditions == 1] = 3
        initial_conditions[initial_conditions == 0] = 2
        initial_conditions[initial_conditions == -1] = 1
        # here i am just changing my shadow state values to a different symbolic alphabet that will work better
        double_cycles = np.append(initial_conditions, initial_conditions, axis=1)
        # double_cycles is each shadow state repeated so that it is twice its length. This is used show checking for cyclic
        # permutations as every permunation exists in the orbit as if it goes through it twice. Ex: all cyclic permutation of 123
        # exist somwhere in 123123
        i = 0
        while i < np.shape(initial_conditions)[0]:  # looping through each row of the initial conditions
            j = np.shape(initial_conditions)[0] - 1
            while j > i:  # looping rows of double_cycles, starting at the bottomw and ending before the row of the current
                # orbit we are checking
                if self.check_cyclic(initial_conditions[i], double_cycles[j]) == True:
                    initial_conditions = np.delete(initial_conditions, j, 0)
                    double_cycles = np.delete(double_cycles, j,
                                              0)  # if a orbit string exists in the double_cycle of of another
                j = j - 1  # orbit, delete one of the cycles
            i = i + 1
        if check_neg == 1:
            initial_conditions[
                initial_conditions == 1] = -1  # if we want to check if cycles are just negatives of another cycle
            initial_conditions[initial_conditions == 2] = 0
            initial_conditions[initial_conditions == 3] = 1
            initial_conditions = initial_conditions * (
                -1)  # have to first convert to shadow states in order to apply negative
            initial_conditions[initial_conditions == 1] = 3  # sign to states, then convert back the the 1 2 3 alphabet
            initial_conditions[initial_conditions == 0] = 2
            initial_conditions[initial_conditions == -1] = 1
            i = 0
            while i < np.shape(initial_conditions)[0]:
                j = np.shape(initial_conditions)[0] - 1
                while j > i:
                    if self.check_cyclic(initial_conditions[i], double_cycles[j]) == True:
                        initial_conditions = np.delete(initial_conditions, j,
                                                       0)  # does the same process as before but for
                        double_cycles = np.delete(double_cycles, j, 0)  # the comparing the negatives of the cycles
                    j = j - 1  # to the double cycles
                i = i + 1
            initial_conditions[initial_conditions == 1] = -1
            initial_conditions[initial_conditions == 2] = 0
            initial_conditions[initial_conditions == 3] = 1
            initial_conditions = initial_conditions * (-1)
            initial_conditions[initial_conditions == 1] = 3
            initial_conditions[initial_conditions == 0] = 2
            initial_conditions[initial_conditions == -1] = 1
        if check_rev == 1:
            initial_conditions = initial_conditions[..., ::-1]
            i = 0
            while i < np.shape(initial_conditions)[0]:
                j = np.shape(initial_conditions)[0] - 1
                while j > i:
                    if self.check_cyclic(initial_conditions[i], double_cycles[j]) == True:
                        initial_conditions = np.delete(initial_conditions, j, 0)
                        double_cycles = np.delete(double_cycles, j, 0)
                    j = j - 1
                i = i + 1
        copy_of_reversed_initial = initial_conditions.copy()
        i = 0
        del_array = np.zeros(np.shape(initial_conditions)[0])
        while i < np.shape(initial_conditions)[0]:
            j = 1
            while j <= np.shape(initial_conditions)[1] - 1:
                self.rotate(copy_of_reversed_initial[i])
                if self.check_cyclic(copy_of_reversed_initial[i], initial_conditions[i]) == True:
                    del_array[i] = 1
                j = j + 1
            i = i + 1

        initial_conditions = np.delete(initial_conditions, np.where(del_array == 1), 0)
        initial_conditions[initial_conditions == 1] = -1
        initial_conditions[initial_conditions == 2] = 0
        initial_conditions[initial_conditions == 3] = 1

        return initial_conditions

    def check_cyclic(self, orbit_1, orbit_2):
        """ Checks if two cycles are members of the same group orbit
    
        A: 
    
        """
        return ', '.join(map(str, orbit_1)) in ', '.join(map(str, orbit_2))

    def rotate(self, A):
        x = A[len(A) - 1]
        for i in range(len(A) - 1, 0, -1):
            A[i] = A[i - 1]
        A[0] = x
        return A