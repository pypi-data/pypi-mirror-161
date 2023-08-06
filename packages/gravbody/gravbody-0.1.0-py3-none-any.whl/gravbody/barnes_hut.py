
import numpy as np
import gravbody.physics_helper as ph

class BarnesHutNode:
    def __init__(self, center, width):
        '''Barnes-Hut Tree Node Implementation
        
        Center: Position in space that the cube-shaped node is centered on
        Width: Node size
        '''
        self.spatialCenter = center # center of the node (cube-shaped) in space
        self.width = width 
        
        # the center of mass of all particles contained in this node
        self.centerMass = np.zeros(3)
        
        # total mass of particles in this node
        self.totalMass = 0 
        
        self.children = {} 
        self.isLeaf = True # boolean representing if this node has children
        self.velocity = np.zeros(3) # used for collisions; only used when node contains a single particle

    def insert(self, particle_pos, particle_mass, particle_vel):
        '''Inserts a particle into this node based on it's location'''
        
        # if this node doesn't have any particles in it
        if self.isLeaf and self.totalMass == 0:
            # add particle mass to node's mass
            self.updateMass(particle_pos, particle_mass)
            
            # store the particle's velocity (for collisions)
            self.velocity = particle_vel 

        elif not self.isLeaf: # if this node has children
            # add particle mass to node's mass
            self.updateMass(particle_pos, particle_mass)
            
            self.insertInAppropriateChild(particle_pos, particle_mass, particle_vel)

        else: # if this node currently contains only one particle

            # split this node up and assign particles to sub-nodes
            self.insertInAppropriateChild(self.centerMass, self.totalMass, self.velocity)
            self.insertInAppropriateChild(particle_pos, particle_mass, particle_vel)
            
            # add particle mass to node's mass
            self.updateMass(particle_pos, particle_mass)
            
            # this node isn't a leaf anymore, so remove leaf properties
            self.isLeaf = False
            self.velocity = np.zeros(3)
            

    def insertInAppropriateChild(self, particle_pos, particle_mass, particle_vel):
        '''Inserts a node into the appropriate child node based on its position relative to the center of the node'''
        
        # Childname is in the format '[x dir][y dir][z dir]' where each [dir] is a + or - based 
        # on where the particle is relative to the node's center
        #
        # Ex: +++ means that the particle belongs in the child node that has a larger x, y, and z coord
        # relative to the current node's center
        
        diff = particle_pos - self.spatialCenter
        childName =  "+" if (diff[0] > 0) else "-"
        childName += "+" if (diff[1] > 0) else "-"
        childName += "+" if (diff[2] > 0) else "-"
        
        
        # if the node that this particle belongs to is empty (thus not yet created)
        if childName not in self.children.keys():
            # get absolute values from diff vector
            # replace 0s with 1s to avoid divide by 0 errors 
            absDiff = np.abs(diff)
            absDiff[0] = 1 if absDiff[0] == 0 else absDiff[0]
            absDiff[1] = 1 if absDiff[1] == 0 else absDiff[1]
            absDiff[2] = 1 if absDiff[2] == 0 else absDiff[2]
            
            # create a vector storing just the signs (+1, -1) of the diff vector
            signs = diff / absDiff
            
            # if the particle is directly on the center of the node, default to the --- node
            # (arbitrary choice)
            if np.isclose(particle_pos, self.spatialCenter).all():
                signs = -np.ones_like(signs)
                
            # create the node and store it in the children dictionary
            childCenter = signs * self.width / 4 + self.spatialCenter
            self.children[childName] = BarnesHutNode(childCenter, self.width/2)

        # insert the particle in the appropriate child node
        self.children[childName].insert(particle_pos, particle_mass, particle_vel)
    
    def updateMass(self, particle_pos, particle_mass):
        '''Updates the total mass and center of mass of this node after a
        particle has been inserted'''
        
        newTotalMass = self.totalMass + particle_mass
        self.centerMass = (self.centerMass * self.totalMass + particle_pos * particle_mass) / newTotalMass
        self.totalMass = newTotalMass
    
def calcAcceleration(particle, mass, node, threshold, softening=3):
    '''Calculate the net acceleration on a particle based on the Barnes-Hut algorithm
    
    Threshold: value used to determine when a particles are sufficiently far away
    Softening: Value used to reduce the impact of forces when particles get close'''
    accel = np.zeros(3)
    diff = node.centerMass - particle
    distSquared = np.dot(diff, diff) + (softening ** 2)
    if node.isLeaf: # if the node only has one particle
        if not np.isclose(node.centerMass, particle).all():
            accel += node.totalMass * diff / (distSquared ** 1.5)
    else: # if the node contains multiple particles
        if distSquared == 0:
            sd_ratio = threshold + 1
        else:
            sd_ratio = node.width / np.sqrt(distSquared)
            
        if sd_ratio < threshold:
            # if the node is far away, treat all the particles within it as a single mass at its center
            
            accel += node.totalMass * diff / (distSquared ** 1.5)
        else: # if the node is nearby
            # Visit each childnode and determine its effects on this particle
            for child in node.children.values():
                accel += calcAcceleration(particle, mass, child, threshold, softening)
    return accel

def handle_elastic_collisions(particle, vel, mass, node, threshold, radius=5):
    '''Causes particles to bounce off of each other when they get close while
    conserving kinetic energy.
    
    Returns new velocity of the given particle'''

    ### TODO
    ### Double check that this algorithm works
    ### There may be cases where the threshold isn't met even though a collision should happen
    
    dist = ph.dist(node.centerMass, particle)
    if node.isLeaf: # if the node only has one particle
        if not np.isclose(node.centerMass, particle).all():
            if dist < 2 * radius:
                v = ph.elastic_collision(particle, vel, mass, node.centerMass,
                                         node.velocity, node.totalMass)
                return v[0]
    else: # if the node contains multiple particles
        if dist == 0:
            sd_ratio = threshold + 1 # make sure to meet the threshold, since we are very close
        else:
            sd_ratio = node.width / dist
            
        if sd_ratio < threshold:
            # if the node is far away, we can't collide with it
            return vel
        else: # if the node is nearby
            for child in node.children.values():
                # check if we collide with any child nodes
                v = handle_elastic_collisions(particle, vel, mass, child, threshold, radius)
                if (v != vel).any():
                    return v
    
    return vel
