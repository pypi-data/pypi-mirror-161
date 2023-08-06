import numpy as np
from scipy.optimize import minimize
from scipy.linalg import eig
from ..core import CycleEquation

__all__ = ['PhiK']


class PhiK(CycleEquation):

    def __init__(self, n, k, musqr, states=None, basis='symbolic', **kwargs):
        """
        :param n: int
            Cycle length
        :param k: int
            potential exponent
        :param musqr: float
            In this implementation of PhiK, this is mu squared. Naming is simply a convention
        :param states: np.ndarray
            NumPy array of states; array of shape (M, N) indicates that there are M different cycles of length N which
            are of interest to the user. 
        :param basis: str
            The basis of the values of the states array; used as a means of tracking the types of values in the states
            array. 
            
        Notes
        -----
        'string' basis implies that all values equal one of the following: ['1', '2', '3'] or ['-1', '0', '1']  
        
        'symbolic' basis implies that all values equal one of the following: [-1, 0, 1]  
        
        'proxy' basis implies that all values equal one of the following: [1, 2, 3]   
        
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
        """ Calculate Phi-K equations (euler-lagrange thereof) for all (approximate) states defined in 'states' attribute.

        Notes
        -----
        If there is only one state in the states attribute, this is equivalent to evaluating the E-L equations for a
        single state. Else it is equivalent to computing the equations for multiple states simultaneously. This allows
        for solving for a large number of converged cycles simultaneously.


        """
        s = self.s
        # E-L equations take a derivative so k -> k - 1
        k_minus_1 = self.k - 1
        states_tensor = self.states
        # the E-L equations
        eqn_tensor = (-1 * np.roll(states_tensor, -1, axis=1) + (-1 * (s - 2) * states_tensor ** k_minus_1 +
                                                                 s * states_tensor) - np.roll(states_tensor, 1, axis=1))
        # the l2 norm, giving us a scalar cost functional
        return eqn_tensor

    def cost(self):
        """ Default cost function; L2 norm of equations evaluated at every state in 'states' tensor.

        Notes
        -----
        Technically couples cycle precision to each other and so if precision is really important, cycles should be
        solved for one at a time (I recommended in parallel) instead of simultaneously

        """
        return (0.5 * np.linalg.norm(self.eqn(), axis=1) ** 2).sum()

    def costgrad(self):
        """ Gradient of default cost function with respect to states 1/2 f^2 --> J^T f

        """
        # s parameter used but the same as mu squared + 2
        s = self.s
        # The states
        states = self.states
        # The evaluation of E-L equations for every state
        Ftensor = self.eqn()
        # matrix-vector product of F with jacobian transpose
        JTF = -np.roll(Ftensor, 1, axis=1) - np.roll(Ftensor, -1, axis=1) + (
                -3 * (s - 2) * states ** 2 + s) * Ftensor
        return JTF.ravel()

    def jac_tensor(self, states=None):
        """ Calculate all Jacobians for all current states

        """
        n, k_minus_1 = self.n, self.k - 1
        if states is None:
            states = self.states
        number_of_states = len(states)
        # Each state
        J = np.zeros([number_of_states, n, n])
        # shift operators can be represented as first sub/super diagonals (with respective signs as well).
        # This gets the array INDICES (positions) for these elements.
        upper_rows, upper_cols = self._kth_diag_indices(J[0], -1)
        lower_rows, lower_cols = self._kth_diag_indices(J[0], 1)

        # Again, we are generating repeats of the indices for the matrix element positions so that we can simply
        # assign values of the respective matrix elements for all cycles simultaneously.
        zeroth = np.repeat(np.arange(number_of_states), len(upper_rows))
        upper_rows = np.tile(upper_rows, number_of_states)
        upper_cols = np.tile(upper_cols, number_of_states)
        lower_rows = np.tile(lower_rows, number_of_states)
        lower_cols = np.tile(lower_cols, number_of_states)

        # Finally we can assign the signed values to produce a 3rd rank tensor which is comprised of all jacobians
        # stacked together. This handles the shifted terms
        J[zeroth, upper_rows, upper_cols] = -1
        J[zeroth, lower_rows, lower_cols] = -1
        J[:, 0, -1] = -1
        J[:, -1, 0] = -1

        # The same assignment of values for the diagonal terms; values are slightly more complicated but it
        # follows the same logic as before.
        tensor_diagonal = (-3 * (self.s - 2) * states ** 2 + self.s).ravel()
        rows, cols = np.diag_indices(n)
        zeroth = np.repeat(np.arange(number_of_states), len(rows))
        J[zeroth, np.tile(rows, number_of_states), np.tile(cols, number_of_states)] = tensor_diagonal
        return J

    def _kth_diag_indices(self, a, k):
        """ Helper function to get the indices for sub/super diagonals.

        :param a: (N, N) dimensional np.ndarray
        :param k: index for sub/super diagonal; i.e. plus or minus 1 gives first sub or super diagonal
        :return:
        """
        rows, cols = np.diag_indices_from(a)
        if k < 0:
            return rows[-k:], cols[:k]
        elif k > 0:
            return rows[:-k], cols[k:]
        else:
            return rows, cols

    def n_cycle_everything(self, compute_eig=False):
        """ Function which takes in a set of initial condition states, attempts to converge them and return their
        respective Jacobian matrices; also potentially the eigenvalues and eigenvectors thereof if corresponding flag
        is True
        
        
        :param compute_eig: bool
            If True, will return eigenvalues and eigenvectors of each cycle Jacobian
        :return: tuple
            Tuple which contains minimization algorithm outputs, jacobians and potentially eigenvalues and eigenvectors
        
        """
        converged_cycles = self.hunt().states
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
            return converged_cycles, n_jacobians, all_eig_val, all_eig_vec, 
        else:
            return converged_cycles, n_jacobians, None, None 

    def generate_states(self, prime=True, sort=False):
        """ Produces all possible combinations of k-ary alphabet, puts them in tensor of shape (k**n, n)

        :return: self
            Self with newly generated states. 
        """

        self.states = np.concatenate([coord.ravel().reshape(-1, 1) for coord in np.meshgrid(*(self.symbols for i in
                                                                                              range(self.n)))],
                                     axis=1)
        return self

    def hunt(self, method='l-bfgs-b', scipy_options=None):
        """ A convenience wrapper for calling scipy.optimize.minimize
        
        :param method: str
            The name of a numerical algorithm provided by 'minimize'   
        :param scipy_options: None or dict
            Dictionary or None (default) the options/hyperparameters of the particular scipy algorithm defined by 'method'
            
        :return: 
        """
        cycles = minimize(self.costwrapper(), self.states, jac=self.costgradwrapper(), method=method,
                          options=scipy_options)
        cycle_tensor = cycles.x.reshape(-1, self.n)
        return self.__class__(**{**vars(self), 'states': cycle_tensor})

    def costwrapper(self):
        """ Wraps the cost function and returns the wrapper

        :return: _minfunc: function
            The function which when called returns the gradient of the cost functional. 
        
        Notes
        -----
        Why do this? Because SciPy optimization routines take a function (i.e. callable) as the argument. 
        
        """

        def _minfunc(x):
            return self.__class__(self.n, self.k, self.musqr, states=x.reshape(-1, self.n)).cost()

        return _minfunc

    def costgradwrapper(self):
        """ Wraps the gradient of the cost function and returns the wrapper
        
        :return: _minjac: function
            The function which when called returns the gradient of the cost functional. 
        
        
        Notes
        -----
        Why do this? Because SciPy optimization routines take a function (i.e. callable) as the argument for the jac
        parameter which defines the gradient of scalar cost functionals. 
        """

        def _minjac(x):
            return self.__class__(self.n, self.k, self.musqr, states=x.reshape(-1, self.n)).costgrad()

        return _minjac

    def change_basis(self, to=None):
        """ Convenience function used to map between different sets of values; string and both integer types.   


        :param to: str
            Takes values 'string', 'symbolic', 'proxy'. If 'string' then the values of the states array is mapped to strings,
            if symbolic then values [-1, 0, 1] else proxy maps to [1,2,3]
        :return:
        """
        if to is None or self.basis == to:
            return self.states
        elif to == 'string':
            # cast as strings of length 2 because of negative sign
            return self.states.astype('|S2')
        elif to == 'symbolic':
            self.states = self.states.astype(int)
            if -1 in self.states:
                return self.states
            else:
                return self.states - 2
        elif to == 'proxy':
            self.states = self.states.astype(int)
            if -1 in self.states:
                return self.states + 2
            else:
                return self.states

    def _check_cyclic(self, cycle_1, cycle_2):
        """ Checks if two cycles are members of the same group cycle

        """
        return ', '.join(map(str, cycle_1)) in ', '.join(map(str, cycle_2))

    def prime_cycles(self, check_neg=False, check_rev=False):
        """ Removes all cycles which are either cyclic permutations or repeats. Quotients further symmetries if specified

        :param check_neg: bool
            If True then removes all cycles with sign change symmetry

        :param check_rev: bool
            If True then removes all cycles with time reversal symmetry

        :return: self
            Returns the PhiK instance with states having been changed inplace.
        """
        initial_conditions = self.states
        # initial conditions should be you entire list of possible shadow state configurations
        # check_neg is a value that takes either 1 or 0 where if it is 1, it will check for phi to negative phi symmetry
        initial_conditions[initial_conditions == 1] = 3
        initial_conditions[initial_conditions == 0] = 2
        initial_conditions[initial_conditions == -1] = 1
        # here i am just changing my shadow state values to a different symbolic alphabet that will work better
        double_cycles = np.append(initial_conditions, initial_conditions, axis=1)
        # double_cycles is each shadow state repeated so that it is twice its length. This is used show checking for cyclic
        # permutations as every permunation exists in the cycle as if it goes through it twice. Ex: all cyclic permutation of 123
        # exist somwhere in 123123
        i = 0
        while i < np.shape(initial_conditions)[0]:  # looping through each row of the initial conditions
            j = np.shape(initial_conditions)[0] - 1
            while j > i:  # looping rows of double_cycles, starting at the bottomw and ending before the row of the current
                # cycle we are checking
                if self._check_cyclic(initial_conditions[i], double_cycles[j]) == True:
                    initial_conditions = np.delete(initial_conditions, j, 0)
                    double_cycles = np.delete(double_cycles, j,
                                              0)  # if a cycle string exists in the double_cycle of of another
                j = j - 1  # cycle, delete one of the cycles
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
                    if self._check_cyclic(initial_conditions[i], double_cycles[j]) == True:
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
                    if self._check_cyclic(initial_conditions[i], double_cycles[j]) == True:
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
                self._rotate(copy_of_reversed_initial[i])
                if self._check_cyclic(copy_of_reversed_initial[i], initial_conditions[i]) == True:
                    del_array[i] = 1
                j = j + 1
            i = i + 1

        initial_conditions = np.delete(initial_conditions, np.where(del_array == 1), 0)
        initial_conditions[initial_conditions == 1] = -1
        initial_conditions[initial_conditions == 2] = 0
        initial_conditions[initial_conditions == 3] = 1
        self.states = initial_conditions
        return self

    def _rotate(self, a):
        x = a[len(a) - 1]
        for i in range(len(a) - 1, 0, -1):
            a[i] = a[i - 1]
        a[0] = x
        return a