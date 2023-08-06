###   Pythonskole.no    Tyngdekraft    ###
###   14.12.2021  kontakt@pythonskole.no ###

import sys
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib import animation

######################
######################
### INITIALIZATION ###
######################
######################

class Tyngdekraft():
    def __init__(self,dt=0.03,L=20.0, tittel = 'Tyngdekraft', 
            kollisjoner = True, massesenter = True):
        #TODO: Add input paramteres
        # - text_ options
        # - follow
        self.tstep = 0
        self.n = 0
        self.dt = dt
        self.L = L
        self.interval=10
        self.center = np.array([0,0])
        self.midten = self.center
        self.cog = self.center
        self.title = tittel
        self.max_tstep = int(1e16)
        self.frames = 1500
        self.activate_collisions = kollisjoner
        self.text_collisions = False
        self.text_energy = False
        self.text_cog = False
        self.follow_center_of_gravity = massesenter
        #Leave these as they are
        self.exit_at_next_iteration = False
        self.anim = None
        self.video_output_file = 'tyngdekraft-'+tittel+'.mp4'

    def nyttObjekt(self,pos,vel,mass):
        datatype = np.dtype([
            ('pos', np.float64 , 2),('vel', np.float64 , 2),
            ('acc', np.float64 , 2),('force', np.float64 , 2),
            ('mass', np.float64 , 1),('size', np.float64 , 1)])
        #datatype = np.dtype([
        #    ('pos', np.float64 , (2,)),('vel', np.float64 , (2,)),
        #    ('acc', np.float64 , (2,)),('force', np.float64 , (2,)),
        #    ('mass', np.float64 , (1,)),('size', np.float64 , (1,))])
        new          = np.zeros(1,dtype=datatype) 
        new["pos"]   = pos
        new["vel"]   = vel
        new["acc"]   = np.zeros(2)
        new["force"] = np.zeros(2)
        new["mass"]  = mass
        new["size"]  = self.sizeFromMass(mass)
        if self.n > 0:
            self.obj = np.append(self.obj,new)
        else:
            self.obj = new 
        self.n = len(self.obj)
 

