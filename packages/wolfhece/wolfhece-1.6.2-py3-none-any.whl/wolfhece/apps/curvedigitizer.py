try:
    from ..PyTranslate import _
except:
    from wolfhece.PyTranslate import _

import wx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def main():
    '''
    Main function of curve digitizer
    '''
    plt.ion()
    ex = wx.App()
    ex.MainLoop()
    curves=[]
    # open the dialog
    file=wx.FileDialog(None,_("Select image to digitize"), 
            wildcard="jpeg image (*.jpg)|*.jpg|png image (*.png)|*.png")
    if file.ShowModal() == wx.ID_CANCEL: 
        return
    else:
        #récuparétaion du nom de fichier avec chemin d'accès
        filein =file.GetPath()
    
    # show the image    
    img = mpimg.imread(filein)
    fig, ax = plt.subplots()
    ax.imshow(img)
    ax.axis('off')  # clear x-axis and y-axis

    # get reference length in x direction
    xfactor = getReferenceLength(0)
    
    MsgBox = wx.MessageDialog(None,_('Do you want to use the same reference along Y?'),style=wx.YES_NO)
    result=MsgBox.ShowModal()
    if result == wx.ID_YES:
       yfactor=xfactor
    else:
        # get the reference length in y direction
        yfactor = getReferenceLength(1)

    print(xfactor)
    print(yfactor)
    
    origin = getOrigin()
    
    # digitize curves until stoped by the user
    reply = wx.ID_YES
    show=True
    while reply==wx.ID_YES:
        if show:
            wx.MessageBox(_("Please digitize the curve.\n" +
                "Left click: select point\n"+
                "Right click: undo\n"+
                "Middle click or Return: finish"),
                _("Digitize curve"))
            show=False

        # get the curve points
        x = plt.ginput(
            -1,
            timeout=0,
            show_clicks=True
            )
        x = np.asarray(x)
        
        ax.plot(x[:,0],x[:,1],'g','linewidth',1.5)

        # convert the curve points from pixels to coordinates
        x[:,0] = (x[:,0]-origin[0]) * xfactor
        x[:,1] = (x[:,1]-origin[1]) * yfactor

        curves.append(x)
        print(x)

        MsgBox = wx.MessageDialog(None,_("Digitize another curve?"),style=wx.YES_NO)
        reply=MsgBox.ShowModal()
        
    # write the data to a file
    # first get the filename
    validFile = False

    while not validFile:
        file=wx.FileDialog(None,_("Select file to save the data"), wildcard=_("Simple text files (.txt)|*.txt"))
        if file.ShowModal() == wx.ID_CANCEL: 
            wx.MessageBox(_("Please select a filename to save the data"),_("Filename error"))
        else:
            #récuparétaion du nom de fichier avec chemin d'accès
            fileout =file.GetPath()        
            validFile = True

    # write the data to file
    f=open(fileout,'w')
    i=0
    for loccurv in curves:
        i+=1
        f.write('line'+str(i)+'\n')
        for idx,xy in enumerate(loccurv):
            f.write('{:14.6f}\t{:14.6f}\n'.format(xy[0],xy[1]))
    f.close()

    # clear the figure
    plt.clf()

def getReferenceLength(index):
    '''
    Get the reference length in the requested direction

    USAGE: factor = getReferenceLength(index)
    index = 0 for x-direction or 1 for y-direction
    '''

    # define a 'direction' string
    direction = 'x' if index == 0 else 'y'

    # get the reference length
    reply = wx.ID_NO
    while reply==wx.ID_NO:
        wx.MessageBox(_("Use the mouse to select the reference length\n") +
            _("Click the start and the end of the reference length"),_("Select reference length"))
        coord = plt.ginput(
            2,
            timeout=0,
            show_clicks=True
            ) # capture only two points
        # ask for a valid length
        validLength = False
        while not validLength:
            dlg=wx.TextEntryDialog(None,_("Enter the reference length"))
            dlg.ShowModal()
            reflength=float(dlg.GetValue())
            dlg.Destroy()

            if isinstance(reflength, float):
                validLength = True
            else:
                wx.MessageBox(_("Please provide a valid length"),_("Error"))
        
        # calculate scaling factor
        deltaref=coord[1][index]-coord[0][index]
        factor=reflength/deltaref

        reply = wx.MessageDialog(None,"{:4.0f} pixels in {:s} direction corresponding to {:4.4f} units. Is this correct?".format(deltaref, direction, reflength),style=wx.YES_NO)
    
    return factor

def getOrigin():
    '''
    Get the Origin

    '''
    wx.MessageBox(_("Click one point"),_("Select an origin"))
    coord = plt.ginput(
        1,
        timeout=0,
        show_clicks=True
        ) # capture only one points

    msg=_('The origin is ')+ '(%d ; %d)' % (coord[0][0],coord[0][1])
    wx.MessageBox(msg)
    return (coord[0][0],coord[0][1])

if __name__ == "__main__":
    # run the main function    
    main()