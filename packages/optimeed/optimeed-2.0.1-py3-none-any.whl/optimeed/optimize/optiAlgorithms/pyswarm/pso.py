import numpy as np
from multiprocessing import Pool
import time


def _is_feasible(theList):
    return np.all(np.array(theList) <= 0)


def _format_fx_fs(objectives_pop, constraints_pop):
    fx = np.zeros(len(objectives_pop))
    fs = np.zeros(len(constraints_pop), dtype=bool)
    for i in range(len(fx)):
        fx[i] = objectives_pop[i][0]
        fs[i] = _is_feasible(constraints_pop[i])
    return fx, fs


class MyMapEvaluator:
    def __init__(self, evaluation_function, callback_on_evaluation):
        self.callback_on_evaluation = callback_on_evaluation
        self.evaluation_function = evaluation_function

    def evaluate_all(self, x):
        objectives_pop = [None]*len(x)
        constraints_pop = [None]*len(x)

        for k, xi in enumerate(x):
            returned_value = self.evaluation_function(xi)
            self.callback_on_evaluation(returned_value)

            objectives_pop[k] = returned_value["objectives"]
            constraints_pop[k] = returned_value["constraints"]
        return objectives_pop, constraints_pop


class MyMultiprocessEvaluator:
    def __init__(self, evaluation_function, callback_on_evaluation, numberOfCores):
        self.callback_on_evaluation = callback_on_evaluation
        self.evaluation_function = evaluation_function
        self.pool = Pool(numberOfCores)

    def evaluate_all(self, x):
        objectives_pop = [None]*len(x)
        constraints_pop = [None]*len(x)
        for k, returned_value in enumerate(self.pool.imap_unordered(self.evaluation_function, x)):
            self.callback_on_evaluation(returned_value)
            objectives_pop[k] = returned_value["objectives"]
            constraints_pop[k] = returned_value["constraints"]
        return objectives_pop, constraints_pop


def pso(lb, ub, initialVectorGuess, theEvaluator, maxtime, callback_generation=lambda objectives, constraints: None, swarmsize=100, omega=0.5, phip=0.5, phig=0.5):
    """
    Perform a particle swarm optimization (PSO)

    Parameters
    ==========
    lb: list
        Lower bounds of each parameter
    ub: list
        upper bounds of each parameter
    initialVectorGuess: list
        initial vector guess for the solution (to be included inside population)
    theEvaluator : object define before
    maxtime : float
        The maximum time (in s) before stopping the algorithm
    callback_generation: function lambda (bjectives (as list), constraints (as list)) per step
        Useful to log convergence
    swarmsize : int
        The number of particles in the swarm (Default: 100)
    omega : scalar
        Particle velocity scaling factor (Default: 0.5)
    phip : scalar
        Scaling factor to search away from the particle's best known position
        (Default: 0.5)
    phig : scalar
        Scaling factor to search away from the swarm's best known position
        (Default: 0.5)

    Returns
    =======
    g : array
        The swarm's best known position (optimal design)
    f : scalar
        The objective value at ``g``
    """
    lb = np.array(lb)
    ub = np.array(ub)

    vhigh = np.abs(ub - lb)
    vlow = -vhigh

    # Initialize the particle swarm ############################################
    S = swarmsize
    D = len(lb)  # the number of dimensions each particle has
    x = np.random.rand(S, D)  # particle positions
    # v = np.zeros_like(x)  # particle velocities
    p = np.zeros_like(x)  # best particle positions
    # fx = np.zeros(S)  # current particle function values
    # fs = np.zeros(S, dtype=bool)  # feasibility of each particle
    fp = np.ones(S)*np.inf  # best particle function values
    # g = []  # best swarm position
    fg = np.inf  # best swarm position starting value
    fsg = True

    # Initialize the particle's position
    x = lb + x*(ub - lb)

    x[0, :] = initialVectorGuess[:]  # inserted initial guess in population

    # Calculate objective and constraints for each particle
    obj, cons = theEvaluator.evaluate_all(x)
    fx, fs = _format_fx_fs(obj, cons)

    # Store particle's best position (if constraints are satisfied)
    i_update = np.logical_and((fx < fp), fs)
    p[i_update, :] = x[i_update, :].copy()
    fp[i_update] = fx[i_update]

    # Update swarm's best position
    i_min = np.argmin(fp)
    if fp[i_min] < fg:
        fg = fp[i_min]
        g = p[i_min, :].copy()
    else:
        # At the start, there may not be any feasible starting point, so just
        # give it a temporary "best" point since it's likely to change
        g = x[0, :].copy()

    # Initialize the particle's velocity
    v = vlow + np.random.rand(S, D)*(vhigh - vlow)

    # Iterate until termination criterion met ##################################

    start = time.time()
    while (time.time() - start) <= maxtime:
        rp = np.random.uniform(size=(S, D))
        rg = np.random.uniform(size=(S, D))

        # Update the particles velocities
        v = omega*v + phip*rp*(p - x) + phig*rg*(g - x)
        # Update the particles' positions
        x = x + v
        # Correct for bound violations
        maskl = x < lb
        masku = x > ub
        x = x*(~np.logical_or(maskl, masku)) + lb*maskl + ub*masku

        # Update objectives and constraints
        obj, cons = theEvaluator.evaluate_all(x)
        fx, fs = _format_fx_fs(obj, cons)

        callback_generation(obj, cons)
        # Store particle's best position (if constraints are satisfied)
        i_update = np.logical_and((fx < fp), fs)
        p[i_update, :] = x[i_update, :].copy()
        fp[i_update] = fx[i_update]

        # Compare swarm's best position with global best position
        i_min = np.argmin(fp)
        if fp[i_min] < fg:
            p_min = p[i_min, :].copy()
            g = p_min.copy()
            fg = fp[i_min]
            fsg = fs[i_min]

    return g, fg, fsg