######################
######################
###  INTEGRATIONS  ###
######################
######################

    def calculate_forces(self):
        # Use linear algebra to calculate the forces acting 
        # between each and every planet in the simulation, 
        # using the N-body method. 
        gravity_factor = 0.1
        ones = np.ones(self.n)
        # Get mass and positions of planets
        m = self.obj["mass"][:]
        x = self.obj["pos"][:,0]
        y = self.obj["pos"][:,1]
        # Calculate discances between each particle and product of masses
        dx = np.outer(ones,x) - np.outer(x,ones)
        dy = np.outer(ones,y) - np.outer(y,ones)
        Mm = np.outer(ones,m) * np.outer(m,ones)
        #d = np.sqrt(dx**2 + dy**2)
        #np.fill_diagonal(d,np.inf)
        d2 = dx**2 + dy**2
        np.fill_diagonal(d2,np.inf)
        # Calculate gravity, angle between positions, and force components
        #f  = gravity_factor*Mm/d  #2D: 1/r
        f  = gravity_factor*Mm/d2  #3D: 1/r2
        theta = np.arctan2(dy, dx)
        fx = np.sum(f * np.cos(theta),1)
        fy = np.sum(f * np.sin(theta),1)
        #Save acceleration acting on each planet
        #self.obj["force"] = np.transpose(np.vstack((fx,fy)))
        self.obj["acc"]   = np.transpose(np.vstack((fx/m,fy/m)))

    def sizeFromMass(self,mass):
        #Scaling so that scatter-objects are in units 
        # of plot coordinates, not window size (pixels) 
        size_to_mass_ratio = 100.0/self.L**2
        return mass*size_to_mass_ratio
    
    def radiusFromSize(self,size):
        size_to_radius_ratio = 0.021  #OLD TESTED VALUE 0.016 , 0.02
        return size_to_radius_ratio*np.sqrt(size)

    def handle_collisions(self):
        ones = np.ones(self.n)
        # Get positions of all the planets
        x = self.obj["pos"][:,0]
        y = self.obj["pos"][:,1]
        # Calculate discances between each planet
        deltax = np.outer(ones,x) - np.outer(x,ones)
        deltay = np.outer(ones,y) - np.outer(y,ones)
        delta2 = deltax**2 + deltay**2
        np.fill_diagonal(delta2,np.inf)
        # Is their size larger than their distance?
        r = self.radiusFromSize(self.obj["size"][:])
        rsum2 = (np.outer(ones,r) + np.outer(r,ones))**2
        # Count all planets that has collided
        collisions = np.tril(delta2 <= rsum2)
        #print("----------------")
        #vx = self.obj["vel"][:,0]
        #vy = self.obj["vel"][:,1]
        #print("d2:",delta2)
        #print("r2:",rsum2)
        #print("vx:",vx)
        #print("vy:",vy)
        if np.sum(collisions) == 0: 
            return 

        indices = np.column_stack(np.where(collisions))
        #print("COLLISION")
        #print(" i: ",indices)
        #for ind in indices: 
        #    print("ind:",ind)
        #    for i in ind:
        #        print("i:",i)
        #        print("delta2;",delta2[i])
        #        print("rsum2:",rsum2[i])
        #        print("vx:",vx[i])
        #        print("vy:",vy[i])
        #self.exit_at_next_iteration = True
        #print("indices:",indices,self.n)
        delete = []
        for ind in indices:
            self.collide(ind)
            delete.append(ind[1])

        #Remove duplicates and sort list, from highest to lowest ID
        delete=list(dict.fromkeys(sorted(delete, reverse=True)))
        for i in delete: 
            self.obj = np.delete(self.obj,i)
        self.n = len(self.obj)
        #print("delete:",delete,self.n)

    def collide(self,ind):
        #Place the heaviest first, the second will be deleted
        if self.obj["mass"][ind[0]] <  self.obj["mass"][ind[0]]:
            ind = np.flip(ind)
        m1 = self.obj["mass"][ind[0]]
        v1 = 0.5*(2*self.obj["vel"][ind[0]]-self.obj["acc"][ind[0]]*self.dt)
        p1 = v1*m1
        m2 = self.obj["mass"][ind[1]]
        v2 = 0.5*(2*self.obj["vel"][ind[1]]-self.obj["acc"][ind[1]]*self.dt)
        p2 = v2*m2
        msum = m1+m2
        ##COLLISION DIAGNOSTICS KEPT FOR NOW
        #print("COLLIDE")
        #print(" ind:",ind)
        #print(" m1:",self.obj["mass"][ind[0]])
        #print(" v1:",self.obj["vel"][ind[0]])
        #print(" m2:",self.obj["mass"][ind[1]])
        #print(" v2:",self.obj["vel"][ind[1]])
        #print(" p1:",p1)
        #print(" p2:",p2)
        #print(" psum:",p1+p2)
        #print(" msum:",msum)
        #print(" vsum:",(p1+p2)/msum)
        #input("Pause")

        self.obj["mass"][ind[0]] = msum
        self.obj["size"][ind[0]] = self.sizeFromMass(msum)
        self.obj["vel"][ind[0],:] =  (p1+p2) / msum

    def integrate_orbits(self):
        if self.n <= 1:
            self.exit_at_next_iteration = True

        self.tstep += 1
        self.obj["vel"]=self.obj["vel"]+self.obj["acc"]*self.dt
        self.obj["pos"]=self.obj["pos"]+self.obj["vel"]*self.dt

    def update_center_of_gravity(self):
        msum = np.sum(self.obj["mass"])
        cogx = np.sum(self.obj["pos"][:,0]*self.obj["mass"])/msum
        cogy = np.sum(self.obj["pos"][:,1]*self.obj["mass"])/msum
        self.cog = np.array([cogx,cogy])



