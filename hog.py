import numpy as np
import cv2


class Hog:
    # Works for 96X160 images
    # Private variables for Hog
    __bin_n = 16  # Number of bins

    # histogram
    __hist = []

    __ahist = 0

    def hog_show(self):
        # only works for 96x1609
        cols, rows, bins = self.__ahist.shape
        print rows, cols
        img = np.zeros((rows*8, cols*8))
        print img.shape
        for i in range(0, cols-1):
            for j in range(0, rows-1):
                # get the angles
                angle_weights = self.__ahist[i][j][:]
                # print angle_weights

                # draw the line
                angle = 0
                x = (1, 4)
                y = (7, 4)
                cell = np.zeros((8, 8))
                for angle_weight in angle_weights:
                    myline = np.zeros((8, 8))
                    cv2.line(myline, x, y, (angle_weight, 0, 0), 1)
                    M = cv2.getRotationMatrix2D((4, 4), angle, 1)
                    myline = cv2.warpAffine(myline, M, (8, 8))
                    cell[cell < myline] = myline[cell < myline]
                    # img[j*8:(j+1)*8, i*8:(i+1)*8] =\
                    #    cv2.addWeighted(img[j*8:(j+1)*8, i*8:(i+1)*8], 0.5,
                    #                    cell, 0.5, 0.0)
                    img[j*8:(j+1)*8, i*8:(i+1)*8] = cell

                    angle += 180/self.__bin_n

        return img

    def descript(self, img):
        rows, cols = img.shape
        numcells_h = 12
        numcells_v = 20
        cell_size_v = np.int8(rows/numcells_v)
        cell_size_h = np.int8(cols/numcells_h)
        img = cv2.resize(img, (cell_size_h * numcells_h,
                               cell_size_v * numcells_v),
                         interpolation=cv2.INTER_AREA)

        # get the gradients
        gx = cv2.filter2D(img, -1, np.mat('-1 0 1'))
        gy = cv2.filter2D(img, -1, np.mat('-1; 0.; 1.'))
        mag, ang = cv2.cartToPolar(gx, gy)  # angles 0 - 2pi
        ang[ang >= np.pi] = ang[ang >= np.pi] - np.pi

        # quantize from 0...16
        bins = np.int32(self.__bin_n * ang / (np.pi))
        # print 'bin shape', bins.shape

        # separate image into cells
        cells = np.array(np.hsplit(bins, numcells_h))
        mcells = np.array(np.hsplit(mag, numcells_h))
        bin_cells = np.empty((numcells_h, numcells_v,
                              cell_size_v, cell_size_h))
        mag_cells = np.empty((numcells_h, numcells_v,
                              cell_size_v, cell_size_h))

        for i in range(0, numcells_h):
            bin_cells[i][:][:][:] = np.array(np.vsplit(cells[:][i],
                                             numcells_v))
            mag_cells[i][:][:][:] = np.array(np.vsplit(mcells[:][i],
                                             numcells_v))

        hist = []
        self.__ahist = np.empty((numcells_h, numcells_v, self.__bin_n+1))
        for i in range(0, numcells_h-1):
            for j in range(0, numcells_v-1):
                # print i
                # 50% Overlap
                hists = np.bincount(
                    np.int32(bin_cells[i:2+i, j:2+j].ravel()),
                    weights=np.int32(mag_cells[i:2+i, j:2+j].ravel()),
                    minlength=self.__bin_n+1)
                # print 'hists', hists
                if np.amax(hists) != 0.0:
                    hists = hists / np.amax(hists) * 255
                    print 'hists', hists
                self.__ahist[i][j][:] = hists
                # make the 1D vector.
                hist.append(hists)
        # print np.array(hist).ravel().shape #20*12*16
        # store stuff for visuals (cell orientations)
        hist = np.array(hist).ravel()
        return hist
