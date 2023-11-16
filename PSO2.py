import numpy as np

# Rosenbrock function
def rosenbrock(x):
    return sum(100.0*(x[i+1]-x[i]**2.0)**2.0 + (1-x[i])**2.0 for i in range(len(x)-1))

# Particle Swarm Optimization
def pso(n_particles, iter_max, v_max, x_max, x_min, w, c1, c2):
    dim = 10  # dimension of the problem
    x = np.random.uniform(low=x_min, high=x_max, size=(n_particles, dim))  # positions of particles
    v = np.random.uniform(low=-v_max, high=v_max, size=(n_particles, dim))  # velocities of particles
    p = x.copy()  # best positions of particles
    pg = x[np.argmin([rosenbrock(x[i]) for i in range(n_particles)])]  # best position of all particles

    for _ in range(iter_max):
        r1 = np.random.rand(n_particles, dim)
        r2 = np.random.rand(n_particles, dim)
        v = w*v + c1*r1*(p-x) + c2*r2*(pg-x)
        x = x + v
        for i in range(n_particles):
            if rosenbrock(x[i]) < rosenbrock(p[i]):
                p[i] = x[i]
        pg = x[np.argmin([rosenbrock(x[i]) for i in range(n_particles)])]

    return pg, rosenbrock(pg)

# parameters
n_particles = 100
iter_max = 1000
v_max = 0.05
x_max = 2.0
x_min = -2.0
w = 0.7
c1 = 1.4
c2 = 1.4

# optimization
pg, value = pso(n_particles, iter_max, v_max, x_max, x_min, w, c1, c2)
print("Optimized parameters: ", pg)
print("Optimized value: ", value)