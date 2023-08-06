
import numpy as np
import gravbody.barnes_hut as bh
import gravbody.physics_helper as ph
import time

class NBody:
    def __init__(self, pos, vel, mass, G, barnes_hut=True, use_collisions=False,
                 softening=0, particle_radius=None):
        '''Implementation of an n-body system
        
        pos and vel are stored as an N x 3 matrix
        mass is a 1-dimensional numpy array'''
        
        self.numParticles = pos.shape[0]
        self.pos = pos
        self.velocity = vel
        self.mass = mass
        self.G = G
        self.barnes_hut = barnes_hut
        self.use_collisions = use_collisions
        self.softening = softening
        self.particle_radius = particle_radius
        
        self.oldAccel = np.zeros(3)
        self.justCollided = [False for i in range(self.numParticles)]
    
    @classmethod
    def FromFile(cls, path, *args, **kwargs):
        '''Reads in a space separated file of particle data
        Format should be: [posX] [posY] [posZ] [velX] [velY] [velZ] [mass] on every line'''
        
        data = np.loadtxt(path)
        pos = data[:, :3]
        vel = data[:, 3:6]
        mass = data[:, 6].reshape(data.shape[0])
        
        return cls(pos, vel, mass, *args, **kwargs)
    
    def leapfrogKickDrift(self, t):
        self.velocity += self.oldAccel * (t/2)
        self.pos += self.velocity * t
        
    def leapfrogFinalKick(self, newAccel, t):
        self.velocity += newAccel * (t / 2)
        self.oldAccel = newAccel
    
    def naive_step(self, t):
        '''Basic O(n^2) method to update particle motion'''
        
        self.leapfrogKickDrift(t)
        
        accel = np.zeros((self.numParticles, 3))
        newVelocities = np.array(self.velocity)
        for i in range(self.numParticles):
            for j in range(self.numParticles):
                if i != j: 
                    # find the difference between the two particles' positions
                    diff = self.pos[j] - self.pos[i]
    
                    # calculate the distance based on the vector between them
                    distSquared = np.sum(diff ** 2) + self.softening**2

                    accel[i] += self.G * self.mass[j] * diff / (distSquared ** 1.5)
        
        self.leapfrogFinalKick(accel, t)
        
        
        # Handle Collisions
        if self.use_collisions: 
            experiencedCollision = [False for i in range(self.numParticles)]
            newVelocities = np.array(self.velocity)
            for i in range(self.numParticles):
                for j in range(self.numParticles):
                    if i != j:
                        dist = ph.dist(self.pos[i], self.pos[j])
                        collided = dist < 2 * self.particle_radius
                        if collided and not self.justCollided[i]:
                            newVel = ph.elastic_collision(self.pos[i], self.velocity[i], self.mass[i],
                                                          self.pos[j], self.velocity[j], self.mass[j])[0]
                            newVelocities[i] = newVel
                        
                        if collided:
                            experiencedCollision[i] = True
                            break
                        
            self.justCollided = experiencedCollision
            self.velocity = newVelocities
    
    def naive_vectorized_step(self, t):
        
        ### INSPIRED BY https://medium.com/swlh/create-your-own-n-body-simulation-with-python-f417234885e9
        
        self.leapfrogKickDrift(t)
        
        x = self.pos[:,0:1]
        y = self.pos[:,1:2]
        z = self.pos[:,2:3]
        
        # matrix that stores all pairwise particle separations: r_j - r_i
        dx = x.T - x
        dy = y.T - y
        dz = z.T - z
        
        # matrix that stores 1/r^3 for all particle pairwise particle separations 
        distSquared = dx**2 + dy**2 + dz**2 + self.softening**2
        inv_r3 = np.power(distSquared, -1.5, out=np.zeros_like(distSquared), where=distSquared!=0)
        ax = self.G * (dx * inv_r3) @ self.mass
        ay = self.G * (dy * inv_r3) @ self.mass
        az = self.G * (dz * inv_r3) @ self.mass
        
        # pack together the acceleration components
        accel = np.stack((ax, ay, az), axis=1)
        self.leapfrogFinalKick(accel, t)
        
        if self.use_collisions: 
            experiencedCollision = [False for i in range(self.numParticles)]
            newVelocities = np.array(self.velocity)
            for i in range(self.numParticles):
                for j in range(self.numParticles):
                    if i != j:
                        dist = ph.dist(self.pos[i], self.pos[j])
                        collided = dist < 2 * self.particle_radius
                        if collided and not self.justCollided[i]:
                            newVel = ph.elastic_collision(self.pos[i], self.velocity[i], self.mass[i],
                                                          self.pos[j], self.velocity[j], self.mass[j])[0]
                            newVelocities[i] = newVel
                        
                        if collided:
                            experiencedCollision[i] = True
                            break
                        
            self.justCollided = experiencedCollision
            self.velocity = newVelocities
    
    def barnes_hut_step(self, t):
        '''Barnes-Hut Algorithm Implementation'''
        
        self.leapfrogKickDrift(t)
        
        # set tree size based on the maximum dist from center of mass to any particle
        com = ph.centerOfMass(self.mass, self.pos)
        maxDist = np.sqrt(np.max(np.sum((self.pos - com) ** 2, 1))) + 1
            
        # Create the tree structure
        root = bh.BarnesHutNode(com, maxDist)
        for i in range(self.numParticles):
            root.insert(self.pos[i], self.mass[i], self.velocity[i])
            
        # Calculate accelerations for each particle
        accel = np.zeros((self.numParticles, 3))
        for i in range(self.numParticles):
            accel[i] = self.G * bh.calcAcceleration(self.pos[i], self.mass[i], root, 1, self.softening)
        self.leapfrogFinalKick(accel, t)
        
        # Handle collisions
        if self.use_collisions:
            experiencedCollision = [False for i in range(self.numParticles)]
            newVelocities = np.array(self.velocity)
            for i in range(self.numParticles):
                newVel = bh.handle_elastic_collisions(self.pos[i], self.velocity[i], self.mass[i], root, 0.5, self.particle_radius)
                collided = (newVel != self.velocity[i]).any()
                if collided and not self.justCollided[i]:
                    newVelocities[i] = newVel
                    
                if collided:
                    experiencedCollision[i] = True
                
            self.justCollided = experiencedCollision
            self.velocity = newVelocities
        
    def advanceSimulation(self, t):
        if self.barnes_hut:
            self.barnes_hut_step(t)
        else:
            self.naive_vectorized_step(t)
    
    def save(self, t, path, numFrames, numFramesPerNotification=None, saveEvery=1):
        '''Saves data from nbody model into animation frame files to be played back later'''
        
        # store the timestep and mass in a data file since they are the same for
        # each frame
        with open(path + '/' + 'data.npy', 'wb') as f:
            data = np.concatenate((np.array([t * saveEvery]), self.mass))
            np.save(f, data)
        
        t1 = time.time()
        start = t1
        for i in range(numFrames):
            with open(path + '/' + str(i) + '.npy', 'wb') as f:
                # combine position and velocity into a single array and save it
                data = np.concatenate((self.pos, self.velocity), axis=1)
                np.save(f, data)
            
            # skip over frames that we aren't saving
            for j in range(saveEvery):
                self.advanceSimulation(t)
            
            # print an update every few frames
            if numFramesPerNotification is not None:
                if (i + 1) % numFramesPerNotification == 0:
                    t2 = time.time()
                    print("Completed", i + 1, "frames!        Time per frame: %.2f s" %
                          ((t2 - t1) / numFramesPerNotification))
                    t1 = time.time()
                
        end = time.time()        
        print("Simulation complete!")
        print("Generated", numFrames, "frames in %.2f seconds" % (end - start))
    
    def calc_energy(self):
        '''Calculates the total energy of the current state of the n body system'''
        
        KE = 0
        PE = 0
        for i in range(self.numParticles):
            KE += 0.5 * self.mass[i] * np.sum((self.velocity[i]) ** 2)
            for j in range(self.numParticles):
                if i != j:
                    PE -= self.G * self.mass[i] * self.mass[j] / np.sqrt(np.sum((self.pos[i] - self.pos[j]) ** 2))
        # print(KE, PE, end="\t")
        PE /= 2
        
        return KE + PE