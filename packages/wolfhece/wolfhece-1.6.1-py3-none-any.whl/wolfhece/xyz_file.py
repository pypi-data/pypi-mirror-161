# Fichier xyz
import numpy as np
import matplotlib.pyplot as plt

from .PyTranslate import _

class XYZFile:
    """ Classe pour la gestion des fichiers xyz """
    nblines:int
    x:np.array
    y:np.array
    z:np.array
    filename:str

    def __init__(self, fname):
        """ Initialisation du nom du fichier """
        self.filename = fname

    def read_from_file(self):
        """ Lecture d'un fichier xyz et remplissage de l'objet """
        with open(self.filename, 'r') as f:
            self.nblines = sum(1 for line in f)
            self.x = np.zeros(self.nblines)
            self.y = np.zeros(self.nblines)
            self.z = np.zeros(self.nblines)
            f.seek(0)
            self.nblines = 0
            for line in f:
                tmp = line.split()
                if tmp:
                    if is_float(tmp[0]):
                        self.x[self.nblines] = float(tmp[0])
                        self.y[self.nblines] = float(tmp[1])
                        self.z[self.nblines] = float(tmp[2])
                        self.nblines += 1

    def fill_from_wolf_array(self, myarray,nullvalue=0.):
        """ Création d'un fichier xyz depuis les données d'un WOLF array """
        self.nblines = myarray.nbx * myarray.nby
        self.x = np.zeros(self.nblines)
        self.y = np.zeros(self.nblines)
        self.z = np.zeros(self.nblines)
        self.nblines = 0
        for cury in range(myarray.nby):
            y = cury * myarray.dy + 0.5 * myarray.dy + myarray.origy + myarray.transly
            for curx in range(myarray.nbx):
                z = myarray.array[curx, cury]
                if z != nullvalue:
                    x = curx * myarray.dx + 0.5 * myarray.dx + myarray.origx + myarray.translx
                    self.x[self.nblines] = x
                    self.y[self.nblines] = y
                    self.z[self.nblines] = z
                    self.nblines += 1

    def write_to_file(self):
        """ Ecriture des informations dans un fichier """
        with open(self.filename, 'w') as f:
            for i in range(self.nblines):
                f.write('{:.3f}\t{:.3f}\t{:.3f}\n'.format(self.x[i], self.y[i], self.z[i], 1))

    def get_extent(self):
        """ Retourne les limites du rectangle qui encadre le nuage de points """
        xlim = [min(self.x[0:self.nblines-1]), max(self.x[0:self.nblines-1])]
        ylim = [min(self.y[0:self.nblines-1]), max(self.y[0:self.nblines-1])]
        return (xlim, ylim)

    def merge(self, xyz_list):
        """ Merge des fichiers xyz en 1 seul """
        for cur_xyz in xyz_list:
            self.nblines += cur_xyz.nblines

        self.x = np.zeros(self.nblines)
        self.y = np.zeros(self.nblines)
        self.z = np.zeros(self.nblines)

        self.nblines = 0
        for cur_xyz in xyz_list:
            self.x[self.nblines:self.nblines + cur_xyz.nblines] = cur_xyz.x[0:cur_xyz.nblines]
            self.y[self.nblines:self.nblines + cur_xyz.nblines] = cur_xyz.y[0:cur_xyz.nblines]
            self.z[self.nblines:self.nblines + cur_xyz.nblines] = cur_xyz.z[0:cur_xyz.nblines]
            self.nblines += cur_xyz.nblines

    def plot(self):
        """ Représentation graphique des points """
        plt.scatter(self.x, self.y, c=self.z, marker='.', cmap='viridis', edgecolors='none')
        plt.xlabel('x [m]')
        plt.ylabel('y [m]')
        plt.colorbar()
        plt.axis('equal')
        plt.savefig('figure.png',dpi=300)
        plt.ion()
        plt.show()
        plt.pause(0.1)


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