######################
######################
###  DIAGNOSTICTS  ###
######################
######################
    def print_collisions(self):

        return "No. of planets={:d}\nMass (heaviest)={:.3f}\nMass (average)={:.3f}\nMass (sum)={:.3f}".format(self.n, np.max(self.obj["mass"]),np.mean(self.obj["mass"]),np.sum(self.obj["mass"]))

    def print_cog(self):
        return "Center of gravity=({:.2f},{:.2f})".format(
                self.cog[0],self.cog[1])

    def print_energy(self):
        m   = self.obj["mass"] 
        vx2 = self.obj["vel"][:,0]**2 
        vy2 = self.obj["vel"][:,1]**2
        Ek  = np.sum(0.5*m*(vx2+vy2))
        return "Ek={:.2e}".format(Ek)

    def print_statistics(self):
        ax  = self.obj["acc"][:,0] 
        ay  = self.obj["acc"][:,1]
        vx  = self.obj["vel"][:,0] 
        vy  = self.obj["vel"][:,1]
        return "a1=({:.2e} {:.2e})  a2=({:.2e} {:.2e})\n v1=({:.2e} {:.2e})  v2=({:.2e} {:.2e})".format(ax[0],ay[0],ax[1],ay[1],vx[0],vy[0],vx[1],vy[1])

    def print_nothing(self):
        return ""


    def plot_text(self):
        text = ''
        if self.text_collisions:
            text = text + "\n" + self.print_collisions()
        if self.text_energy:
            text = text +  "\n" + self.print_energy()
        if self.text_cog:
            text = text +  "\n" + self.print_cog()
        return text



######################
######################
###    PLOTTING    ###
######################
######################

    def update_plot_objects(self):
        #Save to plot objects
        self.planets.set_offsets(self.obj["pos"])
        self.planets.set_sizes(self.obj["size"])
        self.cogmark.set_offsets(self.cog)
        self.text.set_text(self.plot_text())
        if self.follow_center_of_gravity:
            drift = self.cog-self.center
            self.center = self.cog
            self.ax.set_xlim(self.ax.get_xlim()+drift[0])
            self.ax.set_ylim(self.ax.get_ylim()+drift[1])
            self.text.position= [self.center[0]-self.L,self.center[1]-self.L]


    def clean_exit(self):
        self.anim.save(self.video_output_file)
        input("SIMULATION STOPPED! Press to exit")
        sys.exit(0)



    def update(self,frame_number):
        if self.exit_at_next_iteration or self.tstep > self.max_tstep:
            self.clean_exit()
        if self.activate_collisions:
            self.handle_collisions()  
        self.calculate_forces()
        self.integrate_orbits()
        self.update_center_of_gravity()
        self.update_plot_objects()
        print("Frame="+str(frame_number)+"               ", end='\r')
        sys.stdout.flush()
        return self.planets,self.text,self.cogmark,

    def start(self):
        self.update_center_of_gravity()

        # Update velocities with a half time shift (LeapFrog Method)
        self.calculate_forces()
        self.obj["vel"]=self.obj["vel"]-self.obj["acc"]*self.dt/2.
        
        #Lag plott-vindu
        self.fig = plt.figure(figsize=(7,7))
        self.ax = plt.axes(xlim=(-self.L,self.L),ylim=(-self.L,self.L))

        #Opprett plotte-objekter
        self.ax.set_title("Tyngdekraft (pythonskole.no)\n"+self.title)
        self.text = self.ax.text(-self.L+0.5,-self.L+0.5,'')
        self.cogmark = self.ax.scatter(self.cog[0],self.cog[1],
                marker='x',c='red')
        self.planets = self.ax.scatter(self.obj["pos"][:,0], 
                self.obj["pos"][:,1], s=self.obj["size"])

        #Start animasjon
        self.anim = animation.FuncAnimation(self.fig, self.update, 
                interval=self.interval,repeat=False)
        #self.anim = animation.FuncAnimation(self.fig, self.update, 
        #        interval=self.interval,frames=self.frames,
        #        save_count=self.frames,repeat=False)
        plt.show() 

        #print("")
        #print("")
        #print("Wait... saving to video file")
        #self.anim.save(self.video_output_file)

